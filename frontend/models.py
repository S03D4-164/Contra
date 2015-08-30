from django.db import models

import os

class UserAgent(models.Model):
	name = models.CharField(max_length=200)
	strings = models.CharField(max_length=200)
	created_at = models.DateTimeField(auto_now_add=True)
        def __unicode__(self):
                return self.name

class Query(models.Model):
	input = models.URLField(max_length=20000)
	created_at = models.DateTimeField(auto_now_add=True)
        def __unicode__(self):
                return self.input

class Job(models.Model):
	query = models.ForeignKey(Query)
	user_agent = models.ForeignKey(UserAgent, blank=True, null=True)
	status = models.CharField(max_length=2000, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	modified_at = models.DateTimeField(auto_now=True)

class Domain(models.Model):
	name = models.CharField(max_length=2000, unique=True)
	tld = models.CharField(max_length=200, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
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
	url = models.URLField(max_length=2000, unique=True)
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

class Content(models.Model):
	content = models.TextField(blank=True, null=True)
	md5 = models.CharField(max_length=200, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	path = models.FilePathField(path=os.path.abspath(os.path.dirname(__file__)))
	commit = models.CharField(max_length=200, blank=True, null=True)

class Capture(models.Model):
	path = models.FilePathField(path=os.path.abspath(os.path.dirname(__file__)))
	commit = models.CharField(max_length=200, blank=True, null=True)
	md5 = models.CharField(max_length=200, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	base64 = models.TextField(blank=True, null=True)
	b64thumb = models.TextField(blank=True, null=True)

class Resource(models.Model):
	#url = models.URLField(max_length=20000)
	url = models.ForeignKey(URL, blank=True, null=True)
	http_status = models.PositiveSmallIntegerField(blank=True, null=True)
	headers = models.TextField(blank=True, null=True)
	#content = models.TextField(blank=True, null=True)
	content = models.ForeignKey(Content, blank=True, null=True)
	is_page = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	job = models.ForeignKey(Job, blank=True, null=True)
	capture = models.ForeignKey(Capture, blank=True, null=True)

