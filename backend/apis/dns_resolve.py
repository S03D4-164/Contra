from ..celery import app
from django.http import JsonResponse
from django.core.cache import cache

import sys, dns.resolver, hashlib

from ..logger import getlogger
import logging
logger = getlogger()

@app.task(soft_time_limit=10)
def _dns_resolve(query):
    #result = {}
    result = {"query":query}
    #rr = ["A", "AAAA", "CNAME", "MX", "NS", "SOA", "TXT"]
    rr = ["A", "AAAA", "CNAME", "MX", "NS", "TXT"]
    for r in rr:
        rdata = []
        try:
            answer = dns.resolver.query(query, r)
            for a in answer:
                if not str(a) in rdata:
                    rdata.append(str(a))
        except Exception as e:
            logger.debug(str(e))
        if rdata:
            rdata.sort()
        result[r] = rdata
    return result

def dns_resolve(request):
    query = None
    if request.method == "GET":
        if "query" in request.GET:
            query = request.GET["query"]

    key = "dns_"+ str(hashlib.md5(query.encode("utf-8")).hexdigest())
    result = cache.get(key)
    if result:
        logger.debug(str(key))
        return JsonResponse(result)

    logger.debug("dns resolve: " + str(query.encode("utf-8"))) 
    try:
        res = _dns_resolve.delay(query.encode("utf-8"))
        result = res.get()
    except Exception as e:
        logger.error(str(e))
        result = {"error":str(error)}
    cache.set(key, result, 60)
    return JsonResponse(result)

