from ..models import *

import re, hashlib, tldextract

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
	m = re.search("\[?([0-9a-f]*:[0-9a-f]*:[0-9a-f]+)\]?:?([0-9]{,5})?", p["server"])
	if m:
		ipv6 = m.group(1)
		if len(m) == 2:
			p["port"] = m.group(2)
		try:
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
			return url
		except Exception as e:
			logger.error(e)
	return None
			
def parse_ipv4(p):
	ipv4 = p["server"]
	s = p["server"].split(':')
	if len(s) == 2:
		ipv4 = p["server"].split(':')[0]		
		p["port"] = p["server"].split(':')[1]
	try:
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
		return url
	except Exception as e:
		logger.error(e)
	return None

def parse_standard(p):
	hostname = p["server"]
	s = p["server"].split(':')
	if len(s) == 2:
		hostname = p["server"].split(':')[0]		
		p["port"] = p["server"].split(':')[1]
        no_fetch_extract = tldextract.TLDExtract(suffix_list_url=False)
        ext = no_fetch_extract(hostname.encode("utf-8"))
	tld = ext.suffix
        domain = ext.domain + '.'+ tld
	subdomain = ext.subdomain
	if domain:
		d, created = Domain.objects.get_or_create(
			name = domain,
			tld = tld
		)
		h, created = Hostname.objects.get_or_create(
			name = hostname,
			domain = d,
			subdomain = subdomain,
		)
		url, created = URL.objects.get_or_create(
			url = p["url"],
			hostname = h,
			port = p["port"],
			protocol = p["protocol"],
			path = p["path"],
			md5 = hashlib.md5(p["url"].encode("utf-8")).hexdigest()
		)
		return url
	#except Exception as e:
	#	print e
	return None

def parse_datauri(p):
	data = p["url"].split(",")[1:]
	head = p["url"].split(",")[0]
	prefix = head.split(";")[0]
	type = prefix.split(":")[0]
	try:
		url, created = URL.objects.get_or_create(
			url = p["url"],
			protocol = p["protocol"],
			type = type,
			data = data,
			md5 = hashlib.md5(p["url"]).hexdigest()
		)
		return url
	except Exception as e:
		logger.error(e)
	return None

def parse_url(url):
	u = None

	p = init_parse(url)
	logger.debug(p)

	if p["protocol"]== "data":
		u = parse_datauri(p)
	else:
		if re.search("[0-9a-f]*:[0-9a-f]*:[0-9a-f]+", p["server"]):
			u = parse_ipv6url(p)
		elif re.search("^[0-9a-f]*:[0-9a-f]*:[0-9a-f]+", p["server"]):
			u = parse_ipv4url(p)
		else:
			u = parse_standard(p)
	return u


