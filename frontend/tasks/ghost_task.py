from ..celery import app

from django.utils import timezone

from ..forms import *
from ..models import *

from .parse_task import parse_url
from .repository import *
from .whois_domain import whois_domain
from .whois_ip import whois_ip
from .dns_resolve import dns_resolve
from .wappalyze import wappalyze
from .host_inspect import host_inspect

import requests, pickle, hashlib, chardet, base64, re, magic, json, datetime
from PIL import Image

try:
	from cStringIO import StringIO
except:
	from StringIO import StringIO

import logging
from ..logger import getlogger
logger = getlogger(logging.DEBUG)
	
appdir = os.path.abspath(
	os.path.join(os.path.dirname(__file__), "..")
)


def create_headers(jid):
	job = Job.objects.get(pk=jid)
	headers = {
		"Accept-Language":"ja; q=1.0, en; q=0.5",
		"Accept":"text/html; q=1.0, text/*; q=0.8, image/gif; q=0.6, image/jpeg; q=0.6, image/*; q=0.5, */*; q=0.1",
	}
	if job.referer:
		headers['Referer'] = job.referer
	if job.additional_headers:
		lines = job.additional_headers.split("\n")
		for line in lines:
			l = line.split(":")
			if len(l) >= 2:
				key = l[0]
				value= ":".join(l[1:])
				headers[str(key)] = str(value)
	return headers


@app.task
def execute_job(jid, retry=0):
	api="http://localhost:8000/api/local/ghost/"
	#api="http://localhost:8000/api/docker/ghost/"

	job = Job.objects.get(pk=jid)

	job.status = "Parsing Input"
	job.save()
	u = parse_url(job.query.input)
	#logger.debug(u)

	headers = create_headers(jid)

	user_agent = ""
	if job.user_agent:
		user_agent = job.user_agent.strings
	proxy = ""
	if job.proxy:
		proxy = job.proxy.url
	payload = {
		'url': u.url,
		'query': job.query.id,
		'job': job.id,
		'user_agent':user_agent,
		'timeout': job.timeout,
		'proxy':proxy,
		'headers':headers,
		'method': job.method,
		'post_data':job.post_data,
	}
	logger.debug(json.dumps(payload))
	job.status = "Sending Request to API"
	job.save()

	r = None
	try:
		h = {'content-type': 'application/json'}
		r = requests.post(api, data=json.dumps(payload), headers=h, stream=True, timeout=job.timeout, verify=False)
		logger.debug(r.status_code)
		job.status = "Got Response from API: " + str(r.status_code)
		job.save()
	except Exception as e:
		logger.error(e)
		job.status = "Error: " + str(e)
		job.save()
		return

	s = None
	if r.status_code == 200:
		block_size = 1024*1024
		progress = 0
		s = StringIO()
		for chunk in r.iter_content(chunk_size=block_size):
			progress +=  len(chunk)
			job.status = "Reading Response: " + str(progress) + " bytes"
			job.save()
			logger.debug(progress)
			s.write(chunk)
		s.seek(0)
	if s:
		#try:
		if True:
			data = pickle.load(s)
			job.status = "Parsing Response Content"
			job.save()
			parse_data(data, jid)
		"""
		except Exception as e:
			job.status = "Error: " + str(e)
			job.save()
		"""
	else:
		retry = retry + 1
		logger.debug("Retrying: " + str(retry) + " times")
		if retry < 2:
			job.status = "Retry"
			job.save()
			execute_job(jid, retry=retry)
		else:
			job.status = "Error: No Content in Response"
			job.save()


