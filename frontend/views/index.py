from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction

from ..forms import *
from ..models import *
#from ..tasks.ghost_task import execute_job
from ..tasks.job_task import execute_job
from ..tasks.whois_domain import whois_domain
from ..tasks.whois_ip import whois_ip
from ..tasks.dns_resolve import dns_resolve
from ..tasks.host_inspect import host_inspect
from .auth import log_in
from .progress import main as progress

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
			try:
				job = None
				with transaction.atomic():
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
				if job:
	          			execute_job.delay(job.id)
	          			#execute_job(job.id)
					jobs.append(job.id)
			except Exception as e:
				messages.error(request, 'Error: ' + str(e))
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
						name = name.strip(),
					)
					if ua and created:
						ua.strings = strings.strip()
						ua.save()
						messages.success(request, 'User Agent Created: ' + str(ua.name))
					elif ua and not created:
						messages.success(request, 'User Agent Already Exists: ' + str(ua.name))
		elif "dns_resolve" in request.POST:
			iform = InputForm(request.POST)
			if iform.is_valid():
				input = iform.cleaned_data["input"]
				#res = dns_resolve.delay(input.strip())
				#d = res.get()
				d = dns_resolve(input.strip())
				if d:
					return redirect("/dns/" + str(d.id))
		elif "whois_domain" in request.POST:
			iform = InputForm(request.POST)
			if iform.is_valid():
				input = iform.cleaned_data["input"]
				#res = whois_domain.delay(input.strip())
				#wd = res.get()
				wd = whois_domain(input.strip())
				if wd:
					return redirect("/whois_domain/" + str(wd.id))
				else:
					messages.warning(request, 'No Result.')
		elif "whois_ip" in request.POST:
			iform = InputForm(request.POST)
			if iform.is_valid():
				input = iform.cleaned_data["input"]
				#res = whois_ip.delay(input.strip())
				#wi = res.get()
				wi = whois_ip(input.strip())
				if wi:
					return redirect("/whois_ip/" + str(wi.id))
		elif "host_inspect" in request.POST:
			iform = InputForm(request.POST)
			if iform.is_valid():
				input = iform.cleaned_data["input"]
				hi = host_inspect(input.strip())
	query = Query.objects.filter(restriction=2)
	if user.is_authenticated():
		query = Query.objects.filter(restriction=2) | Query.objects.filter(restriction=0)
		try:
			query = Query.objects.filter(restriction=2) \
				| Query.objects.filter(restriction=0) \
				| Query.objects.filter(registered_by__groups__in=user.groups.all())
		except:
			pass

	rc = RequestContext(request, {
		'form': form,
		'authform': AuthenticationForm(),
		"redirect":request.path,
		'query': query,
		'job': Job.objects.filter(query=query),
		#'domain': Domain.objects.all(),
		#'hostname': Hostname.objects.all(),
		'ua': UserAgent.objects.all(),
		'uaform': UserAgentForm(),
		'iform': InputForm(),
		'dns':DNSRecord.objects.all(),
		'whois_domain':Domain_Whois.objects.all(),
		'whois_ip':IP_Whois.objects.all(),
		'host_info':Host_Info.objects.all(),
		#'analysis': Analysis.objects.all(),
	})
	return render_to_response("index.html", rc) 

