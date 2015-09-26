from django.db import models

import os

class Email(models.Model):
	address = models.EmailField(unique=True)
	user = models.CharField(max_length=2000, blank=True, null=True)
	type = models.TextField(max_length=200, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
        def __unicode__(self):
                return self.user

class Whois(models.Model):
	query = models.TextField(max_length=200)
	result = models.TextField(blank=True, null=True)
	md5 = models.CharField(max_length=200, blank=True, null=True)
	organization = models.TextField(max_length=2000, blank=True, null=True)
	country = models.TextField(max_length=20, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	email = models.ManyToManyField(Email)

class Dig(models.Model):
	query = models.TextField(max_length=200)
	result = models.TextField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

class IPAddress(models.Model):
	ip = models.GenericIPAddressField(unique=True)
        def __unicode__(self):
                return self.ip

class IP_Whois(models.Model):
	timestamp = models.DateTimeField(auto_now_add=True)
	ip = models.ForeignKey(IPAddress)
	whois = models.ForeignKey(Whois)

class Domain(models.Model):
	name = models.CharField(max_length=2000, unique=True)
	suffix = models.CharField(max_length=200, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
        def __unicode__(self):
                return self.name

class Domain_Dig(models.Model):
	timestamp = models.DateTimeField(auto_now_add=True)
	domain = models.ForeignKey(Domain)
	dig = models.ForeignKey(Dig)

class Domain_Whois(models.Model):
	timestamp = models.DateTimeField(auto_now_add=True)
	domain = models.ForeignKey(Domain)
	whois = models.ForeignKey(Whois)

class Hostname(models.Model):
	name = models.CharField(max_length=20000, unique=True)
	domain = models.ForeignKey(Domain, blank=True, null=True)
	subdomain = models.CharField(max_length=20000, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
        def __unicode__(self):
                return self.name

class Host_IP(models.Model):
	timestamp = models.DateTimeField(auto_now_add=True)
	hostname = models.ForeignKey(Hostname)
	ip = models.ForeignKey(IPAddress)

class Host_Dig(models.Model):
	timestamp = models.DateTimeField(auto_now_add=True)
	hostname = models.ForeignKey(Hostname)
	dig = models.ForeignKey(Dig)

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

class Analysis(models.Model):
	#object_id = models.CharField(max_length=200, blank=True, null=True)
	#url = models.ForeignKey(URL, blank=True, null=True)
	#content = models.ForeignKey(Content, blank=True, null=True)
	result = models.TextField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

class Content(models.Model):
	content = models.TextField(blank=True, null=True)
	md5 = models.CharField(max_length=200, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	path = models.FilePathField(path=os.path.abspath(os.path.dirname(__file__)))
	commit = models.CharField(max_length=200, blank=True, null=True)
	type = models.CharField(max_length=200, blank=True, null=True)
	length = models.PositiveIntegerField(blank=True, null=True)
	analysis = models.ForeignKey(Analysis, blank=True, null=True)

class Capture(models.Model):
	path = models.FilePathField(path=os.path.abspath(os.path.dirname(__file__)))
	commit = models.CharField(max_length=200, blank=True, null=True)
	#md5 = models.CharField(max_length=200, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	base64 = models.TextField(blank=True, null=True)
	b64thumb = models.TextField(blank=True, null=True)

#class Headers(models.Model):
#	serialized = models.TextField(blank=True, null=True)
#	created_at = models.DateTimeField(auto_now_add=True)

class Resource(models.Model):
	#url = models.URLField(max_length=20000)
	url = models.ForeignKey(URL, blank=True, null=True)
	#http_status = models.PositiveSmallIntegerField(blank=True, null=True)
	http_status = models.CharField(max_length=200, blank=True, null=True)
	headers = models.TextField(blank=True, null=True)
	#headers = models.ManyToManyField(Headers)
	#content = models.TextField(blank=True, null=True)
	content = models.ForeignKey(Content, blank=True, null=True)
	is_page = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	#job = models.ForeignKey(Job, blank=True, null=True)
	#job = models.ManyToManyField(Job)
	capture = models.ForeignKey(Capture, blank=True, null=True)
	#wappalyzer = models.ManyToManyField(Wappalyzer)


class Query(models.Model):
	input = models.URLField(max_length=20000)
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

class Job(models.Model):
	query = models.ForeignKey(Query)
	user_agent = models.ForeignKey(UserAgent, blank=True, null=True)
	referer = models.CharField(max_length=2000, blank=True, null=True)
	proxy = models.ForeignKey(URL, blank=True, null=True)
	additional_headers = models.TextField(blank=True, null=True)
	#http_method = models.CharField(max_length=10, choices=METHOD_CHOICES, default='GET')
	method = models.CharField(max_length=10, default='GET')
	post_data = models.TextField(blank=True, null=True)
	timeout = models.PositiveSmallIntegerField(choices=TIMEOUT_CHOICES, default=60)
	#progresss = models.CharField(max_length=2000, blank=True, null=True)
	status = models.CharField(max_length=2000, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	new = models.ManyToManyField(Resource, related_name="new")
	out = models.ManyToManyField(Resource, related_name="out")
	changed = models.ManyToManyField(Resource, related_name="changed")
	not_changed = models.ManyToManyField(Resource, related_name="not_changed")

class Job_Resource(models.Model):
	job = models.ForeignKey(Job)
	resource = models.ForeignKey(Resource)
	timestamp = models.DateTimeField(auto_now_add=True)
	seq = models.PositiveIntegerField(blank=True, null=True)
	
