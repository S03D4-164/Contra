from django.http import FileResponse
from django.views.decorators.csrf import csrf_exempt

from StringIO import StringIO
import pickle

import docker
import os, sys

import logging
from ..logger import getlogger

logger = getlogger(logging.DEBUG, logging.StreamHandler())
	
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

@csrf_exempt
def thug_api(request):
	res = {}
	if request.method == "POST":
		if "content" in request.POST:
			target = request.POST["content"]
			rid = request.POST["resource"]
			#cid = request.POST["container"]
			option = {}
			#output = "thug/" + str(rid)
			output = str(rid)
			#result = run_thug(target, output, cid, option=option)
			result = run_thug(target, output, option=option)
                        if result:
                                fh = open(result, 'rb')
                                logger.debug(len(fh.read()))
                                fh.seek(0)
                                res = FileResponse(fh)
        return res


#def run_thug(content, output=None, container=None, option={}):
def run_thug(content, output=None, option={}):
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

	contentdir = appdir + "/static/artifacts/" + output
	logger.debug(contentdir)
	if not os.path.exists(contentdir):
		os.makedirs(contentdir)
	with open(contentdir + "/content", 'wb') as fh:
		try:
			fh.write(content.encode("utf-8"))
		except Exception as e:
			logger.error(e)

	command = ["/opt/thug/src/run_thug.py", "/home/contra/artifacts/" + output + "/content"]
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

	json = appdir + "/static/artifacts/thug/" + output + "/analysis/json/analysis.json"
	cli.remove_container(cid)
	if  os.path.isfile(json):
		return json
	return None


