from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from ..forms import *
from ..models import *
from ..tasks.thug_task import content_analysis
from ..tasks.wappalyze import wappalyze
from .auth import check_permission

import ast, base64, json
from StringIO import StringIO
from PIL import Image, ImageOps
from pprint import pprint

import logging
from ..logger import getlogger
logger = getlogger()

appdir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

def create_b64thumb(image):
    thumb = None
    im = Image.open(image)
    im.thumbnail((400,300))
    #im = ImageOps.fit(im, (480,270), centering=(0.0, 0.0))
    tmp = StringIO()
    im.save(tmp, format="PNG")
    thumb = base64.b64encode(tmp.getvalue())
    return thumb

def view(request, id):
    resource = Resource.objects.get(id=id)
    user = request.user

    j = None
    if resource.is_page:
        j = Job.objects.filter(page=resource).distinct().order_by("-id")
    else:
        j = Job.objects.filter(resources=resource).distinct().order_by("-id")

    if not j.filter(query__registered_by=user):
        messages.error(request, "Cannot access Resource " + str(resource.id))
        return redirect("/")

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

    thumbnail = None
    #if job.capture:
    #    thumbnail = create_b64thumb(appdir + "/" + page.capture.path)

    matched = []
    result = None
    if analysis:
        try:
            result = ast.literal_eval(analysis.result)
        except Exception as e:
            logger.error(e)
        if result:
            yara = result["yara_matched"]
            for y in yara:
                desc = None
                try:
                    desc = ast.literal_eval(y["description"])
                except:
                    pass
                if desc:
                    strings = desc["strings"]
                    for s in strings:
                        if not s["data"] in matched:
                            matched.append(s["data"])

    headers = None
    if resource.headers:
        headers = ast.literal_eval(resource.headers)

    size = None
    if content:
        size = os.path.getsize(appdir + "/" + content.path),
        
    c = RequestContext(request, {
        'resource': resource,
        'size':size,
        'job': j,
        'analysis':analysis,
        'result': result,
        'matched':matched,
        #'capture': capture,
        'thumbnail':thumbnail,
        'headers': headers,
        'form':QueryForm(),
        'authform': AuthenticationForm(),
        'redirect': request.path,
    })
    return render_to_response("page.html", c) 

