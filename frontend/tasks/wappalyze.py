from ..celery import app

from Wappalyzer import Wappalyzer, WebPage

from ..models import *

import ast

import logging
from ..logger import getlogger
logger = getlogger()

@app.task
def wappalyze(rid):
	r = Resource.objects.get(pk=rid)

	wappalyzer = Wappalyzer.latest()
	webpage = WebPage(
		url=r.url.url,
		html=r.content.content,
		headers=ast.literal_eval(r.headers),
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
		
