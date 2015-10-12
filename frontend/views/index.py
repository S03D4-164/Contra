from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

from .auth import log_in
from ..forms import *
from ..models import *
from ..tasks.ghost_task import execute_job
from ..tasks.parse_task import parse_url
from progress import main as progress

import re, logging
from ..logger import getlogger
logger = getlogger()

@login_required
def _query_job(request, form, jobs):
	input = form.cleaned_data["input"]
	ua = form.cleaned_data["user_agent"]
	referer = form.cleaned_data["referer"]
	proxy = form.cleaned_data["proxy"]
	if proxy:
		proxy = parse_url(proxy)
	additional_headers = form.cleaned_data["additional_headers"]
	method = form.cleaned_data["method"]
	post_data = form.cleaned_data["post_data"]
	timeout = form.cleaned_data["timeout"]
	
	line = input.splitlines()
	for i in line:
		i.strip()
		if re.match("^(ht|f)tps?://[^/]+", i):
			#try:
			if True:
				q, created = Query.objects.get_or_create(
					input = i,
					registered_by=request.user,
				)
                        	job = Job.objects.create(
              	               		query = q,
                              		status = "Job Created",
					user_agent = ua,
					referer = referer,
					additional_headers = additional_headers,
					method = method,
					post_data = post_data,
					timeout = timeout,
              			)
				if proxy:
					job.proxy = proxy
					job.save()
          			execute_job.delay(job.id)
				jobs.append(job.id)
			#except Exception as e:
			#	messages.error(request, 'Error: ' + str(e))
		else:
			if i:
				messages.error(request, 'Invalid Input: ' + str(i))

	return request, jobs

def view(request):
	user = request.user
	form = QueryForm()
	if request.method == "POST":
		if "register" in request.POST:
			form = QueryForm(request.POST)
			jobs = []
			if form.is_valid():
				request, jobs = _query_job(request, form, jobs)
			rc = progress(request, jobs)
			return render_to_response("progress.html", rc) 
		elif "login" in request.POST:
			next = "/"
			try:
				next = request.GET.get("next")
			except Exception as e:
				logger.error(e)
			log_in(request, next)
		elif "create_ua" in request.POST:
			if request.user.is_authenticated:
				uaform = UserAgentForm(request.POST)
				if uaform.is_valid():
					name = uaform.cleaned_data["name"]
					strings = uaform.cleaned_data["strings"]
					ua, created = UserAgent.objects.get_or_create(
						name = name,
					)
					if ua and created:
						ua.strings = strings
						ua.save()
						messages.success(request, 'User Agent Created: ' + str(ua.name))
					elif ua and not created:
						messages.success(request, 'User Agent Already Exists: ' + str(ua.name))

	query = Query.objects.filter(restriction=2)
	if user.is_authenticated():
		query = Query.objects.filter(restriction=2) | Query.objects.filter(restriction=0)
		try:
			query = Query.objects.filter(restriction=2) \
				| Query.objects.filter(restriction=0) \
				| Query.objects.filter(registered_by__groups__in=user.groups.all())
		except:
			pass

	jr = Job_Resource.objects.filter(job__query__in=query)
	resource = []
	host_ip = []
	ip_whois = []
	domain_whois = []
	for r in jr:
		if r.resource and not r.resource in resource:
			resource.append(r.resource)
		if r.host_ip and not r.host_ip in host_ip:
			host_ip.append(r.host_ip)
		for i in r.ip_whois.all():
			if not i in ip_whois:
				ip_whois.append(i)
		if r.domain_whois and not r.domain_whois in domain_whois:
			domain_whois.append(r.domain_whois)

	rc = RequestContext(request, {
		'form': form,
		'authform': AuthenticationForm(),
		"redirect":request.path,
		'query': query,
		'job': Job.objects.filter(query=query),
		'page': Job_Resource.objects.filter(resource__is_page=True, job__query=query).distinct(),
		'resource': Job_Resource.objects.filter(resource__is_page=False, job__query=query).order_by("-pk").distinct()[0:100],
		'hostip':host_ip,
		'ip_whois':ip_whois,
		'domain_whois':domain_whois,
		#'domain': Domain.objects.all(),
		#'hostname': Hostname.objects.all(),
		'ua': UserAgent.objects.all(),
		'uaform': UserAgentForm(),
		#'jr': Job_Resource.objects.all(),
		#'analysis': Analysis.objects.all(),
		#'url': URL.objects.all(),
		#'capture': Capture.objects.all(),
	})
	return render_to_response("index.html", rc) 

