from ..celery import app

from django.core.mail import send_mail
from django.contrib.auth.models import User 
from ..models import *

import logging
from ..logger import getlogger
logger = getlogger(logging.DEBUG)

@app.task
def job_alert(job_id):
    job = Job.objects.get(id=job_id)

    subject = job.query.input
    message = ""
    user = job.query.registered_by.username
    #users = User.objects.filter(groups__in=user.groups.all)
    mail_from = "contra@localhost"
    mail_to = [user]
    
    if job.page:
        if job.page.analysis:
            if job.page.analysis.rule.all:
                message += job.page.url.url + "\n"
                for a in job.page.analysis.rule.all():
                    message += a.name + "\n"
                message += "----------\n"
    if job.resources.all():
        for r in job.resources.all():
            if r.analysis.rule.all():
                message += r.url.url + "\n"
                for a in r.analysis.rule.all():
                    message += a.name + "\n"
                message += "----------\n"
    if message:
        subject = "[Alert]" + subject
        print(subject)
        print(message)
        print(mail_from)
        print(mail_to)
        try:
            send_mail(subject, message, mail_from, mail_to)
        except Exception as e:
            logger.error(str(e))
