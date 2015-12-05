from ..celery import app

from .Wappalyzer import Wappalyzer, WebPage

from ..models import *

import ast, json

import logging
from ..logger import getlogger
logger = getlogger()

@app.task
def wappalyze(rid):
    r = Resource.objects.get(pk=rid)

    url = None
    if r.url:
        url = r.url.url

    content = None
    if r.content:
        content = r.content.content

    headers = {}
    if r.headers:
        h = ast.literal_eval(r.headers)
        for k,v in h.items():
            headers[k] = v
        headers = json.dumps(headers)
    if url and content and headers:
        print("foo")
        wappalyzer = Wappalyzer.latest()
        print("bar")
        webpage = WebPage(
            url=url,
            html=content,
            headers=headers,
        )
        apps = wappalyzer.analyze(webpage)
        logger.debug(apps)
        for a in apps:
            webapp, created = Webapp.objects.get_or_create(
                name = a,
            )
            r.webapp.add(webapp)
        r.save()

    return r
        
