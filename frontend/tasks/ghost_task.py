from ..api import ContraAPI

import requests, os, json, umsgpack
from contextlib import closing

try:
    from StringIO import StringIO as BytesIO
except ImportError:
    from io import StringIO
    from io import BytesIO

import logging
from ..logger import getlogger
#logger = getlogger(logging.DEBUG)
logger = getlogger()
    
appdir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

def read_response(r):
    block_size = 1024*1024
    progress = 0
    s = BytesIO()
    for chunk in r.iter_content(chunk_size=block_size):
        progress +=  len(chunk)
        logger.debug(progress)
        s.write(chunk)
    s.seek(0)
    result = {}
    data = {}
    if not r.status_code == 200:
        result["error"] = str(s.getvalue().decode())
    else:
        data = umsgpack.load(s)
        if not data:
            result["error"] = "ghost failed"
    s.close()
    if b"error" in data:
        result["error"] = data[b"error"]
    if b"capture" in data:
        result["capture"] = data[b"capture"]
    if b"page" in data:
        result["page"] = dict([(k.decode(), v) for k,v in data[b"page"].items()])
    if b"resources" in data:
        resources = []
        for r in data[b"resources"]:
            resources.append(dict([(k.decode(), v) for k,v in r.items()]))
        result["resources"] = resources
        if result["resources"] == []:
            result["error"] = "ghost failed"
    return result


def ghost_api(payload, timeout=60):
    api = ContraAPI()
    h = {'content-type': 'application/json'}
    d = json.dumps(payload)
    with closing(requests.post(api.docker_ghost, data=d, headers=h, stream=True, timeout=timeout, verify=False)) as r:
        try:
            logger.debug(r.status_code)
            result = read_response(r)
        except Exception as e:
            logger.error(str(e))
            result = {"error": str(e)}

    return result

    """
    s = None
    #try:
    if True:
        block_size = 1024*1024
        progress = 0
        s = BytesIO()
        for chunk in r.iter_content(chunk_size=block_size):
            progress +=  len(chunk)
            logger.debug(progress)
            s.write(chunk)
        s.seek(0)

        data = {}
        if not r.status_code == 200:
            result["error"] = str(s.getvalue().decode())
            #return result
        else:
            data = umsgpack.load(s)
            if not data:
                result["error"] = "ghost failed."
        s.close()
        if b"error" in data:
            result["error"] = data[b"error"]
        if b"capture" in data:
            result["capture"] = data[b"capture"]
        if b"page" in data:
            result["page"] = dict([(k.decode(), v) for k,v in data[b"page"].items()])
        if b"resources" in data:
            resources = []
            for r in data[b"resources"]:
                resources.append(dict([(k.decode(), v) for k,v in r.items()]))
            result["resources"] = resources
            if result["resources"] == []:
                result["error"] = "ghost failed."
        return result
    except Exception as e:
        logger.error(str(e))
        result["error"] = str(e)
        return result
    """
