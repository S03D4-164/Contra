from __future__ import absolute_import

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject2.settings'

from celery import Celery
from datetime import timedelta

app = Celery(
	'frontend',
	broker='redis://',
        backend='redis://',
        include=[
		'frontend.tasks.ghost_task',
		'frontend.tasks.crawl_task',
		'frontend.tasks.iplookup',
		'frontend.tasks.whois_domain',
		'frontend.tasks.whois_ip',
	])

app.conf.update(
	CELERY_MAX_CACHED_RESULTS = 0,
	CELERYBEAT_SCHEDULE = {
		'1h': {
			'task': 'frontend.tasks.crawl_task.crawl',
			'schedule': timedelta(seconds=3600),
			'args': [3600]
		},
	},
)

if __name__ == '__main__':
    app.start()

