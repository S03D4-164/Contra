from django.db import transaction
from ..celery import app

from ..api import ContraAPI
from ..models import *

from django.utils import timezone

import requests, pythonwhois, hashlib, datetime, tldextract

from ..logger import getlogger
import logging
logger = getlogger()

@app.task(soft_time_limit=60)
def whois_domain(input):
    api = ContraAPI()
    payload = {'domain':input}
    res = requests.get(api.whois_domain, params=payload, verify=False)
    result = None
    try:
        result = res.json()
    except Exception as e:
        logger.error(str(e))
        return None

    no_fetch_extract = tldextract.TLDExtract(suffix_list_url=False)
    #ext = no_fetch_extract(str(input))
    ext = no_fetch_extract(input)
    suffix = ext.suffix
    name = None
    if suffix:
        name = ext.domain + '.'+ suffix

    domain = None
    if name:
        try:
            domain, created = Domain.objects.get_or_create(
                name = name,
                suffix = suffix
            )
        except Exception as e:
            logger.error(str(e))
            try:
                domain = Domain.objects.get(
                    name = name,
                    suffix = suffix
                )
            except Exception as e:
                logger.error(str(e))
                return None
    cdate = None
    if "creation_date" in result:
        cdate = result["creation_date"]

    udate = None
    if "updated_date" in result:
        udate = result["updated_date"]

    w = None
    try:
        #with transaction.atomic():
        w, created = Domain_Whois.objects.get_or_create(
            domain = domain,
            creation_date = cdate[0],
            updated_date = udate[0],
        )
        if not created:
            logger.debug("domain whois already exists: " + domain.name)
    except Exception as e:
        logger.debug(str(e))
        try:
            w = Domain_Whois.objects.get(
                domain = domain,
                creation_date = cdate[0],
                updated_date = udate[0],
            )
        except Exception as e:
            logger.debug(str(e))
            return None

    raw = None
    if "raw" in result:
        raw = result["raw"]
        if not w.result:
            w.result = raw[0].encode("utf-8")
        if not w.md5:
            w.md5 = hashlib.md5(raw[0].encode("utf-8")).hexdigest()
        w.save()

    if "contacts" in result:
        logger.debug(result["contacts"])
        #set_contact.delay(w, result)
        w = set_contact(w, result)

    return w

@app.task
def set_contact(w, result):
    for type in result["contacts"]:
        c = result["contacts"][type]
        person = None
        pcreated = None
        if c:
            email = None
            if "email" in c:
                email = c["email"]
            name = None
            if "name" in c:
                name = c["name"]
            org = None
            if "organization" in c:
                org = c["organization"]
            country = None
            if "country" in c:
                country = c["country"]
            if email:
                try:
                    person, pcreated = Person.objects.get_or_create(
                        email = email,
                        name = name,
                        organization = org,
                        country = country,
                    )
                except:
                    person = Person.objects.get(
                        email = email,
                        name = name,
                        organization = org,
                        country = country,
                    )

        contact = None
        if person:
            try:
                contact, ccreated = Contact.objects.get_or_create(
                    type = type,
                    person = person,
                )
            except:
                contact = Contact.objects.get(
                    type = type,
                    person = person,
                )

        if contact:
            w.contact.add(contact)
            w.save()

    return w

