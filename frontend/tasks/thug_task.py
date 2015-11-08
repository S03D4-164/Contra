from ..celery import app
from ..forms import *
from ..models import *

from .parse_task import parse_url
from .repository import *

import requests, pickle, gzip, hashlib, chardet, base64, re

import logging
from ..logger import getlogger
logger = getlogger(logging.DEBUG)

def content_analysis(cid):
	result = {}
        #r = Resource.objects.get(pk=rid)
        #c = r.content
        c = Content.objects.get(pk=cid)
        #api="http://localhost:8000/api/docker/thug/"
        api="http://localhost:8000/api/local/thug/"

        payload = {
                'content': c.content.encode('utf-8'),
                'resource': c.id,
        }
	try:
		res = requests.post(api, data=payload)
		return res.content
	except Exception as e:
		result["error"] = str(e)
		return result
