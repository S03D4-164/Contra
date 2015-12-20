from django.core.mail import send_mail
from django.contrib.auth.models import User 
from ..models import *

def alert(job_id):
    job = Job.objects.get(id=job_id)
    user = job.query.registered_by
    #users = User.objects.filter(groups__in=user.groups.all)
    subject = "Contra"
    message = ""
    mail_from = "contra@localhost"
    mail_to = [user]
    send_mail(subject, message, mail_from, mail_to)
