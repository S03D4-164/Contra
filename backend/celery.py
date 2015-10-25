from __future__ import absolute_import
from kombu import Queue, Exchange

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject2.settings'

from celery import Celery
from datetime import timedelta

app = Celery(
	'backend',
	broker='redis://',
        backend='redis://',
        include=[
		'backend.apis.run_ghost',
		#'backend.apis.dns_resolve',
		#'backend.apis.whois_domain',
		#'backend.apis.whois_ip',
	])

app.conf.update(
	CELERY_DEFAULT_QUEUE = 'backend',
	CELERY_QUEUES = (
	    Queue('backend', Exchange('backend'), routing_key='backend'),
	),
	#CELERY_IGNORE_RESULT = True,
	CELERY_TASK_RESULT_EXPIRES = 600,
	CELERY_MAX_CACHED_RESULTS = -1,
	CELERYD_TASK_TIME_LIMIT = 600,
)

if __name__ == '__main__':
    app.start()

