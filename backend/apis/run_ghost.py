#!/usr/bin/env python

import os, pickle, gzip, json
from .ghost import Ghost

import logging
from ..logger import getlogger
logger = getlogger()

appdir = os.path.abspath(
	os.path.join(os.path.dirname(__file__), "..")
)

def main(url, output, option):
	#appdir = os.path.abspath(os.path.dirname(__file__))
	savedir = appdir + "/static/artifacts/ghost/" +  output
	if not os.path.exists(savedir):
		os.makedirs(savedir)

	defaults = {
		"wait_timeout":60,
		"display": False,
		"viewport_size": (800, 600),
		"plugins_enabled": True,
		"java_enabled": True,
	}
	if option["user_agent"]:
		defaults["user_agent"] = str(option["user_agent"])
	if option["wait_timeout"]:
		defaults["wait_timeout"] = int(option["wait_timeout"])
	logger.info(defaults)
	ghost = Ghost(
		#log_level=logging.DEBUG,
		log_level=logging.INFO,
		defaults=defaults
	)
	logger.info(dir(ghost))
	if hasattr(ghost, "xvfb"):
		logger.info(ghost.xvfb)

	dump = None
	with ghost.start() as session:
		try:
			proxy_url = option["proxy"]
			type = proxy_url.split(":")[0]
			server = proxy_url.split("/")[2]
			host = server.split(":")[0]
			port = server.split(":")[1]
			session.set_proxy(
				str(type),
				host=str(host),
				port=int(port),
			)
		except Exception as e:
			logger.error(e)

		http_method = option["method"] 
		h = option["headers"]
		headers = {}
		logger.debug(h)
		for header in h:
			headers[str(header)] = str(h[header])
		logger.debug(headers)
		body = None
		if option["body"]:
			body = str(option["body"])

		page = None
		resources = None
		error = None
		try:
			page, resources = session.open(
				url,
				method = http_method,
				headers = headers,
				body = body
			)
		except Exception as e:
			error = str(e)
		result = {
			"error":None,
			"page":{},
			"resources":[],
			"capture":None,
		}
		if error:
			result["error"] = error
		if page:
			result["page"] = {
				"url":page.url,
				"http_status":page.http_status,
				"headers":page.headers,
				"content":session.content.encode("utf-8"),
				"seq":0,
			}
			capture = savedir + "/capture.png"
			session.capture_to(capture)
			if os.path.isfile(capture):
				with open(capture, 'rb') as c:
					result["capture"] = c.read()
		if resources:
			seq = 0
			for r in resources:
				seq += 1
				dict = {
					"url":r.url,
					"http_status":r.http_status,
					"headers":r.headers,
					"content":r.content,
					"seq":seq,
				}
				result["resources"].append(dict)
				logger.debug(r.url)
		dump = savedir +  "/ghost.pkl"
		with open(dump, 'wb') as d:
			pickle.dump(result, d)
			logger.debug(dump)
	ghost.exit()
	return dump