def get_savedir(uid, is_page=False):
	u = URL.objects.get(pk=uid)
	hostname = u.hostname.name.encode("utf-8")
	#repodir = "static/repository"
	repodir = None
	if is_page:
		repodir = "static/repository/page"
	else:
		repodir = "static/repository/resource"
	repopath = appdir + "/" + repodir
	repository = get_repo(repopath)
	comdir = None
	if u.type and u.data:
		comdir = "data/" + str(u.type)
	elif re.match("^[0-9a-f]*:[0-9a-f]*:[0-9a-f]+$", hostname):
		comdir = "ipv6/" + str(hostname)
	elif re.match("^([0-9]{1,3}\.){3}[0-9]{1,3}$", hostname):
		comdir = "ipv4/" + str(hostname)
	else:
		comdir = "domain/" + str(hostname)
	contentdir = repodir + "/" + comdir
	fullpath = appdir + "/" + contentdir
	if not os.path.exists(fullpath):
		os.makedirs(fullpath)
	d = {
		"appdir": appdir,
		"repodir": repodir,
		"repopath": repopath,
		"comdir": comdir,
		"contentdir": contentdir,
		"fullpath": fullpath,
	}
	return d


@app.task
def save_resource(data, jid, is_page=False, capture=None):
	job = Job.objects.get(pk=jid)

	u = parse_url(data["url"])
	if not u:
		return None

	d = get_savedir(u.id, is_page=is_page)
	#logger.debug(d)

	s = StringIO()
	s.write(data["content"])
	content = s.getvalue()
	type = magic.from_buffer(content, mime=True)
	length = len(content)

	cd = None
	try:
		cd = chardet.detect(content)
	except ValueError:
		cd = chardet.detect(content)
	logger.debug(cd)
	decoded = content
	md5 = None
	if "encoding" in cd:
		if cd["encoding"]:
		        decoded = content.decode(cd["encoding"], errors="ignore")
			md5 = str(hashlib.md5(decoded.encode("utf-8")).hexdigest())
		else:
		        decoded = content.decode("utf-8", errors="ignore")
			md5 = str(hashlib.md5(decoded.encode("utf-8")).hexdigest())
	#logger.debug(md5)
	s.close()

	file = d["fullpath"] + "/" + str(u.md5)
	with open(file , "wb") as f:
		f.write(data["content"])
	c = None
	if os.path.isfile(file):
		d["compath"] = d["comdir"] + "/" + str(u.md5)
		commit = git_commit(d["compath"], d["repopath"])
		d["contentpath"] = d["contentdir"] + "/" + str(u.md5)
		path = d["contentpath"].decode("utf-8")
		if commit:
			try:
				c = Content.objects.get(
					content = decoded,
					md5 = md5,
					commit = commit,
					path = path,
					type = type,
					length = length,
				)
				logger.debug("content already exists: " + path)
			except Exception as e:
				logger.error(str(e))
				c = Content.objects.create(
					content = decoded,
					md5 = md5,
					commit = commit,
					path = path,
					type = type,
					length = length,
				)
				logger.info("content created: " + path)
	rid = None
	jr = None
	if u and c:
		r = None
		try:
			r = Resource.objects.get(
				url = u,
				http_status = data["http_status"],
				content = c,
				#headers = data["headers"],
				is_page = is_page,
			)
			if r:
				logger.info("resource already exists")
				jr, created = Job_Resource.objects.get_or_create(
					job = job,
					resource = r,
				)
				jrs = Job_Resource_Seq.objects.create(
					job_resource = jr,
					seq = data["seq"],
				)
		except Exception as e:
			logger.error("get resource failed: " + str(e))
			r = Resource.objects.create(
				url = u,
				http_status = data["http_status"],
				content = c,
				headers = data["headers"],
				is_page = is_page,
			)
			jr, created = Job_Resource.objects.get_or_create(
				job = job,
				resource = r,
			)
			jrs = Job_Resource_Seq.objects.create(
				job_resource = jr,
				seq = data["seq"],
			)
		if r:
			rid = r.id
			if is_page and capture and not r.capture:
				cid = save_capture(capture, d, rid)
				c = Capture.objects.get(pk=cid)
				r.capture = c
				r.save()
			wappalyze(rid)

	if jr:
		if not jr.host_info:
			if jr.resource.url.hostname.domain.whitelisted:
				logger.info("whitelisted domain: " + str(jr.resource.url.hostname.domain.name))
			else:
				jrs = Job_Resource.objects.filter(host_info__hostname=jr.resource.url.hostname).order_by("-pk")
				host_info = None
				if jrs:
					logger.info("host info already created in same job: " + str(jr.resource.url.hostname.name))
					host_info = jrs[0].host_info
				else:
				#set_host_info(jr.id)
					host_info = host_inspect(jr.resource.url.hostname.name)
				if host_info:
					jr.host_info = host_info
					jr.save()

	return rid


