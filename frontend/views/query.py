from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from ..forms import *
from ..models import *
from ..tasks.ghost_task import *
from progress import main as progress

import requests, pickle, gzip, hashlib, chardet, base64
from sh import git
from StringIO import StringIO

def view(request, id):
	query = Query.objects.get(pk=id)
	job = Job.objects.filter(query=query)
	jr = Job_Resource.objects.filter(job__in=job, resource__is_page=True).distinct()
	page = []
	for j in jr.all():
		page.append(j.resource)
	#page = Resource.objects.filter(id__in=jr.resource.all())
	if request.method == "POST":
		if "run" in request.POST:
			job = Job.objects.create(
				query = query,
				status = "Created",
			)
			execute_job.delay(job.id)
                        rc = progress(request, [job.id])
                        return render_to_response("progress.html", rc) 
		elif "delete" in request.POST:
			query.delete()
			return redirect("/")
	c = RequestContext(request, {
		'form': QueryForm(),
		'q': query,
		'job': job,
		'page': page,
		#'job': Job.objects.filter(query=query),
		#'page': Resource.objects.filter(job__query=query, is_page=True),
	})
	return render_to_response("query.html", c) 

