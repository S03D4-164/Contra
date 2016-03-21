from __future__ import absolute_import
from kombu import Queue, Exchange

import os
try:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject.settings'
except:
    pass

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
        'Contra.backend.tasks.docker_tasks',
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
    CELERY_MAX_TASKS_PER_CHILD = 1,
    CELERYD_TASK_TIME_LIMIT = 600,
    CELERY_ACCEPT_CONTENT = ['json', 'pickle'],
    CELERY_TASK_SERIALIZER = 'pickle',
    CELERY_RESULT_SERIALIZER = 'pickle',
    CELERYBEAT_SCHEDULE = {
        '1h': {
            'task': 'Contra.backend.tasks.docker_tasks.container_killer',
            'schedule': timedelta(seconds=3600),
            'args': [3600]  
        },
    },
)

if __name__ == '__main__':
    app.start()

