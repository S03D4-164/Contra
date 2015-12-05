from ..api import ContraAPI

import requests, os, json, pickle, umsgpack

try:
    from StringIO import StringIO as BytesIO
except ImportError:
    from io import StringIO
    from io import BytesIO

import logging
from ..logger import getlogger
logger = getlogger(logging.DEBUG)
    
appdir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

def ghost_api(payload, timeout=60):
    api = ContraAPI()

    result = {}
    r = None
    try:
    #if True:
        h = {'content-type': 'application/json'}
        #r = requests.post(api.local_ghost, data=json.dumps(payload), headers=h, stream=True, timeout=timeout, verify=False)
        r = requests.post(api.docker_ghost, data=json.dumps(payload), headers=h, stream=True, timeout=timeout, verify=False)
        logger.debug(r.status_code)
        result["status_code"] = r.status_code
    except Exception as e:
        logger.error(str(e))
        result["error"] = str(e)
        return result

    #s = None
    #if r.status_code == 200:
    try:
        block_size = 1024*1024
        progress = 0
        #s = StringIO()
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
            #data = pickle.load(s, encoding="bytes")
        s.close()
        if b"error" in data:
            result["error"] = data[b"error"]
        if b"capture" in data:
            result["capture"] = data[b"capture"]
        if b"page" in data:
            result["page"] = dict([(k.decode(), v) for k,v in data[b"page"].items()])
        """
        if b"resources" in data:
            resources = []
            for r in data[b"resources"]:
                resources.append(dict([(k.decode(), v) for k,v in r.items()]))
            result["resources"] = resources
        """
        return result
    except Exception as e:
        logger.error(str(e))
        result["error"] = str(e)
        return result
