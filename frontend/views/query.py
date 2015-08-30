from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from ..forms import *
from ..models import *
from ..tasks.tasks import *

import requests, pickle, gzip, hashlib, chardet, base64
from sh import git
from StringIO import StringIO

def view(request, id):
	query = Query.objects.get(pk=id)
	if request.method == "POST":
		if "run" in request.POST:
			job = Job.objects.create(
				query = query,
				status = "Created",
			)
			execute_job(job.id)
		elif "delete" in request.POST:
			query.delete()
			return redirect("/")
	c = RequestContext(request, {
		'form': QueryForm(),
		'q': query,
		'job': Job.objects.filter(query=query),
		'page': Resource.objects.filter(job__query=query, is_page=True),
	})
	return render_to_response("query.html", c) 

