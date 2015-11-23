#!/usr/bin/env python

import os, sys, pickle, gzip, json
from ghost import Ghost

import logging
from logger import getlogger
logger = getlogger()

appdir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

def main(url, output, option={}):
    savedir = appdir + "/artifacts/ghost/" +  output
    if not os.path.exists(savedir):
        try:
            os.makedirs(savedir)
        except Exception as e:
            logger.error(str(e))

    defaults = {
        "wait_timeout":60,
        "display": False,
        "viewport_size": (800, 600),
        "plugins_enabled": True,
        "java_enabled": True,
    }
    proxy_url = None
    http_method = "GET"
    req_headers = None
    body = None
    if option:
        if "user_agent" in option:
            defaults["user_agent"] = str(option["user_agent"])
        if "wait_timeout" in option:
            defaults["wait_timeout"] = int(option["wait_timeout"])
        if "proxy" in option:
            proxy_url = option["proxy"]
        if "method" in option:
            http_method = option["method"] 
        if "headers" in option:
            req_headers = option["headers"]
        if "body" in option:
            body = str(option["body"])
    logger.info(defaults)
    ghost = Ghost(
        log_level=logging.DEBUG,
        #log_level=logging.INFO,
        plugin_path=[ appdir + '/plugins', '/usr/lib/mozilla/plugins', ],
        defaults=defaults,
    )

    dump = None
    with ghost.start() as session:
        if proxy_url:
            try:
                type = proxy_url.split(":")[0]
                server = proxy_url.split("/")[2]
                host = server.split(":")[0]
                port = server.split(":")[1]
                session.set_proxy(str(type),host=str(host),port=int(port),)
            except Exception as e:
                logger.debug(e)

        headers = {}
        if req_headers:
            logger.debug(req_headers)
            for h in req_headers:
                headers[str(h)] = str(req_headers[h])
            logger.debug(headers)

        page = None
        resources = None
        error = None
        if hasattr(ghost, "xvfb"):
            logger.info(ghost.xvfb)
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
            #"error":None,
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
                "error":page.error,
            }
            capture = savedir + "/capture.png"
            try:
                session.capture_to(capture)
                if os.path.isfile(capture):
                    with open(capture, 'rb') as c:
                        result["capture"] = c.read()
            except Exception as e:
                logger.error(str(e))
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
                    "error":r.error,
                }
                result["resources"].append(dict)
                #logger.debug(r.url)
        dump = savedir +  "/ghost.pkl"
        print dump
        with open(dump, 'wb') as d:
            pickle.dump(result, d)
            logger.debug(dump)
    ghost.exit()
    return dump


if __name__ == '__main__':
    target = sys.argv[1]
    output = sys.argv[2]
    if len(sys.argv) > 3:
        option = json.loads(sys.argv[3])
        main(target, output, option=option)
    else:
        main(target, output)

