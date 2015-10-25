from django.shortcuts import render_to_response
from django.template import RequestContext

from ..forms import *
from ..models import *
import re, logging

def view(request):
	rc = None
	if request.method == "GET":
		jobs = request.GET.getlist("job[]")
		if not jobs:
			jobs = request.GET.get("job")
		rc = main(request, jobs)
	return render_to_response("progress.html", rc)

	
def main(request, jobs):
	job = Job.objects.filter(pk__in=jobs).order_by("pk")
	jr = Job_Resource.objects.filter(job__in=job, resource__is_page=True).distinct().order_by("job__id")

	status = None
	for j in job:
		if re.search("(^Completed|^Error)", str(j.status)):
			pass
		else:
			status = "Processing"
	if status == None:
		status = "Finished"

	rc = RequestContext(request, {
		'form': QueryForm(),
		'job': job,
		'page': jr,
		'status': status,
	})
	return rc 

