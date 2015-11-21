from ..api import ContraAPI

import requests, pickle, os, json

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

import logging
from ..logger import getlogger
logger = getlogger(logging.DEBUG)
    
appdir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

def ghost_api(payload, timeout=60):
    #api="http://localhost:8000/api/local/ghost/"
    #api="http://localhost:8000/api/docker/ghost/"
    api = ContraAPI()

    result = {}
    r = None
    try:
    #if True:
        h = {'content-type': 'application/json'}
        r = requests.post(api.local_ghost, data=json.dumps(payload), headers=h, stream=True, timeout=timeout, verify=False)
        logger.debug(r.status_code)
        result["status_code"] = r.status_code
    except Exception as e:
        logger.error(str(e))
        result["error"] = str(e)
        return result

    s = None
    #if r.status_code == 200:
    try:
        block_size = 1024*1024
        progress = 0
        s = StringIO()
        for chunk in r.iter_content(chunk_size=block_size):
            progress +=  len(chunk)
            logger.debug(progress)
            s.write(chunk)
        s.seek(0)
        result["data"] = pickle.load(s)
        return result
    except Exception as e:
        logger.error(str(e))
        result["error"] = str(e)
        return result
