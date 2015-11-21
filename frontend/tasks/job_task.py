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


def create_payload(jid):
    job = Job.objects.get(pk=jid)
    u = parse_url(job.query.input)

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

    return payload


@app.task(time_limit=3600)
def execute_job(jid):
    job = Job.objects.get(pk=jid)

    job.status = "Creating Request Payload"
    job.save()
    try:
        payload = create_payload(jid)
        logger.debug(json.dumps(payload))
    except Exception as e:
        logger.error(str(e))
        job.status = "Error: " + str(e)
        job.save()
        return
    
    job.status = "Sending Request to API"
    job.save()
    result = None
    try:
        result = ghost_api(payload, timeout=job.timeout)
    except Exception as e:
        logger.error(str(e))
        result = {"Error":str(e)}

    if "error" in result:
        if result["error"]:
            job.status = "Error: " + str(result["error"])
            job.save()
            return

    if "data" in result:
        data = result["data"]
        if "page" in data:
            job.status = "Creating Page"
            job.save()
            if data["page"]:
                job = set_resource(job.id, data["page"], is_page=True)

                savedir = get_savedir(data["page"]["url"], is_page=True)
                cap = save_capture(data["capture"], savedir, job.id)
                job.capture = cap
                job.save()

        if "resources" in data:
            total = len(data["resources"])
            count = 0
            for r in data["resources"]:
                count += 1
                job.status = "Creating Resource: " + str(count) + "/" + str(total)
                job.save()
                
                #set_resource.delay(job.id, r, is_page=False)
                set_resource(job.id, r, is_page=False)

        job.status = "Completed"
        job.save()

@app.task
def set_resource(jid, data, is_page=False):
    job = Job.objects.get(id=jid)

    url = None
    content = None
    http_status = None
    try:
        url = parse_url(data["url"])
        http_status = data["http_status"]
        #if http_status:
        savedir = get_savedir(data["url"], is_page=is_page)
        content = save_content(data, savedir, is_page=is_page)
        #elif not http_status:
        #    http_status = data["error"]
    except Exception as e:
        logger.error(str(e))
        #return None

    resource = None
    created = None
    try:
        with transaction.atomic():
            resource, created = Resource.objects.get_or_create(
            #resource = Resource.objects.create(
                url = url,
                http_status = http_status,
                content = content,
                headers = data["headers"],
                is_page = is_page,
                seq = data["seq"],
            )

    except Exception as e:
        logger.error(str(e))
        try:
            resource = Resource.objects.create(
                url = url,
                http_status = http_status,
                content = content,
                headers = data["headers"],
                is_page = is_page,
                seq = data["seq"],
            )
        except Exception as e:
            logger.error(str(e))
            return None

    if resource.is_page == True:
        job.page = resource
        job.status = "Page Created."
        job.save()
    elif resource.is_page == False:
        job.resources.add(resource)
        job.save()

    if resource.url.hostname:
        r = job.resources.all().filter(
            host_info__hostname=resource.url.hostname
        ).order_by("-pk")
        if r:
            logger.debug("host_info already created in same job.")
            resource.host_info = r[0].host_info
            resource.save()
        else:
            set_hostinfo(resource.id)
            #set_hostinfo.delay(resource.id)

    #wappalyze.delay(resource.id)
    resource = wappalyze(resource.id)

    return job

@app.task
def set_hostinfo(rid):
    r = Resource.objects.get(id=rid)
    hostname = r.url.hostname.name
    host_info = host_inspect(hostname)
    r.host_info = host_info
    r.host_info.save()
    r.save()
    return host_info

def get_savedir(url, is_page=False):
    u = parse_url(url)
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
        bcomdir = "data/" + str(u.type)
    elif re.match("^[0-9a-f]*:[0-9a-f]*:[0-9a-f]+$", hostname):
        comdir = "ipv6/" + str(hostname)
    elif re.match("^([0-9]{1,3}\.){3}[0-9]{1,3}$", hostname):
        comdir = "ipv4/" + str(hostname)
    else:
        comdir = "domain/" + str(hostname)
    contentdir = repodir + "/" + comdir
    fullpath = appdir + "/" + contentdir
    if not os.path.exists(fullpath):
        try:
            os.makedirs(fullpath)
        except Exception as e:
            logger.error(str(e))
    d = {
        "appdir": appdir,
        "repodir": repodir,
        "repopath": repopath,
        "comdir": comdir,
        "contentdir": contentdir,
        "fullpath": fullpath,
    }
    logger.debug(d)
    return d


def save_content(data, savedir, is_page=False):
    result = {}
    url = parse_url(data["url"])

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
        else:
            decoded = content.decode("utf-8", errors="ignore")
        if decoded:
            md5 = str(hashlib.md5(decoded.encode("utf-8")).hexdigest())
    s.close()

    d = savedir
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
                url = url,
            )
            if c:
                #set_hash.delay(c.id)
                c = set_hash(c.id)
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
                url = url,
            )
        except Exception as e:
            logger.error(str(e))
    return c


@app.task
def set_hash(cid):
    c = Content.objects.get(id=cid)
    decoded = c.content
    c.sha1 = str(hashlib.sha1(decoded.encode("utf-8")).hexdigest())
    c.sha256 = str(hashlib.sha256(decoded.encode("utf-8")).hexdigest())
    c.sha512 = str(hashlib.sha512(decoded.encode("utf-8")).hexdigest())
    c.save()
    return c


def save_capture(capture, d, jid):
    job = Job.objects.get(id=jid)
    capdir = d["fullpath"] + "/capture/" + job.page.url.md5
    if not os.path.exists(capdir):
        try:
            os.makedirs(capdir)
        except Exception as e:
            logger.error(str(e))

    filename = str(jid) + ".png"
    file = capdir + "/" + filename
    with open(file, 'wb') as f:
        f.write(capture)

    commit = None
    if os.path.isfile(file):
    #if True:
        compath = d["comdir"] + "/capture/" + job.page.url.md5 + "/" + filename 
        #commit = git_commit(compath, d["repopath"])
        cappath = d["contentdir"] + "/capture/" + job.page.url.md5 + "/" + filename
        path = cappath.decode("utf-8")
        im = Image.open(file)
        im.thumbnail((150,150))
        s = StringIO()
        im.save(s, format="PNG")
        thumb = s.getvalue()
        s.close()

    c = None
    try:
        with transaction.atomic():
            c, created = Capture.objects.get_or_create(
                path = path,
                #commit = commit,
                base64 = base64.b64encode(capture),
                b64thumb = base64.b64encode(thumb),
            )
            #cid = c.id
    except Exception as e:
        logger.error(str(e))
        try:
            c = Capture.objects.get(
                path = path,
                #commit = commit,
                base64 = base64.b64encode(capture),
                b64thumb = base64.b64encode(thumb),
            )
            #cid = c.id
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
