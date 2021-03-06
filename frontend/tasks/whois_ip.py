from django.db import transaction
from ..celery import app

from django.utils import timezone

from ipwhois import IPWhois
import requests, hashlib, datetime, re

from ..api import ContraAPI
from ..models import *

from ..logger import getlogger
import logging
logger = getlogger()

@app.task
def whois_ip(input):
    api = ContraAPI()
    payload = {'ip':input}
    result = None
    try:
        print api.whois_ip
        res = requests.get(api.whois_ip, params=payload, verify=False)
        result = res.json()
    except Exception as e:
        logger.error(str(e))
        return None

    ip = None
    try:
        ip = IPAddress.objects.create(
            ip = input
        )
    except Exception as e:
        #logger.debug(str(e))
        try:
            ip = IPAddress.objects.get(
                ip = input
            )
        except:
            return None
        
    nets = None
    if "nets" in result:
        if result["nets"]:
            nets = sorted(result["nets"], key=lambda n:n["cidr"], reverse=True)[0]
            logger.debug(nets)
            if "created" in nets:
                if nets["created"]:
                    if re.match("^[0-9]{8}$", nets["created"]):
                        nets["created"] = datetime.datetime.strptime(nets["created"],'%Y%m%d')
            if "updated" in nets:
                if nets["updated"]:
                    if re.match("^[0-9]{8}$", nets["updated"]):
                        nets["updated"] = datetime.datetime.strptime(nets["updated"],'%Y%m%d')

    elif "error" in result:
        if result["error"]:
            try:
                #with transaction.atomic():
                w, created = IP_Whois.objects.get_or_create(
                    ip = ip,
                    result = result["error"],
                )
                return w
            except Exception as e:
                logger.error(str(e))
                try:
                    w = IP_Whois.objects.get(
                        ip = ip,
                        result = result["error"],
                    )
                    return w
                except Exception as e:
                    logger.error(str(e))
                    return None
    w = None
            
    try:
        #with transaction.atomic():
        w, created = IP_Whois.objects.get_or_create(
            ip = ip,
            creation_date = nets["created"],
            updated_date = nets["updated"],
        )
        if not created:
            logger.debug("ip whois already exists: " + ip.ip)
    except Exception as e:
        logger.error(str(e))
        try:
            w = IP_Whois.objects.get(
                ip = ip,
                creation_date = nets["created"],
                updated_date = nets["updated"],
            )
        except Exception as e:
            logger.error(str(e))
            return None

    if not w.result:
        w.result = result["raw"].encode("utf-8")
    if not w.md5:
        w.md5 = hashlib.md5(result["raw"].encode("utf-8")).hexdigest()
    if not w.country:
        w.country = nets["country"]
    if not w.description:
        w.description = nets["description"]
    if not w.reverse and "reverse" in result:
        if result["reverse"]:
            r = result["reverse"]
            if type(r) is list:
                w.reverse = r[0]
            else:
                w.reverse = r
    w.save()

    return w
