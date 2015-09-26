from django.http import HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt

from .run_ghost import main as run_ghost

import os, sys, pickle, json
from multiprocessing import Process
from StringIO import StringIO

appdir = os.path.abspath(
	os.path.join(os.path.dirname(__file__), "..")
)

from ..logger import getlogger
import logging
logger = getlogger()

@csrf_exempt
def ghost_api(request):
	logger.debug(request.body)
	received = json.loads(request.body)
	"""
	if request.method == "GET":
		if "url" in request.GET:
			target = request.GET["url"]
			qid = request.GET["query"]
			jid = request.GET["job"]
			output = str(qid) + "/" + str(jid)

			option = {}
			logger.debug(request.GET)
			option["user_agent"] = request.GET["user_agent"]
			option["wait_timeout"] = request.GET["timeout"]
			option["headers"] = request.GET["headers"]
			option["proxy"] = request.GET["proxy"]
			option["method"] = request.GET["method"]
			#option["body"] = request.GET["post_data"]
	"""
	if request.method == "POST":
		if "url" in received:
			target = received["url"]
			qid = received["query"]
			jid = received["job"]
			output = str(qid) + "/" + str(jid)

			option = {}
			option["user_agent"] = received["user_agent"]
			option["wait_timeout"] = received["timeout"]
			option["headers"] = received["headers"]
			option["proxy"] = received["proxy"]
			option["method"] = received["method"]
			#option["body"] = request.GET["post_data"]

			result = _ghost_api(target, output, option)
			if result:
				fh = open(result, 'rb')
				logger.debug(len(fh.read()))
				fh.seek(0)
				return FileResponse(fh)
	return HttpResponse(status=400)


def _ghost_api(url, output, option):
	logger.debug(option)
	p = Process(target=run_ghost, args=(url, output, option))
	p.start()
	p.join(300)
	#appdir = os.path.abspath(os.path.dirname(__file__))
	pkl = appdir + "/static/artifacts/" + output + "/ghost.pkl"
	if  os.path.isfile(pkl):
		return pkl
	return None

