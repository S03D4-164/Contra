from ..celery import app
from ..forms import *
from ..models import *

from .parse_task import parse_url
from .repository import *

import requests, pickle, gzip, hashlib, chardet, base64, re

try:
        from cStringIO import StringIO
except:
        from StringIO import StringIO

import logging
from ..logger import getlogger
logger = getlogger(logging.DEBUG)

def content_analysis(rid):
        r = Resource.objects.get(pk=rid)
        c = r.content
        api="http://localhost:8000/api/docker/thug/"

        payload = {
                'content': c.content.encode('utf-8'),
                'resource': r.id,
        }
	r = requests.post(api, data=payload)
	if r.content:
		return r.content
	return None
