from ..celery import app

from ..forms import *
from ..models import *

from .parse_task import parse_url
from .repository import *
from .wappalyze import wappalyze
from .host_inspect import host_inspect
from .ghost_task import ghost_api
from .thug_task import content_analysis
from .alert_task import job_alert

import requests, chardet, re, magic, json
import base64, hashlib, ssdeep
from PIL import Image

try:
    from StringIO import StringIO as BytesIO
except ImportError:
    from io import StringIO
    from io import BytesIO

import logging
from ..logger import getlogger
#logger = getlogger(logging.DEBUG)
logger = getlogger()
    
appdir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)


def create_payload(jid):
    job = Job.objects.get(pk=jid)
    u = parse_url(job.query.input)

    headers = {}
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
        #'query': job.query.id,
        #'job': job.id,
        'user_agent':user_agent,
        'wait_timeout': job.timeout,
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
    #if True:
        payload = create_payload(jid)
        logger.debug(json.dumps(payload))
    except Exception as e:
        #logger.error(str(e))
        job.status = "Error: " + str(e)
        job.save()
        return
    
    job.status = "Sending Request to API"
    job.save()
    res = None
    try:
    #if True:
        res = ghost_api(payload, timeout=job.timeout)
    except Exception as e:
        logger.error(str(e))
        #res = {"error":str(e)}
        job.status = "Error: " + str(e)
        job.save()
        return

    if not res:
        res = {"error":"API returns nothing"}
        job.status = "Error: " + str(res["error"])
        job.save()
        return
    elif res:
        if "error" in res:
            if res["error"]:
                job.status = "Error: " + str(res["error"])
                job.save()
                return

        if "page" in res:
            page = res["page"]
            job.status = "Creating Page"
            job.save()
            if "url" in page:
                try:
                    job = set_resource(job.id, page, is_page=True)
                except Exception as e:
                    logger.debug(str(e))
                if "capture" in res:
                    if res["capture"]:
                        if job.page:
                            try:
                                #savedir = get_savedir(job.page.url, is_page=True)
                                savedir = get_savedir(job.page.url, "capture")
                                cap = save_capture(res["capture"], savedir, job.id)
                                job.capture = cap
                                job.save()
                            except Exception as e:
                                logger.error(str(e))
        if "resources" in res:
            total = len(res["resources"])
            count = 0
            for r in res["resources"]:
                count += 1
                job.status = "Creating Resource: " + str(count) + "/" + str(total)
                job.save()

                try:
                    job = set_resource(job.id, r, is_page=False)
                except Exception as e:
                    logger.error(str(e))

        job.status = "Completed"
        job.save()

        job_diff.delay(job.id)
        job_alert.delay(job.id)

@app.task(soft_time_limit=600)
def set_resource(jid, data, is_page=False):
    job = Job.objects.get(id=jid)

    savedir = None
    content = None
    ccreated = None
    u = None
    if "url" in data:
        u = parse_url(data["url"])
    if u:
        if u.url:
            #savedir = get_savedir(u, is_page=is_page)
            savedir = None
            if is_page:
                savedir = get_savedir(u, "page")
            else:
                savedir = get_savedir(u, "resource")
            if savedir and "content" in data:
                content, ccreated = save_content(data["content"], u, savedir, is_page=is_page)

    http_status = None
    if "http_status" in data:
        http_status = data["http_status"]
    if not http_status and "error" in data:
        http_status = data["error"]

    headers = None
    if "headers" in data:
        headers = data["headers"]

    seq = None
    if "seq" in data:
        seq = data["seq"]

    resource = None
    rcreated = None
    try:
        resource, rcreated = Resource.objects.get_or_create(
            url = u,
            http_status = http_status,
            content = content,
            headers = headers,
            is_page = is_page,
            seq = seq,
        )
        if ccreated:
            #set_analysis.delay(resource.id)
            try:
                if content.length > 0 and not re.match("^image/", content.type):
                    aid = content_analysis(content.id)
                    a = Analysis.objects.get(id=aid)
                    resource.analysis = a
                    resource.save()
            except Exception as e:
                logger.error(str(e))
    except Exception as e:
        logger.error(str(e))
        try:
            #resource = Resource.objects.create(
            resource = Resource.objects.get(
                url = u,
                http_status = http_status,
                content = content,
                headers = headers,
                is_page = is_page,
                seq = seq,
            )
        except Exception as e:
            logger.error(str(e))
            return job

    hostname = None
    domain = None
    if resource:
        if resource.is_page == True:
            job.page = resource
            job.status = "Page Created"
            job.save()
        elif resource.is_page == False:
            job.resources.add(resource)
            job.save()
        if resource.url.hostname:
            hostname = resource.url.hostname
            if hostname:
                domain = resource.url.hostname.domain

    if hostname:
        r = None
        try:
            r = job.page.get(host_info__hostname=hostname)
        except:
            rs = job.resources.all().filter(
                host_info__hostname=hostname
            ).order_by("-pk")
            if rs:
                r = rs[0]
        if r:
            logger.debug("host_info already created in same job.")
            resource.host_info = r.host_info
            resource.save()
        else:
            host_info = None
            if domain:
                if domain.whitelisted:
                    logger.debug("host_inspect skipped: whitelisted domain" + str(domain.name))
                else:
                    #host_info = host_inspect(hostname.name)
                    set_hostinfo.delay(resource.id)
            else:
                #host_info = host_inspect(hostname.name)
                set_hostinfo.delay(resource.id)
            if host_info:
                resource.host_info = host_info
                resource.save()
    #wappalyze.delay(resource.id)
    resource = wappalyze(resource.id)

    return job

