from ..celery import app

from ipwhois import IPWhois
import hashlib
import datetime

from ..models import *
#from ..views.db import get_node_on_db

from ..logger import getlogger
import logging
logger = getlogger()

#@app.task
@app.task(rate_limit="5/m")
def whois_ip(ipid):
	ip = IPAddress.objects.get(pk=ipid)
	#logger.debug(ip)
        iws = IP_Whois_History.objects.filter(ip=ip).order_by("-last_seen")
	last = None
        if iws:
	        last = iws[0]
                if datetime.datetime.now() < (last.last_seen + datetime.timedelta(minutes=30)):
                	logger.debug("ip whois skipped: " + ip.ip)
			return last

	results = None
	reverse = None
	try:
		obj = IPWhois(ip.ip)
		results = obj.lookup(inc_raw=True)
		logger.debug(results["nets"])
		rev = obj.get_host()
		logger.debug(rev)
		if rev:
			reverse = rev[0]
	except Exception as e:
		logger.debug(e)

	if results:
		nets = sorted(results["nets"], key=lambda n:n["cidr"], reverse=True)[0]
		if last:
			if last.whois.updated_date == nets["updated"]:
				logger.debug("ip whois not changed: " + ip.ip)
				last.save()
				return last
		else:
			logger.debug("ip whois changed: " + ip.ip)

		wi, created = Whois_IP.objects.get_or_create(
			ip = ip,
			result = results["raw"],
			md5 = hashlib.md5(results["raw"]).hexdigest(),
			country = nets["country"],
			description = nets["description"],
			creation_date = nets["created"],
			updated_date = nets["updated"],
		)
		iwh = IP_Whois_History.objects.create(
			ip = ip,
			whois = wi,
			reverse = reverse,
		)
		return iwh
	else:
		return None
