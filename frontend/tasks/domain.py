from ..celery import app

from ..models import *

from django.utils import timezone

import pythonwhois
import hashlib, datetime

from ..logger import getlogger
import logging
logger = getlogger()

#@app.task
@app.task(rate_limit="5/m")
def whois_domain(did):
	domain = Domain.objects.get(pk=did)

	last = None
        dws = Domain_Whois_History.objects.filter(domain=domain).order_by("-last_seen")
        if dws:
	        last = dws[0]
                #if datetime.datetime.now() < (last.last_seen + datetime.timedelta(minutes=1)):
                if timezone.now() < (last.last_seen + datetime.timedelta(minutes=10)):
        	        logger.debug("domain whois skipped: " + domain.name)
			return last

	result = None
	cdate = None
	udate = None
	try:
		pythonwhois.net.socket.setdefaulttimeout(30)
		result = pythonwhois.get_whois(domain.name)
		cdate = result["creation_date"]
		udate = result["updated_date"]

	except Exception as e:
		logger.debug("domain whois error: " + str(e))
		return None

	if last:
		if last.whois.updated_date == udate:
			logger.debug("domain whois not changed: " + domain.name)
			last.save()
			return last

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
		wd.result = raw[0]
		wd.md5 = hashlib.md5(raw[0]).hexdigest()
		wd.save()
	#dwh = Domain_Whois_History.objects.create(
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
