from ..celery import app

from .Wappalyzer import Wappalyzer, WebPage

from ..models import *

import ast, json

import logging
from ..logger import getlogger
logger = getlogger()

@app.task
def wappalyze(rid):
    r = None
    url = None
    content = None
    headers = {}
    try:
        r = Resource.objects.get(pk=rid)
        if r.url:
            url = r.url.url
        if r.content:
            content = r.content.content
        if r.headers:
            h = ast.literal_eval(r.headers)
            for k,v in h.items():
                headers[k] = v
    except Exception as e:
        logger.error(str(e))
        #return None

    if url and content and headers:
        try:
            wappalyzer = Wappalyzer.latest()
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
            #return r
        except Exception as e:
            logger.error(str(e))

    return rid
