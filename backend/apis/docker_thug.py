from django.http import FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from ..celery import app

import os, sys, re, docker

from .docker_container import contra_container 

import logging
from ..logger import getlogger

#logger = getlogger(logging.DEBUG, logging.StreamHandler())
logger = getlogger()
    
appdir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

@csrf_exempt
def thug_api(request):
    res = None
    if request.method == "POST":
        content = None
        id = None
        if "content" in request.POST:
            content = request.POST["content"]
        if "id" in request.POST:
            id = request.POST["id"]
        if content and id:
            cli = docker.Client(base_url='unix://var/run/docker.sock')
            cid = contra_container(cli)
            print(cid)
            try:
                if re.match("^[0-9]+$", id):
                    output = str(id)
                    res = run_thug.delay(cid, content, output)
                    result = res.get()
                    fh = open(result, 'rb')
                    logger.debug(len(fh.read()))
                    fh.seek(0)
                    res = FileResponse(fh)
            except Exception as e:
                res = HttpResponse(str(e), status=400)
            if cli and cid:
                cli.remove_container(cid)
    if res:
        return res  

    return HttpResponse("Invalid Request", status=400)

@app.task
def run_thug(cid, content, output=None):
    cli = docker.Client(base_url='unix://var/run/docker.sock')
    #cid = "contra"
    logger.debug(cid)

    response = cli.start(container=cid)
    #logger.debug(response)

    contentdir = appdir + "/static/artifacts/thug/" + output
    logger.debug(contentdir)
    if not os.path.exists(contentdir):
        os.makedirs(contentdir)
    with open(contentdir + "/content", 'wb') as fh:
        try:
            fh.write(content.encode("utf-8"))
        except Exception as e:
            logger.error(e)

    command = [
        "./run_thug.py",
        "/home/contra/artifacts/thug/" + output + "/content"
    ]
    if output:
        command.append(output)
    logger.debug(command)
    e = cli.exec_create(
        cid,
        command,
        #user="contra",
    )
    logger.debug(e)
    logger.debug(cli.exec_start(e["Id"], stream=False))
    cli.stop(cid, timeout=300)

    json = contentdir + "/analysis/json/analysis.json"
    logger.debug(json)
    #cli.remove_container(cid)
    if  os.path.isfile(json):
        return json
    return None

