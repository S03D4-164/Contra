from django.http import HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt

import docker
import os, sys, json, pickle

import logging
from ..logger import getlogger
#logger = getlogger(logging.DEBUG, logging.StreamHandler())
logger = getlogger()
    
appdir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

def _container(cli):
    cid = None
    if cli:
        container = cli.create_container(
        image="contra:latest",
        #name="contra",
        user="contra",
        working_dir="/home/contra/files",
        #command="/usr/bin/run.sh",
        stdin_open=True,
        tty=True,
        volumes=['/home/contra/artifacts'],
        host_config=cli.create_host_config(
            binds={
                appdir + '/static/artifacts': {
                        'bind': '/home/contra/artifacts',
                        'mode': 'rw',
                    },
                }),
        )
        cid = container.get('Id')

    return cid

@csrf_exempt
def ghost_api(request):
    url = None
    output = None
    option = {}
    if request.method == "POST":
        received = None
        try:
            received = json.loads(request.body)
        except Exception as e:
            logger.debug(str(e))
        if "url" in received:
            url = received["url"]
        if "query" in received and "job" in received :
            qid = received["query"]
            jid = received["job"]
            output = str(qid) + "/" + str(jid)
        if "method" in received:
            option["method"] = received["method"]
            option["wait_timeout"] = received["timeout"]
            option["user_agent"] = received["user_agent"]
            option["headers"] = received["headers"]
            option["proxy"] = received["proxy"]
            option["body"] = received["post_data"]
    elif request.method == "GET":
        if "url" in request.GET:
            url = request.GET["url"]
            output = "get"

    if url:
        try:
        #if True:
            result = run_ghost(url, output, option=option)
            fh = open(result, 'rb')
            logger.debug(len(fh.read()))
            fh.seek(0)
            response = FileResponse(fh)
            response['Content-Disposition'] = 'attachment; filename=ghost.pkl'
            return response
        except Exception as e:
            return HttpResponse(str(e), status=400)
            
    return HttpResponse("Invalid Request", status=400)

def run_ghost(url, output=None, option={}):
    cli = docker.Client(base_url='unix://var/run/docker.sock')
    #cid = _container(cli)
    cid = "contra"
    logger.debug(cid)

    response = cli.start(container=cid)
    #logger.debug(response)

    command = ["./run_ghost.py", url]
    if output:
        command.append(output)
    if option:
        command.append(json.dumps(option))
    logger.debug(command)
    e = cli.exec_create(
        cid,
        command,
        #user="contra",
    )
    logger.debug(e)
    logger.debug(cli.exec_start(e["Id"], stream=False))
    cli.stop(cid, timeout=300)

    pkl = appdir + "/static/artifacts/ghost/" + output + "/ghost.pkl"
    logger.debug(pkl)
    #cli.remove_container(cid)
    if  os.path.isfile(pkl):
        return pkl
    return None

