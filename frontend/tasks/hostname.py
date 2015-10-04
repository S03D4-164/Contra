from ..celery import app

import tldextract, socket, datetime

from ..models import *
#from .domain import whois_domain
from .ipaddress import whois_ip

from ..logger import getlogger
import logging
logger = getlogger()

#@app.task(rate_limit="1/s")
@app.task
def iplookup(hid):
	hostname = Hostname.objects.get(pk=hid)
	hostips = Host_IP.objects.filter(hostname=hostname).order_by("-last_seen")
	last = None
	ips = []
	if hostips:
		last = hostips[0]
	try:
		addr = socket.getaddrinfo(hostname.name, None)
		for a in addr:
			ip = a[4][0]
			i, created = IPAddress.objects.get_or_create(
				ip = ip
			)
			if not i in ips:
				ips.append(i)
				#logger.debug(i)
	except Exception as e:
		logger.debug(e)

	h = None
	if last:
		ip_new = []
		ip_out = []
		for i in ips:
			if not i in last.ip.all():
				ip_new.append(i)
		for i in last.ip.all():
			if not i in ips:
				ip_out.append(i)
		if ip_new or ip_out:
			logger.debug("ip changed: " + hostname.name)
			h = Host_IP.objects.create(
				hostname = hostname,
			)
			for i in ips:
				h.ip.add(i)
			for i in ip_new:
				h.ip_new.add(i)
			for i in ip_out:
				h.ip_out.add(i)
			h.save()
		else:
			logger.debug("ip not changed: " + hostname.name)
			h = last
			h.save()
	else:
		logger.debug("new hostname: " + hostname.name)
		h = Host_IP.objects.create(
			hostname = hostname,
		)
		for i in ips:
			h.ip.add(i)
			h.ip_new.add(i)
		h.save()

	return h
