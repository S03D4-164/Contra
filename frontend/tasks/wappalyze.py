from ..celery import app

from Wappalyzer import Wappalyzer, WebPage

from ..models import *

import ast

import logging
from ..logger import getlogger
logger = getlogger()

@app.task
def wappalyze(res_id):
	r = Resource_Info.objects.get(pk=res_id)

	wappalyzer = Wappalyzer.latest()
	webpage = WebPage(
		url=r.resource.url.url,
		html=r.resource.content.content,
		headers=ast.literal_eval(r.headers),
		#url=url,
		#html=content,
		#headers=ast.literal_eval(headers),
	)
	apps = wappalyzer.analyze(webpage)
	logger.debug(apps)
	for a in apps:
		webapp, created = Webapp.objects.get_or_create(
			name = a,
		)
		r.webapp.add(webapp)
	r.save()
		
