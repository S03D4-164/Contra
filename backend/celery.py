from __future__ import absolute_import
from kombu import Queue, Exchange

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject.settings'

from celery import Celery
from datetime import timedelta

app = Celery(
    'Contra.backend',
    broker='redis://',
    backend='redis://',
    include=[
        'Contra.backend.apis.dns_resolve',
        'Contra.backend.apis.whois_domain',
        'Contra.backend.apis.whois_ip',
    ],
    )

app.conf.update(
    CELERY_DEFAULT_QUEUE = 'backend',
    CELERY_QUEUES = (
        Queue('backend', Exchange('backend'), routing_key='backend'),
    ),
    #CELERY_IGNORE_RESULT = True,
    CELERY_TASK_RESULT_EXPIRES = 600,
    CELERY_MAX_CACHED_RESULTS = -1,
    CELERYD_TASK_TIME_LIMIT = 600,
    CELERY_ACCEPT_CONTENT = ['json', 'pickle'],
    CELERY_TASK_SERIALIZER = 'pickle',
    CELERY_RESULT_SERIALIZER = 'pickle',
)

if __name__ == '__main__':
    app.start()

