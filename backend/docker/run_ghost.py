#!/usr/bin/env python

import os, sys, logging
import pickle, gzip

from ghost import Ghost

if __name__ == "__main__":
	url = None
	if sys.argv[1]:
		url = sys.argv[1].decode("utf-8")
	else:
		sys.exit("no argument.")

	output = "result"
	try:
		output = sys.argv[2]
	except:
		pass
	savedir = "/home/contra/artifacts/ghost/" +  output
	if not os.path.exists(savedir):
		os.makedirs(savedir)

	defaults = {
        	#"user_agent":None,
        	"wait_timeout":60,
        	"display":True,
        	"viewport_size":(800, 600),
        	"plugins_enabled":True,
        	"java_enabled":True,
        	"download_images":True,
        	"show_scrollbars":True,
        	#"exclude":None,
	}
	try:
		defaults = sys.argv[3]
	except:
		pass



        ghost = Ghost(
                #log_level=logging.DEBUG,
                log_level=logging.INFO,
                defaults=defaults
        )

	dump = None
	page = None
	resources = None
	#capture = None
	capture = savedir + "/capture.png"
	with ghost.start() as session:
		headers={
			"Accept-Language": "ja; q=1.0, en; q=0.5",
			"Accept": "text/html; q=1.0, text/*; q=0.8, image/gif; q=0.6, image/jpeg; q=0.6, image/*; q=0.5, */*; q=0.1",
			#"Referer":None,
		}
		page, resources = session.open(url, headers=headers)
		#capture = savedir + "/capture.png"
		session.capture_to(capture)

	result = {
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
			"seq":0,
		}

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

	dump = savedir +  "/ghost.pkl"
        with open(dump, 'wb') as d:
        	pickle.dump(result, d)

        ghost.exit()