@app.task(soft_time_limit=60)
def set_analysis(rid):
    resource = None
    try:
        resource = Resource.objects.get(id=rid)
        content = resource.content
        if content.length > 0 and not re.match("^image/", content.type):
            logger.debug(content.url)
            aid = content_analysis(content.id)
            a = Analysis.objects.get(id=aid)
            resource.analysis = a
            resource.save()
    except Exception as e:
        logger.error(str(e))
    return resource

@app.task(soft_time_limit=600)
def set_hostinfo(rid):
    r = Resource.objects.get(id=rid)
    hostname = r.url.hostname.name
    host_info = None
    try:
        host_info = host_inspect(hostname)
        r.host_info = host_info
        r.save()
    except Exception as e:
        logger.error(str(e))
    return host_info


def get_savedir(u, d):
    hostname = None
    subdomain = None
    domain = None
    suffix = None
    if u:
        if u.hostname:
            hostname = u.hostname.name
            subdomain = u.hostname.subdomain
            if u.hostname.domain:
                domain = u.hostname.domain.name
                suffix = u.hostname.domain.suffix

    repodir = "static/repository"
    repopath = appdir + "/" + repodir
    #repository = get_repo(repopath)

    comdir = None
    """
    if is_page:
        comdir = "page/"
    else:
        comdir = "resource/"
    """
    if d:
        comdir = d + "/"
    else:
        comdir = "unknown/"
    if u.protocol == "data" and u.type:
        comdir += "data/" + u.type
    elif re.match("^[0-9a-f]*:[0-9a-f]*:[0-9a-f]+$", str(hostname)):
        comdir += "ipv6/" + hostname
    elif re.match("^([0-9]{1,3}\.){3}[0-9]{1,3}$", str(hostname)):
        comdir += "ipv4/" + hostname
    else:
        if domain:
            comdir += "domain"
            #if suffix:
            #    comdir += "/" + str(suffix)
            if domain:
                comdir += "/" + domain
            if subdomain:
                comdir += "/" + subdomain
        else:
            comdir += "hostname/" + hostname
    contentdir = repodir + "/" + comdir
    fullpath = appdir + "/" + contentdir
    if not os.path.exists(fullpath):
        try:
            os.makedirs(fullpath)
        except Exception as e:
            logger.error(str(e))
    repository = get_repo(fullpath)
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


