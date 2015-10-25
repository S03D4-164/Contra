from .parse_task import parse_hostname
from .dns_resolve import dns_resolve
from .whois_domain import whois_domain
from .whois_ip import whois_ip

from ..models import *

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

def host_inspect(host):
	hostname = parse_hostname(host)

	host_dr = dns_resolve(hostname.name)
	last_hd = Host_DNS.objects.filter(hostname=hostname).order_by("-pk")
	host_dns = None
	if last_hd:
		if host_dr == last_hd[0].dns:
			host_dns = last_hd[0]
			host_dns.save()
	if not host_dns:
		host_dns = Host_DNS.objects.create(
			hostname = hostname,
			dns = host_dr,
		)

        ips = []
	ipv4 = host_dns.dns.a.all()
	for ip in ipv4:
                if not ip in ips:
                	ips.append(ip)
	ipv6 = host_dns.dns.aaaa.all()
	for ip in ipv6:
                if not ip in ips:
                	ips.append(ip)
	host_ip = create_hostip(hostname, ips)

	domain = hostname.domain
	domain_dr = dns_resolve(domain.name)
	last_dd = Domain_DNS.objects.filter(domain=domain).order_by("-pk")
	domain_dns = None
	if last_dd:
		if domain_dr == last_dd[0].dns:
			domain_dns = last_dd[0]
			domain_dns.save()
	if not domain_dns:
		domain_dns = Domain_DNS.objects.create(
			domain = domain,
			dns = domain_dr,
		)
	domain_whois = whois_domain(domain.name)
	
        host_info, created = Host_Info.objects.get_or_create(
                hostname = hostname,
                host_dns = host_dns,
                host_ip = host_ip,
                domain_dns = domain_dns,
                domain_whois = domain_whois,
        )
	if host_ip:
        	for i in host_ip.ip.all():
                	ip_whois = whois_ip(i.ip)
                	if ip_whois:
                        	host_info.ip_whois.add(ip_whois)
        host_info.save()

	return host_info
