from django.http import FileResponse
from django.views.decorators.csrf import csrf_exempt

from StringIO import StringIO
import pickle

import docker
import os, sys

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
		working_dir="/home/contra/artifacts",
		#command="/usr/bin/run.sh",
		stdin_open=True,
		tty=True,
		volumes=['/home/contra/artifacts'],
		host_config=docker.utils.create_host_config(
			binds={
				appdir + '/static/artifacts': {
            				'bind': '/home/contra/artifacts',
            				'mode': 'rw',
        				},
				}),
		)
		cid = container.get('Id')

	return cid


def ghost_api(request):
	res = {}
	if request.method == "GET":
		if "url" in request.GET:
			target = request.GET["url"]
			qid = request.GET["query"]
			jid = request.GET["job"]
			#cid = request.GET["container"]
			option = {}
			if "user_agent" in request.GET:
				optiion["user_agent"] =  request.GET["user_agent"]
			if "timeout" in request.GET:
				optiion["wait_timeout"] =  request.GET["user_agent"]
			#output = "ghost/" + str(qid) + "/" + str(jid)
			output = str(qid) + "/" + str(jid)
			#result = run_ghost(target, output, cid, option=option)
			result = run_ghost(target, output, option=option)
                        if result:
                                fh = open(result, 'rb')
                                logger.debug(len(fh.read()))
                                fh.seek(0)
                                res = FileResponse(fh)
        return res

def run_ghost(url, output=None, container=None, option={}):
	cli = docker.Client(base_url='unix://var/run/docker.sock')
	"""
	cid = None
	if container:
		cid = container
	else:
	"""
	cid = _container(cli)
	logger.debug(cid)

	response = cli.start(container=cid)
	logger.debug(response)

	command = ["/opt/thug/src/run_ghost.py", url]
	if output:
		command.append(output)
	if option:
		command.append(option)
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
	cli.remove_container(cid)
	if  os.path.isfile(pkl):
		return pkl
	return None

