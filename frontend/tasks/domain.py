from ..celery import app

from pythonwhois import get_whois

from ..models import *

import hashlib, datetime

from ..logger import getlogger
import logging

logger = getlogger()

#@app.task
@app.task(rate_limit="5/m")
def whois_domain(did):
	domain = Domain.objects.get(pk=did)
	#logger.debug(domain)

	last = None
        dws = Domain_Whois_History.objects.filter(domain=domain).order_by("-last_seen")
        if dws:
	        last = dws[0]
                if datetime.datetime.now() < (last.last_seen + datetime.timedelta(minutes=1)):
        	        logger.debug("domain whois skipped: " + domain.name)
			return last

	result = None
	cdate = None
	udate = None
	try:
		result = get_whois(domain.name)
		cdate = result["creation_date"]
		udate = result["updated_date"]

	except Exception as e:
		logger.debug(e)
		return None

	if last:
		if last.whois.updated_date == udate:
			logger.debug("domain whois not changed: " + domain.name)
			last.save()
			return last

	logger.debug("creating domain whois: " + domain.name)
	wd, created = Whois_Domain.objects.get_or_create(
		domain = domain,
		creation_date = cdate[0],
		updated_date = udate[0],
	)
	raw = result["raw"]
	if raw:
		wd.result = raw[0]
		wd.md5 = hashlib.md5(raw[0]).hexdigest()
		wd.save()
	dwh = Domain_Whois_History.objects.create(
		domain = domain,
		whois = wd,
	)
	logger.debug(result["contacts"])
	for type in result["contacts"]:
		contact = result["contacts"][type]
		try:
			c, created = Contact.objects.get_or_create(
				email = contact["email"],
				name = contact["name"],
				organization = contact["organization"],
				type = type,
				#country = contact["country"],
			)
			if c:
				wd.contact.add(c)
				wd.save()
				c.country = contact["country"]
				c.save()
		except Exception as e:
			logger.debug(e)
	return dwh
