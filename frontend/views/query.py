from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from ..forms import *
from ..models import *
from ..tasks.ghost_task import *
from progress import main as progress

import requests, pickle, gzip, hashlib, chardet, base64
from sh import git
from StringIO import StringIO

def _query_job(query, form):
        ua = form.cleaned_data["user_agent"]
        referer = form.cleaned_data["referer"]
        proxy = form.cleaned_data["proxy"]
        if proxy:
                proxy = parse_url(proxy)
        additional_headers = form.cleaned_data["additional_headers"]
        method = form.cleaned_data["method"]
        post_data = form.cleaned_data["post_data"]
        timeout = form.cleaned_data["timeout"]
	job = Job.objects.create(
		query = query,
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
	return job

def view(request, id):
	query = Query.objects.get(pk=id)
	job = Job.objects.filter(query=query)
	page = Job_Resource.objects.filter(job__in=job, resource__is_page=True).distinct()
	"""
	page = []
	for j in jr.all():
		if not j.resource in page:
			page.append(j.resource)
	#page = Resource.objects.filter(id__in=jr.resource.all())
	"""
	cform = CrawlForm(instance=query)
	if request.method == "POST":
		if "run" in request.POST:
			form = QueryRunForm(request.POST)
			if form.is_valid():
				j = _query_job(query, form)
				execute_job.delay(j.id)
                        	rc = progress(request, [j.id])
                        	return render_to_response("progress.html", rc) 
		elif "delete" in request.POST:
			query.delete()
			return redirect("/")
		elif "update" in request.POST:
			cform = CrawlForm(request.POST)
			if cform.is_valid():
				interval = cform.cleaned_data["interval"]
				counter = cform.cleaned_data["counter"]
				query.interval = interval
				query.counter = counter
				query.save()
				
	c = RequestContext(request, {
		'form': QueryForm(),
		'qrform': QueryRunForm(),
		'q': query,
		'job': job,
		'page': page,
		'cform': cform,
		#'job': Job.objects.filter(query=query),
		#'page': Resource.objects.filter(job__query=query, is_page=True),
	})
	return render_to_response("query.html", c) 

