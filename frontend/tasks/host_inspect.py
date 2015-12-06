from django.db import transaction
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
    logger.debug(ips)

    domain = hostname.domain
    domain_dr = None
    domain_whois = None
    if domain:
        domain_dr = dns_resolve(domain.name)
        domain_whois = whois_domain(domain.name)

    host_info = None
    created = None
    try:
        #with transaction.atomic():
        host_info, created = Host_Info.objects.get_or_create(
            hostname = hostname,
            host_dns = host_dr,
            domain_dns = domain_dr,
            domain_whois = domain_whois,
        )
    except Exception as e:
        logger.error(str(e))
        try:
            host_info = Host_Info.objects.get(
                hostname = hostname,
                host_dns = host_dr,
                domain_dns = domain_dr,
                domain_whois = domain_whois,
            )
        except Exception as e:
            logger.error(str(e))

    if created:
        for i in ips:
            ip_whois = whois_ip(i.ip)
            if ip_whois:
                host_info.ip_whois.add(ip_whois)
                host_info.save()

    return host_info
