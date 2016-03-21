from django.http import HttpResponse, FileResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..celery import app

import os, sys, json, umsgpack, docker

from .docker_container import contra_container

import logging
from ..logger import getlogger
#logger = getlogger(logging.DEBUG, logging.StreamHandler())
logger = getlogger()
    
appdir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

@csrf_exempt
def ghost_api(request):
    url = None
    output = ""
    option = {}

    received = None
    if request.method == "POST":
        try:
        #if True:
            body = request.body.decode()
            received = json.loads(body)
        except Exception as e:
            logger.debug(str(e))
            #return HttpResponse(str(e), status=400)
            return JsonResponse({"error":str(e)})
    elif request.method == "GET":
        received = request.GET
    if received:
        if "url" in received:
            url = received["url"]
        if "method" in received:
            option["method"] = received["method"]
            if option["method"] == "POST" and "body" in received:
                option["body"] = received["post_data"]
        if "user_agent" in received:
            option["user_agent"] = received["user_agent"]
        if "timeout" in received:
            option["wait_timeout"] = received["timeout"]
        if "headers" in received:
            option["headers"] = received["headers"]
        if "proxy" in received:
            option["proxy"] = received["proxy"]
        if "serialize" in received:
            option["serialize"] = received["serialize"]
        if "no_remove" in received:
            option["no_remove"] = True

    response = None
    if url:
        cli = docker.Client(base_url='unix://var/run/docker.sock')
        cid = contra_container(cli)
        try:
        #if True:
            if option:
                option = json.dumps(option)
            res = run_ghost.delay(cid, url, option=option)
            response = JsonResponse(res.get())
            """
            result = res.get()
            fh = open(result, 'rb')
            logger.debug(len(fh.read()))
            fh.seek(0)
            if request.method == "POST":
                if option["serialize"] == "umsgpack":
                    response = FileResponse(fh)
                    response['Content-Disposition'] = 'attachment; filename=ghost.pkl'
                else:
                    j = json.loads(fh.read())
                    response = JsonResponse(j)
            elif request.method == "GET":
                j = json.loads(fh.read())
                response = JsonResponse(j)
                data = umsgpack.load(fh)
                if data[b"page"]:
                    page = data[b"page"]
                    response = JsonResponse({
                        "url":page[b"url"],
                        "error":page[b"error"],
                        "http_status":page[b"http_status"],
                        "headers":page[b"headers"],
                        "content":page[b"content"],
                    })
                
                else:
                    response = JsonResponse({
                        "error":data[b"resources"][0][b"error"],
                    })
            """
        except Exception as e:
            logger.error(str(e))
            response = JsonResponse({
                "error":str(e),
            })
        if not "no_remove" in option:
            cli.stop(cid, timeout=300)
            cli.remove_container(cid, force=True)

    if response:
        return response

    #return HttpResponse("Invalid Request", status=400)
    return JsonResponse({"error":"Invalid Request"})

@app.task(soft_time_limit=3600)
def run_ghost(cid, url, option={}):
    cli = docker.Client(base_url='unix://var/run/docker.sock')
    #logger.debug(cid)

    response = cli.start(container=cid)

    command = ["./run_ghost.py", url, cid]
    if option:
        command.append(option)

    logger.debug(command)
    e = cli.exec_create(
        cid,
        command,
        user="contra",
    )
    logger.debug(e)
    result = cli.exec_start(e["Id"], stream=False)
    logger.debug(result.decode("utf-8"))

    #pkl = appdir + "/static/artifacts/ghost/" + cid + "/ghost.pkl"
    output = appdir + "/static/artifacts/ghost/" + cid
    if os.path.isfile(output):
        logger.debug(output)
        #return pkl
        fh = open(output, 'rb')
        #logger.debug(len(fh.read()))
        #fh.seek(0)
        j = json.loads(fh.read())
        #logger.debug(j)
        fh.close()
        return j
    return {"error":"ghost failed."}

