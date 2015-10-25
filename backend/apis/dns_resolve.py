from ..celery import app
from django.http import JsonResponse

import sys, dns.resolver, hashlib

from ..logger import getlogger
import logging
logger = getlogger()

def dns_resolve(request):
	result = {}
	query = None
	if request.method == "GET":
		if "query" in request.GET:
			query = request.GET["query"]
	logger.debug("resolve: " + str(query))
	rr = ["A", "AAAA", "CNAME", "MX", "NS", "SOA", "TXT"]
	for r in rr:
		rdata = []
        	try:
                	answer = dns.resolver.query(query, r)
	                for a in answer:
				if not str(a) in rdata:
					rdata.append(str(a))
	        except Exception as e:
        	        logger.error(str(e))
		if rdata:
			rdata.sort()
		result[r] = rdata
	return JsonResponse(result)

