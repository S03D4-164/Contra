from django.http import HttpResponse, FileResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..celery import app

import os, sys, json, umsgpack, docker

from .docker_container import contra_container

import logging
from ..logger import getlogger
logger = getlogger(logging.DEBUG, logging.StreamHandler())
#logger = getlogger()
    
appdir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

@csrf_exempt
def ghost_api(request):
    url = None
    output = ""
    option = {}

    if request.method == "POST":
        received = None
        try:
        #if True:
            body = request.body.decode()
            received = json.loads(body)
        except Exception as e:
            logger.debug(str(e))

        if "url" in received:
            url = received["url"]
        if "query" in received and "job" in received :
            qid = received["query"]
            jid = received["job"]
            if type(qid) is int and type(jid) is int:
                output = str(qid) + "/" + str(jid)
        if "method" in received:
            option["method"] = received["method"]
            if option["method"] == "POST" and "body" in received:
                option["body"] = received["post_data"]
        if "user_agent" in received:
            option["user_agent"] = received["user_agent"]
        if "wait_timeout" in received:
            option["wait_timeout"] = received["timeout"]
        if "headers" in received:
            option["headers"] = received["headers"]
        if "proxy" in received:
            option["proxy"] = received["proxy"]
    elif request.method == "GET":
        if "url" in request.GET:
            url = request.GET["url"]
            output = "get"

    if url:
        try:
        #if True:
            #res = run_ghost(url, output, option=option)
            res = run_ghost.delay(url, output, option=option)
            result = res.get()
            fh = open(result, 'rb')
            logger.debug(len(fh.read()))
            fh.seek(0)
            response = None
            if request.method == "POST":
                response = FileResponse(fh)
                response['Content-Disposition'] = 'attachment; filename=ghost.pkl'
            elif request.method == "GET":
                data = umsgpack.load(fh)
                if data[b"page"]:
                    page = data[b"page"]
                    response = JsonResponse({
                        "url":page[b"url"],
                        "error":page[b"error"],
                        "http_status":page[b"http_status"],
                        "headers":page[b"headers"],
                        #"content":page[b"content"].decode(),
                        "content":page[b"content"],
                    })
                else:
                    response = JsonResponse({
                        "error":data[b"resources"][0][b"error"],
                    })
            return response
        except Exception as e:
            logger.error(str(e))
            return HttpResponse(str(e), status=400)
            
    return HttpResponse("Invalid Request", status=400)

@app.task
def run_ghost(url, output=None, option={}):
    cli = docker.Client(base_url='unix://var/run/docker.sock')
    cid = contra_container(cli)
    #cid = "contra"
    logger.debug(cid)

    response = cli.start(container=cid)
    #logger.debug(response)

    command = ["./run_ghost.py", url]
    if output:
        command.append(output)
    if option:
        opt = json.dumps(option)
        command.append(opt)
        #command.append(json.dumps(option))
    logger.debug(command)
    e = cli.exec_create(
        cid,
        command,
        #user="contra",
    )
    logger.debug(e)
    result = cli.exec_start(e["Id"], stream=False)
    logger.debug(result.decode())
    cli.stop(cid, timeout=300)
    cli.remove_container(cid)

    pkl = appdir + "/static/artifacts/ghost/" + output + "/ghost.pkl"
    if os.path.isfile(pkl):
        logger.debug(pkl)
        return pkl
    return None

