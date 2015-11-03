from django.db import models
from django.contrib.auth.models import User

import os

class IPAddress(models.Model):
	ip = models.GenericIPAddressField(unique=True)
	created_at = models.DateTimeField(auto_now_add=True)
        def __unicode__(self):
                return self.ip

class Domain(models.Model):
	name = models.CharField(max_length=2000, unique=True)
	suffix = models.CharField(max_length=200, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	whitelisted = models.BooleanField(default=False)
        def __unicode__(self):
                return self.name

class Hostname(models.Model):
	name = models.CharField(max_length=20000, unique=True)
	domain = models.ForeignKey(Domain, blank=True, null=True)
	subdomain = models.CharField(max_length=20000, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
        def __unicode__(self):
                return self.name

class URL(models.Model):
	url = models.URLField(max_length=20000, unique=True)
	hostname = models.ForeignKey(Hostname, blank=True, null=True)
	port = models.PositiveIntegerField(blank=True, null=True)
	protocol = models.CharField(max_length=200, blank=True, null=True)
	type = models.CharField(max_length=200, blank=True, null=True)
	data = models.TextField(blank=True, null=True)
	path = models.CharField(max_length=20000, blank=True, null=True)
	md5 = models.CharField(max_length=200, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
        def __unicode__(self):
                return self.url


class Host_IP(models.Model):
	hostname = models.ForeignKey(Hostname)
	ip = models.ManyToManyField(IPAddress)
	#ip_new = models.ManyToManyField(IPAddress, related_name="ip_new")
	#ip_out = models.ManyToManyField(IPAddress, related_name="ip_out")
	#timestamp = models.DateTimeField(auto_now_add=True)
	first_seen = models.DateTimeField(auto_now_add=True)
	last_seen = models.DateTimeField(auto_now=True)


class IP_Whois(models.Model):
	ip = models.ForeignKey(IPAddress)
	reverse = models.CharField(max_length=2000, blank=True, null=True)
	result = models.TextField(blank=True, null=True)
	md5 = models.CharField(max_length=200, blank=True, null=True)
	country = models.TextField(max_length=20, blank=True, null=True)
	description = models.TextField(max_length=2000, blank=True, null=True)
	creation_date = models.DateTimeField(blank=True, null=True)
	updated_date = models.DateTimeField(blank=True, null=True)
	#timestamp = models.DateTimeField(auto_now_add=True)
	first_seen = models.DateTimeField(auto_now_add=True)
	last_seen = models.DateTimeField(auto_now=True)

"""
class IP_Whois_History(models.Model):
	first_seen = models.DateTimeField(auto_now_add=True)
	last_seen = models.DateTimeField(auto_now=True)
	ip = models.ForeignKey(IPAddress)
	reverse = models.CharField(max_length=2000, blank=True, null=True)
	whois = models.ForeignKey(Whois_IP)
"""

class Person(models.Model):
	email = models.EmailField()
	name = models.CharField(max_length=2000, blank=True, null=True)
	organization = models.CharField(max_length=2000, blank=True, null=True)
	country = models.TextField(max_length=20, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

class Contact(models.Model):
	type = models.TextField(max_length=200, blank=True, null=True)
	person = models.ForeignKey(Person)
	created_at = models.DateTimeField(auto_now_add=True)

class Domain_Whois(models.Model):
	domain = models.ForeignKey(Domain)
	result = models.TextField(blank=True, null=True)
	md5 = models.CharField(max_length=200, blank=True, null=True)
	creation_date = models.DateTimeField(blank=True, null=True)
	updated_date = models.DateTimeField(blank=True, null=True)
	contact = models.ManyToManyField(Contact)
	#timestamp = models.DateTimeField(auto_now_add=True)
	first_seen = models.DateTimeField(auto_now_add=True)
	last_seen = models.DateTimeField(auto_now=True)

"""
class Domain_Whois_History(models.Model):
	first_seen = models.DateTimeField(auto_now_add=True)
	last_seen = models.DateTimeField(auto_now=True)
	domain = models.ForeignKey(Domain)
	whois = models.ForeignKey(Whois_Domain)
"""


class DNSRecord(models.Model):
	query = models.CharField(max_length=20000)
	md5 = models.CharField(max_length=200, blank=True, null=True)
	serialized = models.TextField(blank=True, null=True)
	a = models.ManyToManyField(IPAddress, related_name="A")
	aaaa = models.ManyToManyField(IPAddress, related_name="AAAA")
	cname = models.ManyToManyField(Hostname, related_name="CNAME")
	ns = models.ManyToManyField(Hostname, related_name="NS")
	mx = models.TextField(blank=True, null=True)
	soa = models.TextField(blank=True, null=True)
	txt = models.TextField(blank=True, null=True)
	#timestamp = models.DateTimeField(auto_now_add=True)
	first_seen = models.DateTimeField(auto_now_add=True)
	last_seen = models.DateTimeField(auto_now=True)

"""
class Domain_DNS(models.Model):
	first_seen = models.DateTimeField(auto_now_add=True)
	last_seen = models.DateTimeField(auto_now=True)
	domain = models.ForeignKey(Domain)
	dns = models.ForeignKey(DNSRecord)

class Host_DNS(models.Model):
	first_seen = models.DateTimeField(auto_now_add=True)
	last_seen = models.DateTimeField(auto_now=True)
	hostname = models.ForeignKey(Hostname)
	dns = models.ForeignKey(DNSRecord)
"""

class Content(models.Model):
	content = models.TextField(blank=True, null=True)
	md5 = models.CharField(max_length=32, blank=True, null=True)
	sha1 = models.CharField(max_length=40, blank=True, null=True)
	sha256 = models.CharField(max_length=64, blank=True, null=True)
	sha512 = models.CharField(max_length=128, blank=True, null=True)
	ssdeep = models.CharField(max_length=200, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	path = models.FilePathField(path=os.path.abspath(os.path.dirname(__file__)), max_length=2000)
	commit = models.CharField(max_length=200, blank=True, null=True)
	type = models.CharField(max_length=200, blank=True, null=True)
	length = models.PositiveIntegerField(blank=True, null=True)
	#analysis = models.ForeignKey(Analysis, blank=True, null=True)

class Analysis(models.Model):
	content = models.ForeignKey(Content, blank=True, null=True)
	result = models.TextField(blank=True, null=True)
	rule = models.CharField(max_length=200, blank=True, null=True)
	tag = models.CharField(max_length=200, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

class Capture(models.Model):
	path = models.FilePathField(path=os.path.abspath(os.path.dirname(__file__)), max_length=2000)
	commit = models.CharField(max_length=200, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	base64 = models.TextField(blank=True, null=True)
	b64thumb = models.TextField(blank=True, null=True)

#class Headers(models.Model):
#	serialized = models.TextField(blank=True, null=True)
#	created_at = models.DateTimeField(auto_now_add=True)

class Webapp(models.Model):
 	name = models.CharField(max_length=2000)
        def __unicode__(self):
                return self.name

class Resource(models.Model):
	url = models.ForeignKey(URL, blank=True, null=True)
	http_status = models.CharField(max_length=200, blank=True, null=True)
	headers = models.TextField(blank=True, null=True)
	#headers = models.ManyToManyField(Headers)
	content = models.ForeignKey(Content, blank=True, null=True)
	is_page = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	webapp = models.ManyToManyField(Webapp)
	analysis = models.ForeignKey(Analysis, blank=True, null=True)

RESTRICTION_CHOICES = (
    (0, 'login_user'),
    (1, 'group_only'),
    (2, 'all_user'),
)

class Query(models.Model):
	input = models.URLField(max_length=20000)
	registered_by = models.ForeignKey(User)
	restriction = models.PositiveSmallIntegerField(choices=RESTRICTION_CHOICES, default=0)
	interval = models.PositiveSmallIntegerField(default=0)
	counter = models.PositiveSmallIntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
        def __unicode__(self):
                return self.input

class UserAgent(models.Model):
	name = models.CharField(max_length=200)
	strings = models.CharField(max_length=2000)
	created_at = models.DateTimeField(auto_now_add=True)
        def __unicode__(self):
                return self.name

METHOD_CHOICES = (
    ('GET', 'GET'),
    ('POST', 'POST'),
    ('HEAD', 'HEAD'),
)

TIMEOUT_CHOICES = (
    (60, '1m'),
    (120, '2m'),
    (180, '3m'),
)


class Host_Info(models.Model):
	hostname = models.ForeignKey(Hostname)
	host_dns = models.ForeignKey(DNSRecord, related_name="host_dns", blank=True, null=True)
	domain_dns = models.ForeignKey(DNSRecord, related_name="domain_dns", blank=True, null=True)
	domain_whois = models.ForeignKey(Domain_Whois, blank=True, null=True)
	ip_whois = models.ManyToManyField(IP_Whois)
	#timestamp = models.DateTimeField(auto_now_add=True)
	first_seen = models.DateTimeField(auto_now_add=True)
	last_seen = models.DateTimeField(auto_now=True)

class Resource_Info(models.Model):
	resource = models.ForeignKey(Resource)
	headers = models.TextField(blank=True, null=True)
	seq = models.PositiveIntegerField()
	host_info = models.ForeignKey(Host_Info, blank=True, null=True) 
	timestamp = models.DateTimeField(auto_now_add=True)
	webapp = models.ManyToManyField(Webapp)
	analysis = models.ForeignKey(Analysis, blank=True, null=True)

class Job(models.Model):
	query = models.ForeignKey(Query)
	status = models.CharField(max_length=2000, blank=True, null=True)
	user_agent = models.ForeignKey(UserAgent, blank=True, null=True)
	referer = models.CharField(max_length=2000, blank=True, null=True)
	proxy = models.ForeignKey(URL, blank=True, null=True)
	additional_headers = models.TextField(blank=True, null=True)
	method = models.CharField(max_length=10, default='GET')
	post_data = models.TextField(blank=True, null=True)
	timeout = models.PositiveSmallIntegerField(choices=TIMEOUT_CHOICES, default=60)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	page = models.ForeignKey(Resource_Info, blank=True, null=True, related_name="page")
	capture = models.ForeignKey(Capture, blank=True, null=True)
	resources = models.ManyToManyField(Resource_Info, related_name="resources")
	#new = models.ManyToManyField(Resource, related_name="new")
	#out = models.ManyToManyField(Resource, related_name="out")
	#changed = models.ManyToManyField(Resource, related_name="changed")
	#not_changed = models.ManyToManyField(Resource, related_name="not_changed")


