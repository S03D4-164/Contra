from ..celery import app

from .parse_task import parse_hostname
from .dns_resolve import dns_resolve
from .whois_domain import whois_domain
from .whois_ip import whois_ip

from ..models import *

import re

from ..logger import getlogger
import logging
logger = getlogger()

def create_hostip(hostname, ips):
        hostips = Host_IP.objects.filter(hostname=hostname).order_by("-last_seen")
        last = None
        if hostips:
                last = hostips[0]
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
			"""
                        for i in ip_new:
                                h.ip_new.add(i)
                        for i in ip_out:
                                h.ip_out.add(i)
			"""
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
                        #h.ip_new.add(i)
                h.save()

	return h

@app.task
def host_inspect(host):
	logger.debug(host)
	hostname = parse_hostname(host)

	host_dr = dns_resolve(hostname.name)
        ips = []
        if re.search("\[?([0-9a-f]*:[0-9a-f]*:[0-9a-f]+)\]?:?([0-9]{,5})?", hostname.name):
		try:
			ip = IPAddress.objects.create(ip = hostname.name)
			ips.append(ip)
		except:
			ip = IPAddress.objects.get(ip = hostname.name)
			ips.append(ip)
        elif re.search("^([0-9]{1,3}\.){3}[0-9]{1,3}$", hostname.name):
		try:
			ip = IPAddress.objects.create(ip = hostname.name)
			ips.append(ip)
		except:
			ip = IPAddress.objects.get(ip = hostname.name)
			ips.append(ip)
	elif host_dr:
		ipv4 = host_dr.a.all()
		for ip in ipv4:
	                if not ip in ips:
               			ips.append(ip)
		ipv6 = host_dr.aaaa.all()
		for ip in ipv6:
               		if not ip in ips:
	                	ips.append(ip)

	#host_ip = create_hostip(hostname, ips)

	domain = hostname.domain
	domain_dr = None
	domain_whois = None
	if domain:
		domain_dr = dns_resolve(domain.name)
		domain_whois = whois_domain(domain.name)
	
        host_info, created = Host_Info.objects.get_or_create(
                hostname = hostname,
                host_dns = host_dr,
                #host_ip = host_ip,
                domain_dns = domain_dr,
                domain_whois = domain_whois,
        )
	"""
	if host_ip:
        	for i in host_ip.ip.all():
                	ip_whois = whois_ip(i.ip)
                	if ip_whois:
                        	host_info.ip_whois.add(ip_whois)
	if not host_info.ip_whois.all():
	"""
	if created:
		for i in ips:
      	        	ip_whois = whois_ip(i.ip)
        	       	if ip_whois:
                       		host_info.ip_whois.add(ip_whois)

        host_info.save()

	return host_info
