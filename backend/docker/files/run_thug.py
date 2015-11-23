#!/usr/bin/env python

import os, sys

os.sys.path.append("/opt/thug/src")

from ThugAPI import *

import logging
from pprint import pprint

log = logging.getLogger("Thug")

appdir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

def mycallback(data):
    import yara
    print(data)
    yara.CALLBACK_CONTINUE

def main(url, output):
    logdir = appdir + "/artifacts/thug"

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

    t.add_urlclassifier(logdir + "/rule")
    if output:
        logdir = logdir + "/" + output
    t.set_log_dir(logdir)
    
    t.set_no_fetch()
    t.run_local(url)
    #t.run_remote(url)

    #matches = log.URLClassifier.rules.match(url, callback=None)
    matches = []
    rules = log.URLClassifier.rules
    with open(url, 'rb') as data:
        matches = rules.match(url)
    for m in matches:
        rule = str(m.rule)
        tags = []
        for tag in m.tags:
            if not tag in tags:
            tags.append(str(tag))
        strings = []
        for s in m.strings:
            d = s[2]
            if not d in strings:
            strings.append(d)
        result = {
            "strings":strings,
            "rule":rule,
            "tags":tags,
        }
        log.ThugLogging.add_yara_matched(result)
        #log.ThugLogging.add_behavior_warn("[URL Classifier] URL: %s (Rule: %s, Classification: %s)" % (url, ", ".join(rule), ", ".join(tags), ))

    t.log_event()
    print logdir
    return logdir

if __name__ == '__main__':
    target = sys.argv[1]
    if len(sys.argv) > 2:
        output = sys.argv[2]
        main(target, output)
    else:
        main(target)
