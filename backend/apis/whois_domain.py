from ..celery import app
from django.http import JsonResponse
from django.core.cache import cache

from django.utils import timezone

import pythonwhois
import hashlib, datetime

from ..logger import getlogger
import logging
logger = getlogger()

@app.task(soft_time_limit=10)
def _whois_domain(domain):
    result = {}
    try:
        pythonwhois.net.socket.setdefaulttimeout(10)
        result = pythonwhois.get_whois(domain)
    except Exception as e:
        logger.debug("domain whois error: " + str(e))
        result["error"] = str(e)
    return result

def whois_domain(request):
    domain = None
    if request.method == "GET":
        if "domain" in request.GET:
            domain = request.GET["domain"]

    key = "domain_"+ str(hashlib.md5(domain.encode("utf-8")).hexdigest())
    result = cache.get(key)
    if result:
        logger.debug(key)
        return JsonResponse(result)

    logger.debug("domain whois: " + domain)
    try:
        res = _whois_domain.delay(domain) 
        result = res.get()
    except Exception as e:
        logger.debug(key)
        result = {"error":str(e)}

    cache.set(key, result, 60)
    return JsonResponse(result)

