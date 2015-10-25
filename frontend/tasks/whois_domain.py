from ..celery import app

from ..models import *

from django.utils import timezone

import requests, pythonwhois, hashlib, datetime, tldextract

from ..logger import getlogger
import logging
logger = getlogger()

@app.task
def whois_domain(input):
        api = "http://localhost:8000/api/whois_domain"
        payload = {'domain':input}
        res = requests.get(api, params=payload, verify=False)
        result = res.json()
	if not result:
		return None

        no_fetch_extract = tldextract.TLDExtract(suffix_list_url=False)
        ext = no_fetch_extract(input.encode("utf-8"))
        suffix = ext.suffix
        name = ext.domain + '.'+ suffix
        if name:
       		domain, created = Domain.objects.get_or_create(
               	        name = name,
                       	suffix = suffix
               	)
	cdate = result["creation_date"]
	udate = result["updated_date"]
	
	wd, created = Whois_Domain.objects.get_or_create(
		domain = domain,
		creation_date = cdate[0],
		updated_date = udate[0],
	)
	if created:
		logger.debug("domain whois created: " + domain.name)
	else:
		logger.debug("domain whois already exists: " + domain.name)
	raw = result["raw"]
	if raw:
		wd.result = raw[0].encode("utf-8")
		wd.md5 = hashlib.md5(raw[0].encode("utf-8")).hexdigest()
		wd.save()

	dwh, created = Domain_Whois_History.objects.get_or_create(
		domain = domain,
		whois = wd,
	)
	dwh.save()
	logger.debug(result["contacts"])
	for type in result["contacts"]:
		c = result["contacts"][type]
		try:
			person, created = Person.objects.get_or_create(
				email = c["email"],
				name = c["name"],
				organization = c["organization"],
				#country = contact["country"],
			)
			if person:
				contact, created = Contact.objects.get_or_create(
					type = type,
					person = person,
				)
				wd.contact.add(contact)
				wd.save()
				person.country = c["country"]
				person.save()
		except Exception as e:
			logger.debug(e)

	return dwh
