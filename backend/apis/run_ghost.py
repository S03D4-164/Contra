#!/usr/bin/env python

import os, pickle, gzip
from ghost import Ghost

def main(url, output, defaults={}):
	appdir = os.path.abspath(os.path.dirname(__file__))
	savedir = appdir + "/static/artifacts/" +  output
	if not os.path.exists(savedir):
		os.makedirs(savedir)
	#ghost = Ghost()
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
			capture = savedir + "/capture.png"
			session.capture_to(capture)
			if os.path.isfile(capture):
				with open(capture, 'rb') as c:
					result["capture"] = c.read()
		if resources:
			for r in resources:
				dict = {
					"url":r.url,
					"http_status":r.http_status,
					"headers":r.headers,
					"content":r.content,
				}
				result["resources"].append(dict)

		dump = savedir +  "/ghost.pkl.gz"
		with gzip.open(dump, 'wb') as d:
			pickle.dump(result, d)
			return
