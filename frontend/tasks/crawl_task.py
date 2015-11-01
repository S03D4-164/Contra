from ..models import *
from .job_task import execute_job

from ..logger import getlogger
import logging
logger = getlogger()

from ..celery import app

@app.task
def crawl(interval):
	query = Query.objects.filter(interval=interval)
	for q in query:
		j = Job.objects.filter(query=q).order_by("-pk")[0]
                job = Job.objects.create(
                	query = q,
                        status = "Job Created",
                        user_agent = j.user_agent,
                        referer = j.referer,
                        additional_headers = j.additional_headers,
                        method = j.method,
                        post_data = j.post_data,
                        timeout = j.timeout,
                )
                if j.proxy:
                	job.proxy = j.proxy
                	job.save()
                execute_job.delay(job.id)
		q.counter -= 1
		if q.counter <= 0:
			q.interval = 0
		q.save()

	
