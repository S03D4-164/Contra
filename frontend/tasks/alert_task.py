from ..celery import app

from django.core.mail import send_mail
from django.contrib.auth.models import User 
from ..models import *

import logging
from ..logger import getlogger
logger = getlogger(logging.DEBUG)


def set_signature(resource, signature):
    if resource.analysis:
        if resource.analysis.rule.all():
            for a in resource.analysis.rule.all():
                if not a.name in signature:
                    signature[a.name] = [resource.url.url]
                elif a.name in signature:
                    if not resource.url.url in signature[a.name]:
                        signature[a.name].append(resource.url.url)
    return signature

@app.task(soft_time_limit=60)
def job_alert(job_id):
    job = Job.objects.get(id=job_id)

    subject = job.query.input
    message = ""
    user = job.query.registered_by.username
    #users = User.objects.filter(groups__in=user.groups.all)
    mail_from = "contra@localhost"
    mail_to = [user]

    signature = {}
    if job.page:
        signature = set_signature(job.page, signature)
    if job.resources.all():
        for r in job.resources.all():
            signature = set_signature(r, signature)

    changed = []
    for c in job.changed.all():
        if not c.url.url in changed:
            changed.append(c.url.url)

    if signature:
        subject = "[Alert] " + str(len(signature)) + " signature found: " + subject
        for s in signature:
            message += "signature: " + s + "\n"
            for url in signature[s]:
                message += url + "\n"
        message += "\n----------\n"
        
    elif changed:
        subject = "[Info] " + str(len(changed)) + " resource changed: " + subject
    if changed:
        message += "changed:\n"
        for c in changed:
            message += c + "\n"
            
    if message:
        logger.debug(subject)
        logger.debug(message)
        try:
            send_mail(subject, message, mail_from, mail_to)
        except Exception as e:
            logger.error(str(e))
    return job
