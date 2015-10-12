from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib import messages

from ..forms import *
from ..models import *
from ..tasks.ghost_task import *
from .auth import check_permission 

import requests, pickle, gzip, hashlib, chardet, base64
from sh import git
from StringIO import StringIO

def view(request, id):
	job = Job.objects.get(pk=id)

	if not check_permission(request, job.query.id):
                messages.error(request, "Cannot access Job " + str(job.id))
                return redirect("/")

	jrs = Job_Resource_Seq.objects.filter(job_resource__job=job)
	page = None
	try:
		#page = Resource.objects.get(job=job, is_page=True)
		p = jrs.get(job_resource__resource__is_page=True)
		page = p.job_resource
		#page = p.resource
	except:
		pass
	resource = jrs.filter(job_resource__resource__is_page=False).order_by("seq")
	if request.method == "POST":
		if "run" in request.POST:
			j = Job.objects.create(
				query = job.query,
				status = "Created",
			)
			execute_job(j.id)

	c = RequestContext(request, {
		'form': QueryForm(),
		'q': job.query,
		'j': job,
		'p': page,
		'resource': resource,
	})
	return render_to_response("job.html", c) 

