from django.shortcuts import render_to_response
from django.template import RequestContext

from ..forms import *
from ..models import *
from ..tasks.tasks import *
from progress import main as progress

import re, logging

def query_job(form, jobs):
	input = form.cleaned_data["input"]
	ua = form.cleaned_data["user_agent"]
	line = input.splitlines()
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
	return jobs

def view(request):
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.INFO)
	ch = logging.StreamHandler()
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	ch.setFormatter(formatter)
	logger.addHandler(ch)
	form = QueryForm()
	if request.method == "POST":
		if "register" in request.POST:
			form = QueryForm(request.POST)
			jobs = []
			if form.is_valid():
				jobs = query_job(form, jobs)
			rc = progress(request, jobs)
			return render_to_response("progress.html", rc) 
		elif "create_ua" in request.POST:
			uaform = UserAgentForm(request.POST)
			if uaform.is_valid():
				name = uaform.cleaned_data["name"]
				strings = uaform.cleaned_data["strings"]
				ua, created = UserAgent.objects.get_or_create(
					name = name,
					strings = strings,
				)

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
		'uaform': UserAgentForm(),
	})
	return render_to_response("index.html", rc) 

