from ..celery import app

from django.utils import timezone

from ipwhois import IPWhois
import requests, hashlib, datetime

from ..models import *

from ..logger import getlogger
import logging
logger = getlogger()

@app.task
def whois_ip(input):
        api = "http://localhost:8000/api/whois_ip"
        payload = {'ip':input}
        res = requests.get(api, params=payload, verify=False)
        results = res.json()
        if not results:
                return None

	if results:
		ip, created = IPAddress.objects.get_or_create(
                                ip = results["query"]
                )
		nets = sorted(results["nets"], key=lambda n:n["cidr"], reverse=True)[0]
		print nets
		wi, created = Whois_IP.objects.get_or_create(
			ip = ip,
			creation_date = nets["created"],
			updated_date = nets["updated"],
		)
	        if created:
        	        logger.debug("ip whois created: " + ip.ip)
	        else:
        	        logger.debug("ip whois already exists: " + ip.ip)

		if not wi.result:
			wi.result = results["raw"].encode("utf-8")
		if not wi.md5:
			wi.md5 = hashlib.md5(results["raw"].encode("utf-8")).hexdigest()
		if not wi.country:
			wi.country = nets["country"]
		if not wi.description:
			wi.description = nets["description"]
		wi.save()

		iwh, created = IP_Whois_History.objects.get_or_create(
			ip = ip,
			whois = wi,
		)
		if not iwh.reverse:
			try:
				iwh.reverse = results["reverse"][0]
			except Exception as e:
				logger.error(str(e))
		iwh.save()

	return iwh
