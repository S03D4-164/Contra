from ..celery import app
from ..forms import *
from ..models import *

from .parse_task import parse_url
from .repository import *

import requests, pickle, gzip, hashlib, chardet, base64, re
from StringIO import StringIO
from PIL import Image

@app.task
def execute_job(jid, retry=0):
	job = Job.objects.get(pk=jid)
	job.status = "Started"
	job.save()
	api="http://localhost:8000/api/local/ghost/"
	#api="http://localhost:8000/api/docker/ghost/"
	container = "3b1887ea522d113ce97d55ce05e148fa7c8b938f79ecf4a1f99ef153886a4deb"

	job.status = "Parsing Input"
	job.save()
	u = parse_url(job.query.input)

	payload = {
		'url': u.url,
		'query': job.query.id,
		'job': job.id,
		'container': container,
	}
	job.status = "Sending Request to API"
	job.save()
	r = requests.get(api, params=payload, stream=True)
	print r.status_code
	job.status = "Got Response from API: " + str(r.status_code)
	job.save()
	s = None
	if r.status_code == 200:
		block_size = 65536
		progress = 0
		s = StringIO()
		for chunk in r.iter_content(chunk_size=block_size):
			progress +=  len(chunk)
			job.status = "Reading Response: " + str(progress) + " bytes"
			job.save()
			#print progress
			s.write(chunk)
		s.seek(0)
	if s:
		#with open("tmp.pkl","wb") as t:
		#	t.write(s.getvalue())
		#try:
		if True:
			#pkl = gzip.GzipFile(mode='rb',fileobj=StringIO(r.content))
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
		print retry
		if retry < 2:
			job.status = "Retry"
			job.save()
			execute_job(jid, retry=retry)
		else:
			job.status = "Error: No Content in Response"
			job.save()

def get_savedir(uid):
	u = URL.objects.get(pk=uid)
	hostname = u.hostname.name.encode("utf-8")
	appdir = os.path.abspath(
		os.path.join(os.path.dirname(__file__), "..")
	)
	repodir = "static/repository"
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

def save_resource(data, jid, is_page=False, capture=None):
	job = Job.objects.get(pk=jid)
	u = parse_url(data["url"])
	if not u:
		return None
	
	d = get_savedir(u.id)
	print d

	c = None
	s = StringIO()
	s.write(data["content"])
	content = s.getvalue()
	cd = None
	try:
		cd = chardet.detect(content)
	except ValueError:
		cd = chardet.detect(content.encode("utf-8"))
	print cd
	decoded = content
	md5 = None
	if "encoding" in cd:
		if cd["encoding"]:
		        decoded = content.decode(cd["encoding"], errors="ignore")
			md5 = str(hashlib.md5(decoded.encode("utf-8")).hexdigest())
		else:
		        decoded = content.decode("utf-8", errors="ignore")
			md5 = str(hashlib.md5(decoded.encode("utf-8")).hexdigest())
	print md5
	s.close()
	file = d["fullpath"] + "/" + str(u.md5)
	with open(file , "wb") as f:
		f.write(data["content"])
	if os.path.isfile(file):
		d["compath"] = d["comdir"] + "/" + str(u.md5)
		commit = git_commit(d["compath"], d["repopath"])
		c = None
		d["contentpath"] = d["contentdir"] + "/" + str(u.md5)
		path = d["contentpath"].decode("utf-8")
		if commit:
			c = Content.objects.create(
				content = decoded,
				md5 = md5,
				commit = commit,
				path = path,
			)
			if c:
				print "content committed: " + path
		else:
			try:
				c = Content.objects.get(
					content = decoded,
					md5 = md5,
					#path = d["contentpath"],
				)
				if c:
					print "content already exists: " + path
			except Exception as e:
				#print e
				c = Content.objects.create(
					content = decoded,
					md5 = md5,
					path = path,
				)
				if c:
					print "content not committed but created: " + path
	rid = None
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
				print "resource already exists"
				if not job in r.job.all():
					r.job.add(job)
					r.save()
		except Exception as e:
			print(e)
			r = Resource.objects.create(
				url = u,
				http_status = data["http_status"],
				content = c,
				headers = data["headers"],
				is_page = is_page,
			)
			if not job in r.job.all():
				r.job.add(job)
				r.save()
		if r:
			rid = r.id
			if is_page and capture and not r.capture:
				cid = save_capture(capture, d, rid)
				c = Capture.objects.get(pk=cid)
				r.capture = c
				r.save()
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
	p = save_resource(data["page"], jid, is_page=True, capture=data["capture"])
	if p:
		job.status = "Page Created"
		job.save()
	else:
		job.status = "Error: No Page"
		job.save()
		
	resources = data["resources"]
	job.status = "Creating Resources"
	job.save()
	count = 0
	for resource in resources:
		count = count + 1
		job.status = "Creating Resources: " + str(count) + "/" + str(len(resources))
		job.save()
		r = save_resource(resource, jid, is_page=False)
	job.status = "Completed"
	job.save()

