from django.db import transaction

from ..models import *

import re, hashlib, tldextract, datetime

import logging
from ..logger import getlogger
#logger = getlogger(logging.DEBUG)
logger = getlogger()

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
        try:
            server = url.split('/')[2]
            path = url.split('/')[3:]
        except Exception as e:
            logger.error(str(e))
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
        h = None
        try:            
            h, created = Hostname.objects.get_or_create(name=ipv6)
        except:
            h = Hostname.objects.get(name=ipv6)
        if h:
            try:
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
                url = URL.objects.get(
                    md5 = hashlib.md5(p["url"].encode("utf-8")).hexdigest()
                )
    return url
            
def parse_ipv4url(p):
    ipv4 = p["server"]
    s = p["server"].split(':')
    if len(s) == 2:
        ipv4 = p["server"].split(':')[0]        
        p["port"] = p["server"].split(':')[1]
    h = None
    try:
        h, created = Hostname.objects.get_or_create(name=ipv4)
    except:
        h = Hostname.objects.get(name=ipv4)
    url = None
    if h:
        try:
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
            url = URL.objects.get(
                md5 = hashlib.md5(p["url"].encode("utf-8")).hexdigest()
            )

    return url

def parse_hostname(hostname):
    no_fetch_extract = tldextract.TLDExtract(suffix_list_url=False)
    ext = no_fetch_extract(hostname)
    suffix = ext.suffix
    domain = None
    if suffix:
        domain = ext.domain + '.'+ suffix
        
    subdomain = ext.subdomain
    d = None
    try:
        d, created = Domain.objects.get_or_create(
            name = domain,
            suffix = suffix
        )
    except:
        d = Domain.objects.get(
            name = domain,
            suffix = suffix
        )
    h = None
    try:
        h, created = Hostname.objects.get_or_create(
            name = hostname,
            domain = d,
            subdomain = subdomain,
        )
    except Exception as e:
        logger.error(e)
        h = Hostname.objects.get(
            name = hostname,
        )

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
        url = URL.objects.get(
            md5 = hashlib.md5(p["url"].encode("utf-8")).hexdigest()
        )

    return url

def parse_datauri(p):
    data = p["url"].split(",")[1:]
    head = p["url"].split(",")[0]
    prefix = head.split(";")[0]
    type = prefix.split(":")[1]
    url = None
    try:
        url, created = URL.objects.get_or_create(
            url = p["url"],
            protocol = p["protocol"],
            type = type,
            md5 = hashlib.md5(p["url"].encode("utf-8")).hexdigest()
        )
    except Exception as e:
        logger.error(e)
        url = URL.objects.get(
            md5 = hashlib.md5(p["url"].encode("utf-8")).hexdigest()
        )
    return url

def parse_url(url):
    p = None
    try:
        p = init_parse(url)
        logger.debug(p)
    except Exception as e:
        logger.error(str(e))

    u = None
    try:
        if p["protocol"]== "data":
            u = parse_datauri(p)
        elif p["server"]:
            if re.search("[0-9a-f]*:[0-9a-f]*:[0-9a-f]+", p["server"]):
                u = parse_ipv6url(p)
            elif re.search("^([0-9]{1,3}\.){3}[0-9]{1,3}:?", p["server"]):
                u = parse_ipv4url(p)
            else:
                u = parse_standard(p)
    except Exception as e:
        logger.error(str(e))

    return u


