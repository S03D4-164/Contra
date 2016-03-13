from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from ..forms import *
from ..models import *
from ..tasks.thug_task import content_analysis
from ..tasks.wappalyze import wappalyze
from ..tasks.repository import git_diff, git_log
from .auth import check_permission

import ast, base64, json
from difflib import unified_diff
from pprint import pprint

import logging
from ..logger import getlogger
logger = getlogger()

appdir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)


def view(request, id):
    content = Content.objects.get(id=id)
    user = request.user

    j = Job.objects.filter(page__content=content).distinct().order_by("-id") \
        | Job.objects.filter(resources__content=content).distinct().order_by("-id")

    for i in j:
        check_permission(request, i.query.id)
    
    c = {
        'content': content,
        #'size':size,
        'job': j,
    }
    return render(request, "content.html", c) 

