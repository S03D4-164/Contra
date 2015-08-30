from django.shortcuts import render_to_response
from django.template import RequestContext

from ..forms import *
from ..models import *
from ..tasks.tasks import *
from progress import main as progress

import re, logging

def view(request):
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.INFO)
	ch = logging.StreamHandler()
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	ch.setFormatter(formatter)
	logger.addHandler(ch)
	form = QueryForm()
	if request.method == "POST":
		form = QueryForm(request.POST)
		if form.is_valid():
			input = form.cleaned_data["input"]
			ua = form.cleaned_data["user_agent"]
			line = input.splitlines()
			jobs = []
			for i in line:
				i.strip()
				if re.match("^(ht|f)tps?://[^/]+", i):
					try:
						q, created = Query.objects.get_or_create(
							input = i,
						)
		                        	job = Job.objects.create(
                	                		query = q,
                        	        		status = "Created",
							user_agent = ua,
                        			)
                      	  			execute_job.delay(job.id)
						jobs.append(job.id)
					except Exception as e:
						logger.error(e)
			rc = progress(request, jobs)
			#rc = RequestContext(request, {
			#	'jobs': jobs,
			#})
			return render_to_response("progress.html", rc) 

	rc = RequestContext(request, {
		'form': form,
		'query': Query.objects.all(),
		'job': Job.objects.all(),
		'page': Resource.objects.filter(is_page=True),
		'resource': Resource.objects.filter(is_page=False),
		'domain': Domain.objects.all(),
		'hostname': Hostname.objects.all(),
		'url': URL.objects.all(),
		#'capture': Capture.objects.all(),
		'ua': UserAgent.objects.all(),
	})
	return render_to_response("index.html", rc) 

