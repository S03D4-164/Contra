from ..celery import app
from django.http import JsonResponse
from django.core.cache import cache

from django.utils import timezone

from ipwhois import IPWhois
import hashlib, datetime

from ..logger import getlogger
import logging
logger = getlogger()

@app.task(soft_time_limit=10)
def _whois_ip(ip):
    result = {}
    obj = None
    try:
        obj = IPWhois(ip)
        result = obj.lookup(inc_raw=True)
        logger.debug(result["nets"])
    except Exception as e:
        logger.debug(e)
        result["error"] = str(e)

    if result:
        result["reverse"] =  None
        try:
            rev = obj.net.get_host()
            logger.debug(rev)
            if rev:
                result["reverse"] = rev
        except Exception as e:
            logger.debug(e)
            result["reverse"] = str(e)

    return result

def whois_ip(request):
    result = {}

    ip = None
    if request.method == "GET":
        if "ip" in request.GET:
            ip = request.GET["ip"]

    key = "ip_"+ str(hashlib.md5(ip.encode("utf-8")).hexdigest())
    result = cache.get(key)
    if result:
        logger.debug(str(key))
        return JsonResponse(result)

    logger.debug("ip whois: " + str(ip))
    try:
        res = _whois_ip.delay(str(ip))
        result = res.get()
    except Exception as e:
        logger.debug(str(key))
        result = {"error":str(e)}

    cache.set(key, result, 60)
    return JsonResponse(result)

