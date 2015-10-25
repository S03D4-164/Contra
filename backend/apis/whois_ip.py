from ..celery import app
from django.http import JsonResponse

from django.utils import timezone

from ipwhois import IPWhois
import hashlib, datetime

from ..logger import getlogger
import logging
logger = getlogger()

def whois_ip(request):
        results = {}
        ip = None
        if request.method == "GET":
                if "ip" in request.GET:
                        ip = request.GET["ip"]
        logger.debug("ip whois: " + str(ip))

	try:
		obj = IPWhois(ip)
		results = obj.lookup(inc_raw=True)
		logger.debug(results["nets"])
		results["reverse"] =  None
		rev = obj.get_host()
		logger.debug(rev)
		if rev:
			#reverse = rev[0]
			results["reverse"] = rev
	except Exception as e:
		logger.debug(e)

	return JsonResponse(results)

