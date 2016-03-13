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
    resource = Resource.objects.get(id=id)
    user = request.user

    j = None
    if resource.is_page:
        j = Job.objects.filter(page=resource).distinct().order_by("-id")
    else:
        j = Job.objects.filter(resources=resource).distinct().order_by("-id")

    for i in j:
        check_permission(request, i.query.id)
    #if not j.filter(query__registered_by=user):
    #    messages.error(request, "Cannot access Resource " + str(resource.id))
    #    return redirect("/")

    content = resource.content
    analysis = resource.analysis

    if request.method == "POST":
        if "analysis" in request.POST:
            aid = content_analysis(content.id)
            try:
                analysis = Analysis.objects.get(pk=aid)
                resource.analysis = analysis
                resource.save()
            except Exception as e:
                logger.error(str(e))
        elif "wappalyze" in request.POST:
            result = wappalyze(info.id)
            logger.debug(result)

    matched = []
    result = None
    if analysis:
        result = analysis.result
        if result:
            yara = {}
            try:
                r = json.loads(result)
                yara = r["yara_matched"]
            except Exception as e:
                logger.error(e)
            for y in yara:
                desc = ast.literal_eval(y["description"])
                if desc:
                    strings = desc["strings"]
                    for s in strings:
                        if not s in matched:
                            matched.append(s)

    headers = None
    if resource.headers:
        headers = ast.literal_eval(resource.headers)

    diff = ""
    c = git_log(content.path, content.commit)
    c = c.split("\n")
    if len(c) == 2:
        a = Content.objects.get(commit=c[0])
        b = Content.objects.get(commit=c[1])
        for i in unified_diff(b.content.split("\n"),a.content.split("\n")):
            diff += i + "\n"
    elif len(c) == 1:
        a = Content.objects.get(commit=c[0])
        for i in unified_diff([], a.content.split("\n")):
            diff += i + "\n"
        
    """
    diff = None
    try:
        diff = git_diff(content.path, content.commit).encode("utf-8")
    except:
        pass
    """
    
    c = {
        'resource': resource,
        #'size':size,
        'job': j,
        'analysis':analysis,
        'result': result,
        'diff': diff,
        'matched':matched,
        'headers': headers,
        'form':QueryForm(),
        'authform': AuthenticationForm(),
        'redirect': request.path,
    }
    return render(request, "page.html", c) 

