from django.db import transaction

from ..models import *

import re, hashlib, tldextract, datetime

import logging
from ..logger import getlogger
logger = getlogger(logging.DEBUG)

def init_parse(url):
    port = None
    protocol = url.split(':')[0]
    if protocol == "http":
        port = 80
    elif protocol == "https":
        port = 443
    elif protocol == "ftp":
        port = 21

    server = None
    path = None
    if protocol != "data":
        server = url.split('/')[2]
        path = url.split('/')[3:]
    parsed = {
        "url":url,
        "protocol":protocol,
        "server":server,
        "path":path,
        "port":port,
    }
    return parsed

def parse_ipv6url(p):
    url = None
    m = re.search("\[?([0-9a-f]*:[0-9a-f]*:[0-9a-f]+)\]?:?([0-9]{,5})?", p["server"])
    if m:
        ipv6 = m.group(1)
        if len(m) == 2:
            p["port"] = m.group(2)
        try:
            
            with transaction.atomic():
                h, created = Hostname.objects.get_or_create(
                    name = ipv6,
                )
                url, created = URL.objects.get_or_create(
                    url = p["url"],
                    hostname = h,
                    port = p["port"],
                    protocol = p["protocol"],
                    path = p["path"],
                    md5 = hashlib.md5(p["url"]).hexdigest()
                )
        except Exception as e:
            logger.error(e)
    return url
            
def parse_ipv4url(p):
    ipv4 = p["server"]
    s = p["server"].split(':')
    if len(s) == 2:
        ipv4 = p["server"].split(':')[0]        
        p["port"] = p["server"].split(':')[1]
    url = None
    try:
        with transaction.atomic():
            h, created = Hostname.objects.get_or_create(
                name = ipv4,
            )
            url, created = URL.objects.get_or_create(
                url = p["url"],
                hostname = h,
                port = p["port"],
                protocol = p["protocol"],
                path = p["path"],
                md5 = hashlib.md5(p["url"]).hexdigest()
            )
    except Exception as e:
        logger.error(e)

    return url

def parse_hostname(hostname):
    no_fetch_extract = tldextract.TLDExtract(suffix_list_url=False)
    ext = no_fetch_extract(str(hostname).encode("utf-8"))
    logger.debug(ext)
    suffix = ext.suffix
    domain = None
    if suffix:
        domain = ext.domain + '.'+ suffix
        
    subdomain = ext.subdomain
    h = None
    try:
        with transaction.atomic():
            d = None
            if domain:
                d, created = Domain.objects.get_or_create(
                    name = domain,
                    suffix = suffix
                )
            h, created = Hostname.objects.get_or_create(
                name = hostname,
                domain = d,
                subdomain = subdomain,
            )
    except Exception as e:
        logger.error(e)
        try:
            h = Hostname.objects.get(
                name = hostname,
            )
        except:
            pass

    return h

def parse_standard(p):
    hostname = p["server"]
    s = p["server"].split(':')
    if len(s) == 2:
        hostname = p["server"].split(':')[0]        
        p["port"] = p["server"].split(':')[1]

    h = parse_hostname(hostname)
    url = None
    try:
        with transaction.atomic():
            url, created = URL.objects.get_or_create(
                url = p["url"],
                hostname = h,
                port = p["port"],
                protocol = p["protocol"],
                path = p["path"],
                md5 = hashlib.md5(p["url"].encode("utf-8")).hexdigest()
            )
    except Exception as e:
        logger.error(e)

    return url

def parse_datauri(p):
    data = p["url"].split(",")[1:]
    head = p["url"].split(",")[0]
    prefix = head.split(";")[0]
    type = prefix.split(":")[1]
    url = None
    try:
        with transaction.atomic():
            url, created = URL.objects.get_or_create(
                url = p["url"],
                protocol = p["protocol"],
                #type = type,
                data = data,
                md5 = hashlib.md5(p["url"]).hexdigest()
            )
            if url:
                url.type = type
                url.save()
    except Exception as e:
        logger.error(e)
    return url

def parse_url(url):
    u = None

    p = init_parse(url)
    logger.debug(p)

    if p["protocol"]== "data":
        u = parse_datauri(p)
    else:
        if re.search("[0-9a-f]*:[0-9a-f]*:[0-9a-f]+", p["server"]):
            u = parse_ipv6url(p)
        elif re.search("^([0-9]{1,3}\.){3}[0-9]{1,3}:?", p["server"]):
            u = parse_ipv4url(p)
        else:
            u = parse_standard(p)
    return u


