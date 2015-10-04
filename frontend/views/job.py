from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from ..forms import *
from ..models import *
from ..tasks.ghost_task import *

import requests, pickle, gzip, hashlib, chardet, base64
from sh import git
from StringIO import StringIO

def view(request, id):
	job = Job.objects.get(pk=id)
	jr = Job_Resource.objects.filter(job=job)
	page = None
	try:
		#page = Resource.objects.get(job=job, is_page=True)
		p = jr.get(resource__is_page=True)
		#page = p.resource
	except:
		pass
	#resource = []
	#for r in jr.filter(resource__is_page=False).order_by("seq"):
	#	resource.append(r)
	resource = jr.filter(resource__is_page=False).order_by("seq")
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
		'p': p,
		'resource': resource,
	})
	return render_to_response("job.html", c) 

