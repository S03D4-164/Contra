#!/usr/bin/env python

from ThugAPI import *

import os, sys
import logging
from pprint import pprint

log = logging.getLogger("Thug")

def mycallback(data):
	import yara
	print data
	yara.CALLBACK_CONTINUE

def main(url, output=None):
	t = ThugAPI(url)
	t.set_web_tracking()
	t.disable_honeyagent()
	t.set_verbose()
	t.set_debug()
	#t.set_ast_debug()
	#t.set_http_debug()
	t.set_extensive()

	t.set_file_logging()
	t.set_json_logging()
	#t.set_mongodb_address("172.17.42.1:27017")
	t.log_init(url)
	logdir = "/home/contra/artifacts/thug"
	if output:
		logdir = "/home/contra/artifacts/thug/" + output
	t.set_log_dir(logdir)
	
	t.set_no_fetch()
	t.run_local(url)
	#t.run_remote(url)

	matches = log.URLClassifier.rules.match(url, callback=None)
	for m in matches:
		match = matches[m]
		#rule = []
		#tags = []
		for i in match:
			pprint(i)
			#rule.append(str(i["rule"]))
			rule = str(i["rule"])
			tags = []
			for tag in i["tags"]:
				if not tag in tags:
					tags.append(str(tag))
			strings = []
			for s in i["strings"]:
				d = s["data"]
				if not d in strings:
					strings.append(d)
			#log.ThugLogging.add_behavior_warn("[yara matched] %s (Rule: %s, Classification: %s)" % (strings, rule, ", ".join(tags), ))
			log.ThugLogging.add_behavior_warn(i)
		#log.ThugLogging.add_behavior_warn("[URL Classifier] URL: %s (Rule: %s, Classification: %s)" % (url, ", ".join(rule), ", ".join(tags), ))

	t.log_event()
	#log.info(log.ThugOpts.analysis_id)
	#return log.ThugOpts.analysis_id

if __name__ == '__main__':
	target = sys.argv[1]
	output = None
	if len(sys.argv) > 2:
		output = sys.argv[2]
	main(target, output)
