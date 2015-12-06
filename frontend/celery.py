from __future__ import absolute_import
from kombu import Queue, Exchange

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject.settings'

from celery import Celery
from datetime import timedelta

app = Celery(
    'Contra.frontend',
    broker='redis://',
    backend='redis://',
    include=[
        'Contra.frontend.tasks.crawl_task',
    ])

app.conf.update(
    CELERY_DEFAULT_QUEUE = 'frontend',
    CELERY_QUEUES = (
        Queue('frontend', Exchange('frontend'), routing_key='frontend'),
    ),
    CELERY_IGNORE_RESULT = True,
    CELERY_TASK_RESULT_EXPIRES = 600,
    CELERY_MAX_CACHED_RESULTS = -1,
    CELERYD_TASK_TIME_LIMIT = 600,
    CELERYBEAT_SCHEDULE = {
        '1h': {
            'task': 'Contra.frontend.tasks.crawl_task.crawl',
            'schedule': timedelta(seconds=3600),
            'args': [3600]
        },
    },
    CELERY_ACCEPT_CONTENT = ['json', 'pickle'],
    CELERY_TASK_SERIALIZER = 'pickle',
    CELERY_RESULT_SERIALIZER = 'pickle',
)

if __name__ == '__main__':
    app.start()

