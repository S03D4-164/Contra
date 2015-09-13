from django.http import StreamingHttpResponse, FileResponse

from .run_ghost import main as run_ghost

import os, sys, pickle
from multiprocessing import Process
from StringIO import StringIO

appdir = os.path.abspath(
	os.path.join(os.path.dirname(__file__), "..")
)

def ghost_api(request):
	res = {}
	if request.method == "GET":
		if "url" in request.GET:
			target = request.GET["url"]
			qid = request.GET["query"]
			jid = request.GET["job"]
			output = str(qid) + "/" + str(jid)
			option = {}
			if "user_agent" in request.GET:
				option["user_agent"] = request.GET["user_agent"]
			if "timeout" in request.GET:
				option["wait_timeout"] = request.GET["timeout"]
			result = _ghost_api(target, output, option)
			print result
			if result:
				fh = open(result, 'rb')
				print len(fh.read())
				fh.seek(0)
				res = FileResponse(fh)
				#r = fh.read()
				#res = StreamingHttpResponse(r)
	print res
	return res

#def run_ghost(url, output=None, container=None):
def _ghost_api(url, output, option):
	print url
	p = Process(target=run_ghost, args=(url, output, option))
	p.start()
	p.join()
	print p
	#appdir = os.path.abspath(os.path.dirname(__file__))
	pkl = appdir + "/static/artifacts/" + output + "/ghost.pkl"
	if  os.path.isfile(pkl):
		return pkl
	return None

