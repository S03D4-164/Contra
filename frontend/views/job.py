from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib import messages

from ..forms import *
from ..models import *
from ..tasks.ghost_task import *
from .auth import check_permission 


def view(request, id):
	job = Job.objects.get(pk=id)

	if not check_permission(request, job.query.id):
                messages.warning(request, "Cannot access Job " + str(job.id))
                return redirect("/")

	jrs = Job_Resource_Seq.objects.filter(job_resource__job=job)
	page = None
	try:
		p = jrs.get(job_resource__resource__is_page=True)
		page = p.job_resource
	except:
		pass
	resource = jrs.filter(job_resource__resource__is_page=False).order_by("seq")
	if request.method == "POST":
		if "run" in request.POST:
			j = Job.objects.create(
				query = job.query,
				status = "Job Created",
				user_agent = job.ua,
				referer = job.referer,
				additional_headers = job.additional_headers,
				method = job.method,
				post_data = job.post_data,
				timeout = job.timeout,
				proxy = job.proxy
			)
			execute_job.delay(j.id)
			rc = progress(request, [j.id])
			return render_to_response("progress.html", rc)

	c = RequestContext(request, {
		'form': QueryForm(),
		'q': job.query,
		'j': job,
		'p': page,
		'resource': resource,
		'redirect': request.path,
	})
	return render_to_response("job.html", c) 

