from django.shortcuts import render_to_response
from django.template import RequestContext

from ..forms import *
from ..models import *
from ..tasks.tasks import *
import re, logging

def view(request):
	rc = None
	if request.method == "GET":
		print request.GET
		jobs = request.GET.getlist("job[]")
		if not jobs:
			jobs = request.GET.get("job")
		print jobs
		rc = main(request, jobs)
	return render_to_response("progress.html", rc)

	
def main(request, jobs):
	job = Job.objects.filter(pk__in=jobs)
	page = Resource.objects.filter(job__in=job, is_page=True)
	status = None
	for j in job:
		print j.status
		if re.search("(^Completed|^Error)", str(j.status)):
			pass
		else:
			status = "Processing"
	if status == None:
		status = "Finished"
	print status

	rc = RequestContext(request, {
		'job': job,
		'page': page,
		'status': status,
	})
	return rc 

