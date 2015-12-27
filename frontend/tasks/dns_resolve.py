from ..celery import app

from ..api import ContraAPI
from ..models import *
from .parse_task import parse_hostname

import requests, hashlib, json

from ..logger import getlogger
import logging
logger = getlogger()

@app.task(soft_time_limit=60)
def dns_resolve(query):
    api = ContraAPI()
    payload = {'query':query}
    result = None
    try:
        res = requests.get(api.dns, params=payload, verify=False)
        result = res.json()
    except Exception as e:
        logger.debug(str(e))
        return None

    d = None
    created = None
    if result:
        serialized = str(json.dumps(result, sort_keys=True)).encode('utf-8')
        logger.debug(serialized)
        md5 = hashlib.md5(serialized).hexdigest()
        try:
            d, created = DNSRecord.objects.get_or_create(
                query = query,
                md5 = md5,
                serialized = serialized,
                mx = "\n".join(result["MX"]),
                txt = "\n".join(result["TXT"]),
                soa = "\n".join(result["SOA"]),
                axfr = result["AXFR"],
            )
            if not created:
                logger.debug("DNS result already exists.")
                return d
        except Exception as e:
            logger.debug(str(e))
            try:
                d = DNSRecord.objects.get(
                    query = query,
                    md5 = md5,
                    serialized = str(serialized),
                    mx = "\n".join(result["MX"]),
                    txt = "\n".join(result["TXT"]),
                    soa = "\n".join(result["SOA"]),
                    axfr = result["AXFR"],
                )
                return d
            except Exception as e:
                logger.debug(str(e))
                return None
        for a in result["A"]:
            ip = None
            try:
                ip = IPAddress.objects.create(ip = a)
            except:
                ip = IPAddress.objects.get(ip = a)
            if ip:
                d.a.add(ip)
        for a in result["AAAA"]:
            ip = None
            try:
                ip = IPAddress.objects.create(ip = a)
            except:
                ip = IPAddress.objects.get(ip = a)
            if ip:
                d.a.add(ip)
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
