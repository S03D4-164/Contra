#!/usr/bin/env python

import os, sys, pickle, gzip, json, shutil, base64
#import umsgpack

try:
    from StringIO import StringIO as BytesIO
except ImportError:
    from io import StringIO
    from io import BytesIO

from PySide.QtCore import QByteArray, QIODevice, QBuffer

from ghost import Ghost

import logging
from logger import getlogger
logger = getlogger()

appdir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

def main(url, output, option={}):
    result = {
        "error":[],
        "page":{},
        "resources":[],
        "capture":None,
    }
    #savedir = appdir + "/artifacts/ghost/" +  output
    #dump = savedir +  "/ghost.pkl"
    savedir = os.path.join(appdir, "artifacts/ghost")
    dump = savedir +  "/" + output
    try:
    	#if os.path.exists(savedir):
        #    shutil.rmtree(savedir)
        #os.makedirs(savedir)
        with open(dump, 'wb') as d:
            #umsgpack.dump(result, d)
            json.dump(result, d)
    except Exception as e:
        logger.error(str(e))
        result["error"].append(str(e))

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
        if "timeout" in option:
            defaults["wait_timeout"] = int(option["timeout"])
        if "proxy" in option:
            proxy_url = option["proxy"]
        if "method" in option:
            http_method = option["method"] 
        if "headers" in option:
            req_headers = option["headers"]
        if "post_data" in option:
            body = str(option["post_data"])
    logger.info(defaults)

    ghost = None
    try:
        ghost = Ghost(
            #log_level=logging.DEBUG,
            log_level=logging.INFO,
            plugin_path=[ appdir + '/plugins', '/usr/lib/mozilla/plugins', ],
            defaults=defaults,
        )
    except Exception as e:
        logger.error("ghost init failed. " + str(e))
        result["error"].append(str(e))

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

        if hasattr(ghost, "xvfb"):
            logger.info(ghost.xvfb)

        page = None
        resources =None
        try:
            page, resources = session.open(
                url.decode("utf-8"),
                method = http_method,
                headers = headers,
                body = body
            )
        except Exception as e:
            logger.error(str(e))
            result["error"].append(str(e))

        #if error:
        #    result["error"] = error.spilt(".")[-1]
        if page:
            result["page"] = {
                "url":page.url,
                "http_status":page.http_status,
                "headers":page.headers,
                #"content":session.content.encode("utf-8"),
                "content":base64.b64encode(session.content.encode("utf-8")),
                "seq":0,
                #"error":page.error.encode("utf-8").split(".")[-1],
                "error":page.error.split(".")[-1],
            }
            try:
                image = session.capture()
                ba = QByteArray()
                buffer = QBuffer(ba)
                buffer.open(QIODevice.WriteOnly)
                image.save(buffer, "PNG")
                bio = BytesIO(ba)
                bio.seek(0)
                #result["capture"] = bio.read()
                result["capture"] = base64.b64encode(bio.read())
                bio.flush()
                bio.close()
                ba.clear()
                buffer.close()
            except Exception as e:
                logger.error(str(e))
                result["error"].append(str(e))
        if resources:
            seq = 0
            for r in resources:
                seq += 1
                #logger.debug(r.url)
                dict = {
                    "url":r.url,
                    "http_status":r.http_status,
                    "headers":r.headers,
                    #"content":r.content.encode("utf-8"),
                    "content":base64.b64encode(r.content),
                    "seq":seq,
                    #"error":r.error.encode("utf-8").split(".")[-1],
                    "error":r.error.split(".")[-1],
                }
                result["resources"].append(dict)
    with open(dump, 'wb') as d:
        #umsgpack.dump(result, d)
        json.dump(result, d)
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
