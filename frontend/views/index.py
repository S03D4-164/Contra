from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages

from ..forms import *
from ..models import *
from ..tasks.ghost_task import execute_job
from ..tasks.parse_task import parse_url
from progress import main as progress

from ..logger import getlogger
import re, logging
logger = getlogger()

def query_job(request, form, jobs):
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
				)
                        	job = Job.objects.create(
              	               		query = q,
                              		status = "Job Created",
					user_agent = ua,
					referer = referer,
					#proxy = proxy,
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
	form = QueryForm()
	if request.method == "POST":
		if "register" in request.POST:
			form = QueryForm(request.POST)
			jobs = []
			if form.is_valid():
				request, jobs = query_job(request, form, jobs)
			rc = progress(request, jobs)
			return render_to_response("progress.html", rc) 
		elif "create_ua" in request.POST:
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
					messages.success(request, 'UA created: ' + str(ua.name))
				elif ua and not created:
					messages.success(request, 'UA already exists: ' + str(ua.name))

	rc = RequestContext(request, {
		'form': form,
		'query': Query.objects.all(),
		'job': Job.objects.all(),
		'page': Resource.objects.filter(is_page=True),
		'resource': Resource.objects.filter(is_page=False),
		'domain': Domain.objects.all(),
		'hostname': Hostname.objects.all(),
		#'url': URL.objects.all(),
		#'capture': Capture.objects.all(),
		'ua': UserAgent.objects.all(),
		'uaform': UserAgentForm(),
		#'jr': Job_Resource.objects.all(),
		#'analysis': Analysis.objects.all(),
	})
	return render_to_response("index.html", rc) 

