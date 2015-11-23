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
            try:
                data = request.POST["content"]
                id = request.POST["id"]
                savedir = appdir + "/static/artifacts/thug/" + str(id)
                if not os.path.exists(savedir):
                    os.makedirs(savedir)

                content = savedir + "/content"
                with open(content, 'wb') as fh:
                    fh.write(data.encode("utf-8"))
                result = run_thug(content, savedir)
                if result:
                    json = savedir + "/analysis/json/analysis.json"
                    if os.path.isfile(json):
                        fh = open(json, 'rb')
                        logger.debug(len(fh.read()))
                        fh.seek(0)
                        return FileResponse(fh)
            except Exception as e:
                logger.error(e)
                return HttpResponse(str(e), status=400)

    return HttpResponse("Invalid Request", status=400)