def save_capture(capture, d, rid):
	capdir = d["fullpath"] + "/capture"
	if not os.path.exists(capdir):
		os.makedirs(capdir)
	#cappath = d["contentpath"] + ".png"
	#file = d["appdir"] + "/" + cappath
	filename = str(rid) + ".png"
	file = capdir + "/" + filename
	with open(file, 'wb') as f:
		f.write(capture)

	cid = None
	if os.path.isfile(file):
		#commit = git_commit(d["compath"] + ".png", d["repopath"])
		compath = d["comdir"] + "/capture/" + filename 
		commit = git_commit(compath, d["repopath"])
		#path = cappath.decode("utf-8")
		cappath = d["contentdir"] + "/capture/" + filename
		path = cappath.decode("utf-8")
		im = Image.open(file)
		im.thumbnail((150,150))
		s = StringIO()
		im.save(s, format="PNG")
		thumb = s.getvalue()
		s.close()
		if commit:
			c, created = Capture.objects.get_or_create(
				path = path,
				commit = commit,
				#md5 = hashlib.md5(capture).hexdigest(),
				base64 = base64.b64encode(capture),
				b64thumb = base64.b64encode(thumb),
			)
			cid = c.id
		else:
			try:
				c = Capture.objects.get(
					path = path,
					#md5 = hashlib.md5(capture).hexdigest(),
					base64 = base64.b64encode(capture),
				)
			except:
				c, created = Capture.objects.get_or_create(
					path = path,
					#md5 = hashlib.md5(capture).hexdigest(),
					base64 = base64.b64encode(capture),
					b64thumb = base64.b64encode(thumb),
				)
			cid = c.id
	return cid


def parse_data(data, jid):
	job = Job.objects.get(pk=jid)

	job.status = "Creating Page"
	job.save()
	p = None
	if data["page"]:
		p = save_resource(data["page"], jid, is_page=True, capture=data["capture"])
	if p:
		job.status = "Page Created"
		job.save()
	else:
		job.status = "No Page"
		job.save()
		
	resources = data["resources"]
	job.status = "Creating Resources"
	job.save()
	count = 0
	for resource in resources:
		count = count + 1
		job.status = "Creating Resources: " + str(count) + "/" + str(len(resources))
		job.save()
		u = parse_url(resource["url"])
		r = save_resource(resource, jid, is_page=False)

	if count == 0:
		job.status = "Completed: No resources"
	else:
		job.status = "Completed"
		job_diff(job.id)
	job.save()

@app.task
def job_diff(jid):
	job = Job.objects.get(pk=jid)
	jrs = Job_Resource.objects.filter(job=job)

	old_jobs = Job.objects.filter(query=job.query, pk__lt=jid, status="Completed").order_by("-id")
	old_jrs = None
	if old_jobs:
		old_job = old_jobs[0]
		old_jrs = Job_Resource.objects.filter(job=old_job)

	for jr in jrs:
		r = jr.resource
		if old_jrs:
			same_urls = old_jrs.filter(resource__url=r.url).order_by("-id")
			if same_urls:
				same_url = same_urls[0]
				if r.content == same_url.resource.content:
					job.not_changed.add(r)
				else:
					job.changed.add(r)
			else:
				job.new.add(r)

		else:
			job.new.add(r)
	if old_jrs:
		for jr in old_jrs:
			r = jr.resource
			if not jrs.filter(resource__url=r.url):
				job.out.add(r)
	job.save()