def save_content(content, url, savedir, is_page=False):
    result = {}
    length = len(content)
    logger.debug(length)

    encoded = content
    try:
        encoded = content.encode("utf-8")
    except:
        pass
    cd = chardet.detect(encoded)
    logger.debug(cd)
    decoded = None
    md5 = None
    if "encoding" in cd:
        if cd["encoding"]:
            decoded = encoded.decode(cd["encoding"], errors="ignore")
        else:
            decoded = content.decode("utf-8", errors="ignore")
        md5 = str(hashlib.md5(encoded).hexdigest())

    d = savedir
    file = d["fullpath"] + "/" + str(url.md5)
    logger.debug(file)
    with open(file , "wb") as f:
        f.write(encoded)
    commit = None
    path = None
    type = None
    if os.path.isfile(file):
        type = magic.from_file(file, mime=True)
        logger.debug(type)
        #d["compath"] = d["comdir"] + "/" + str(url.md5)
        #commit = git_commit(d["compath"], d["repopath"])
        commit = git_commit(str(url.md5), d["fullpath"])
        d["contentpath"] = d["contentdir"] + "/" + str(url.md5)
        #path = d["contentpath"].decode("utf-8")
        path = d["contentpath"]
    c = None
    created = None
    try:
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
            c = set_hash(c.id)
    except Exception as e:
        logger.error(str(e))
        try:
            c = Content.objects.get(
                url = url,
                md5 = md5,
                path = path,
                commit = commit,
            )
        except Exception as e:
            logger.error(str(e))
    return c, created


@app.task
def set_hash(cid):
    c = Content.objects.get(id=cid)
    if c:
        if c.content:
            try:
                encoded = c.content.encode("utf-8")
                c.sha1 = str(hashlib.sha1(encoded).hexdigest())
                c.sha256 = str(hashlib.sha256(encoded).hexdigest())
                c.sha512 = str(hashlib.sha512(encoded).hexdigest())
                c.ssdeep = str(ssdeep.hash(encoded))
                c.save()
            except Exception as e:
                logger.error(str(e))
    return c


def save_capture(capture, d, jid):
    job = Job.objects.get(id=jid)
    #capdir = d["fullpath"] + "/capture/" + job.page.url.md5
    capdir = d["fullpath"] + "/" + job.page.url.md5
    if not os.path.exists(capdir):
        try:
            os.makedirs(capdir)
        except Exception as e:
            logger.error(str(e))

    filename = str(jid) + ".png"
    file = capdir + "/" + filename
    try:
        with open(file, 'wb') as f:
            f.write(capture)
    except Exception as e:
        logger.error(str(e))
        return None

    path = None
    thumb = None
    commit = None
    if os.path.isfile(file):
        try:
            #compath = d["comdir"] + "/capture/" + job.page.url.md5 + "/" + filename 
            compath = d["comdir"] + "/" +job.page.url.md5 + "/" + filename 
            #commit = git_commit(compath, d["repopath"])
            #cappath = d["contentdir"] + "/capture/" + job.page.url.md5 + "/" + filename
            cappath = d["contentdir"] + "/" + job.page.url.md5 + "/" + filename
            path = cappath
            im = Image.open(file)
            im.thumbnail((150,150))
            s = BytesIO()
            im.save(s, format="PNG")
            im.close()
            thumb = s.getvalue()
            s.close()
        except Exception as e:
            logger.error(str(e))

    try:
        c, created = Capture.objects.get_or_create(
                path = path,
                base64 = base64.b64encode(capture),
                b64thumb = base64.b64encode(thumb),
                #commit = commit,
            )
    except Exception as e:
        logger.error(str(e))
        try:
            c = Capture.objects.get(
                path = path,
                base64 = base64.b64encode(capture),
                b64thumb = base64.b64encode(thumb),
                #commit = commit,
            )
        except Exception as e:
            logger.error(str(e))

    return c


@app.task(soft_time_limit=600)
def job_diff(jid):
    job = Job.objects.get(pk=jid)
    rs = job.resources.all()

    old_jobs = Job.objects.filter(query=job.query, pk__lt=jid, status="Completed").order_by("-id")
    old_rs = None
    if old_jobs:
        old_job = old_jobs[0]
        old_rs = old_job.resources.all()

    for r in rs:
        if old_rs:
            same_urls = old_rs.filter(url=r.url).order_by("-id")
            if same_urls:
                same_url = same_urls[0]
                if r.content == same_url.content:
                    job.not_changed.add(r)
                else:
                    job.changed.add(r)
            else:
                job.new.add(r)

        else:
            job.new.add(r)
    if old_rs:
        for r in old_rs:
            if not rs.filter(url=r.url):
                job.out.add(r)
    job.save()
    return job

