#!/usr/bin/env python

import os, pickle, gzip
from ghost import Ghost

appdir = os.path.abspath(
	os.path.join(os.path.dirname(__file__), "..")
)

def main(url, output, defaults={}):
	#appdir = os.path.abspath(os.path.dirname(__file__))
	savedir = appdir + "/static/artifacts/" +  output
	if not os.path.exists(savedir):
		os.makedirs(savedir)
	#ghost = Ghost()
	#defaults["display"] = True
	#defaults["viewport_size"] = (640, 480)
	ghost = Ghost(defaults=defaults)
	with ghost.start() as session:
		page, resources = session.open(url)
		result = {
			"status":"Start",
			"page":{},
			"resources":[],
			"capture":None,
		}
		if page:
			result["page"] = {
				"url":page.url,
				"http_status":page.http_status,
				"headers":page.headers,
				"content":page.content,
			}
			print page.url
			capture = savedir + "/capture.png"
			session.capture_to(capture)
			if os.path.isfile(capture):
				with open(capture, 'rb') as c:
					result["capture"] = c.read()
					print capture
		if resources:
			for r in resources:
				dict = {
					"url":r.url,
					"http_status":r.http_status,
					"headers":r.headers,
					"content":r.content,
				}
				result["resources"].append(dict)
				print r.url
		dump = savedir +  "/ghost.pkl"
		print dump
		with open(dump, 'wb') as d:
			pickle.dump(result, d)
		"""
		dump = savedir +  "/ghost.pkl.gz"
		with gzip.open(dump, 'wb') as d:
			pickle.dump(result, d)
		"""
		return dump
