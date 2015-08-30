from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from ..forms import *
from ..models import *
from ..tasks.tasks import *

import requests, pickle, gzip, hashlib, chardet, base64
from sh import git
from StringIO import StringIO

def view(request, id):
	job = Job.objects.get(pk=id)
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
		'p': Resource.objects.get(job=job, is_page=True),
		'resource': Resource.objects.filter(job=job, is_page=False),
	})
	return render_to_response("job.html", c) 

