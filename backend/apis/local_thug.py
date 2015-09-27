from django.http import FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .run_thug import main as run_thug

import os, sys

import logging
from ..logger import getlogger
logger = getlogger()
	
appdir = os.path.abspath(
	os.path.join(os.path.dirname(__file__), "..")
)

@csrf_exempt
def thug_api(request):
	if request.method == "POST":
		if "content" in request.POST:
			content = request.POST["content"]
			rid = request.POST["resource"]
			output = str(rid)
			result = _thug_api(content, output)
                        if result:
                                fh = open(result, 'rb')
                                logger.debug(len(fh.read()))
                                fh.seek(0)
        			return FileResponse(fh)

	return HttpResponse(status=400)
	
def _thug_api(data, output):
	logger.debug(output)
	contentdir = appdir + "/static/artifacts/thug/" + output
	content = contentdir + "/content"
	logger.debug(contentdir)
	if not os.path.exists(contentdir):
		os.makedirs(contentdir)
	with open(content, 'wb') as fh:
		try:
			fh.write(data.encode("utf-8"))
		except Exception as e:
			logger.error(e)

	result = run_thug(content, output)

	json = appdir + "/static/artifacts/thug/" + output + "/analysis/json/analysis.json"
	if  os.path.isfile(json):
		return json

	return None
