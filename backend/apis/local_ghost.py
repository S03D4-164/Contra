from django.http import HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt

from .run_ghost import main as run_ghost

import os, sys, pickle, json
from multiprocessing import Process

appdir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

from ..logger import getlogger
import logging
logger = getlogger()

@csrf_exempt
def ghost_api(request):
    url = None
    savedir = appdir + "/static/artifacts/ghost" 
    option = {}
    if request.method == "POST":
        received = None
        try:
            received = json.loads(request.body)
        except Exception as e:
            logger.debug(str(e))
        if "url" in received:
            url = received["url"]
            qid = received["query"]
            jid = received["job"]
            savedir = savedir + "/" + str(qid) + "/" + str(jid)
            option["user_agent"] = received["user_agent"]
            option["wait_timeout"] = received["timeout"]
            option["headers"] = received["headers"]
            option["proxy"] = received["proxy"]
            option["method"] = received["method"]
            option["body"] = received["post_data"]
    elif request.method == "GET":
        if "url" in request.GET:
            url = request.GET["url"]
            savedir = savedir + "/get"

    if not url:
        return HttpResponse("Invalid Request", status=400)

    #result = None
    try:
        logger.debug(option)
        res = run_ghost.delay(url, savedir, option)
        result = res.get()
        logger.debug(result)
        fh = open(result, 'rb')
        logger.debug(len(fh.read()))
        fh.seek(0)
        response = FileResponse(fh)
        response['Content-Disposition'] = 'attachment; filename=ghost.pkl'
        return response
    except Exception as e:
        return HttpResponse(str(e), status=400)

