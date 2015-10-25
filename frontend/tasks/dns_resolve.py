from ..celery import app

from ..models import *
from .parse_task import parse_hostname

import requests, hashlib

from ..logger import getlogger
import logging
logger = getlogger()

@app.task
def dns_resolve(query):
	api = "http://localhost:8000/api/dns_resolve"
	payload = {'query':query}
	res = requests.get(api, params=payload, verify=False)
	result = res.json()
	d = None
	if result:
		logger.debug(result)
		md5 = hashlib.md5(str(result)).hexdigest()
		d, created = DNSRecord.objects.get_or_create(
			query = query,
			md5 = md5,
			serialized = str(result),
			mx = "\n".join(result["MX"]),
			soa = "\n".join(result["SOA"]),
			txt = "\n".join(result["TXT"]),
		)
		if not created:
			logger.debug("DNS result already exists.")
			return d
		for a in result["A"]:
			logger.debug(a)
			ip, created = IPAddress.objects.get_or_create(
				ip = a
			)
			d.a.add(ip)
		for a in result["AAAA"]:
			ip, created = IPAddress.objects.get_or_create(
				ip = a
			)
			d.aaaa.add(ip)
		for a in result["CNAME"]:
			h = parse_hostname(a)
			if h:
				d.cname.add(h)
		for a in result["NS"]:
			h = parse_hostname(a)
			if h:
				d.ns.add(h)
		d.save()
	return d
