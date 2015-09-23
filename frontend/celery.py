from __future__ import absolute_import

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject2.settings'

from celery import Celery

app = Celery('frontend',
             broker='redis://',
             backend='redis://',
             include=['frontend.tasks.ghost_task'])

# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
)

if __name__ == '__main__':
    app.start()

