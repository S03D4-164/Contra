from ..celery import app
from django.http import JsonResponse

from django.utils import timezone

import pythonwhois
import hashlib, datetime

from ..logger import getlogger
import logging
logger = getlogger()

def whois_domain(request):
	result = {}
	domain = None
        if request.method == "GET":
                if "domain" in request.GET:
                        domain = request.GET["domain"]
        logger.debug("domain whois: " + str(domain))

	cdate = None
	udate = None
	try:
		pythonwhois.net.socket.setdefaulttimeout(30)
		result = pythonwhois.get_whois(domain)
		cdate = result["creation_date"]
		udate = result["updated_date"]
	except Exception as e:
		logger.debug("domain whois error: " + str(e))
	return JsonResponse(result)

