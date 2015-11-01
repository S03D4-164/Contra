from ..celery import app

from django.db import transaction
from django.utils import timezone

from ..forms import *
from ..models import *

from .parse_task import parse_url
from .repository import *
from .wappalyze import wappalyze
from .host_inspect import host_inspect
from .ghost_task import ghost_api

import requests, hashlib, chardet, base64, re, magic, json, datetime
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
def execute_job(jid):
	job = Job.objects.get(pk=jid)

	job.status = "Parsing Input"
	job.save()
	u = parse_url(job.query.input)

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
	result = ghost_api(payload, timeout=job.timeout)
	if "error" in result:
		job.status = result["error"]
		job.save()
	elif "data" in result:
		data = result["data"]
		if "page" in data:
			job.status = "Creating Page"
			job.save()
			try:
			#if data["page"]:
				page, savedir = save_resource(data["page"], is_page=True)
				cap = save_capture(data["capture"], savedir, job.id)
				job.capture = cap
				job.save()
				seq = data["page"]["seq"]
				hostname = page.url.hostname.name
				host_info = host_inspect(hostname)
				info = Resource_Info.objects.create(
					resource = page,
					seq = seq,
					host_info = host_info,
				)
				job.page = info
				job.status = "Page Created"
				job.save()
			except Exception as e:
				job.status = str(e)
				job.save()
				
		if "resources" in data:
			total = len(data["resources"])
			count = 0
			for r in data["resources"]:
				count += 1
				job.status = "Creating Resource: " + str(count) + "/" + str(total)
				resource, savedir = save_resource(r)
				seq = r["seq"]
				hostname = resource.url.hostname.name
				host_info = host_inspect(hostname)
				info = Resource_Info.objects.create(
					resource = resource,
					seq = seq,
					host_info = host_info,
				)
				job.resources.add(info)
				job.save()
		job.status = "Completed"
		job.save()


def get_savedir(uid, is_page=False):
	u = URL.objects.get(pk=uid)
	hostname = u.hostname.name.encode("utf-8")

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


def save_resource(data, is_page=False):
	result = {}
	url = parse_url(data["url"])

	d = get_savedir(url.id, is_page=is_page)

	s = StringIO()
	s.write(data["content"])
	content = s.getvalue()
	type = magic.from_buffer(content, mime=True)
	length = len(content)

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
	s.close()

	file = d["fullpath"] + "/" + str(url.md5)
	with open(file , "wb") as f:
		f.write(data["content"])
	commit = None
	path = None
	if os.path.isfile(file):
		d["compath"] = d["comdir"] + "/" + str(url.md5)
		commit = git_commit(d["compath"], d["repopath"])
		d["contentpath"] = d["contentdir"] + "/" + str(url.md5)
		path = d["contentpath"].decode("utf-8")

	c = None
	try:
		with transaction.atomic():
			c, created = Content.objects.get_or_create(
				content = decoded,
				md5 = md5,
				commit = commit,
				path = path,
				type = type,
				length = length,
			)
	except Exception as e:
		logger.error(str(e))
		try:
			c = Content.objects.get(
				content = decoded,
				md5 = md5,
				commit = commit,
				path = path,
				type = type,
				length = length,
			)
		except Exception as e:
			logger.error(str(e))

	r = None
	try:
		with transaction.atomic():
			r, created = Resource.objects.get_or_create(
				url = url,
				http_status = data["http_status"],
				content = c,
				#headers = data["headers"],
				is_page = is_page,
			)
	except Exception as e:
		logger.error(str(e))
		try:
			r = Resource.objects.get(
				url = url,
				http_status = data["http_status"],
				content = c,
				#headers = data["headers"],
				is_page = is_page,
			)
		except Exception as e:
			logger.error(str(e))

	if r:
		if not r.headers:
			r.headers = data["headers"]
			r.save()
		wappalyze.delay(r.id)

	return r, d


def save_capture(capture, d, id):
	capdir = d["fullpath"] + "/capture"
	if not os.path.exists(capdir):
		os.makedirs(capdir)
	filename = str(id) + ".png"
	file = capdir + "/" + filename
	with open(file, 'wb') as f:
		f.write(capture)

	commit = None
	if os.path.isfile(file):
		compath = d["comdir"] + "/capture/" + filename 
		commit = git_commit(compath, d["repopath"])
		cappath = d["contentdir"] + "/capture/" + filename
		path = cappath.decode("utf-8")
		im = Image.open(file)
		im.thumbnail((150,150))
		s = StringIO()
		im.save(s, format="PNG")
		thumb = s.getvalue()
		s.close()

	cid = None
	try:
		with transaction.atomic():
			c, created = Capture.objects.get_or_create(
				path = path,
				commit = commit,
				base64 = base64.b64encode(capture),
				b64thumb = base64.b64encode(thumb),
			)
			cid = c.id
	except Exception as e:
		logger.error(str(e))
		try:
			c = Capture.objects.get(
				path = path,
				commit = commit,
				base64 = base64.b64encode(capture),
				b64thumb = base64.b64encode(thumb),
			)
			cid = c.id
		except Exception as e:
			logger.error(str(e))
	return c


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
