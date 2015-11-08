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
       	im.thumbnail((480,270))
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
	analysis = None
	try:
		analysis = Analysis.objects.get(content=content)
	except Exception as e:
		logger.error(e)

	if request.method == "POST":
		logger.debug(request.POST)
		if "analysis" in request.POST:
			result = content_analysis(content.id)
			if result:
				analysis = Analysis.objects.filter(content=content)
				for a in analysis:
					a.delete()
				analysis, created = Analysis.objects.get_or_create(
					content = content,
					result = result
				)
				if analysis:
					page.analysis = analysis
		elif "wappalyze" in request.POST:
			result = wappalyze(info.id)
			logger.debug(result)
	thumbnail = None
	#if job.capture:
	#	thumbnail = create_b64thumb(appdir + "/" + page.capture.path)

	matched = []
	tags = []
	rule = []
	behavior = None
	if analysis:
		results = None
		try:
			results = json.loads(analysis.result)
		except Exception as e:
			logger.error(e)
		if results:
			behavior = results["behavior"]
			for b in behavior:
				desc = None
				try:
					desc = ast.literal_eval(b["description"])
				except:
					pass
				if desc:
					strings = desc["strings"]
					for s in strings:
						if not s["data"] in matched:
							matched.append(s["data"])
					if not desc["tags"][0] in tags:
						tags.append(desc["tags"][0])
					if not desc["rule"] in rule:
						rule.append(desc["rule"])

	headers = None
	if resource.headers:
		headers = ast.literal_eval(resource.headers)
	print resource.host_info.id
	c = RequestContext(request, {
		'resource': resource,
		'size':os.path.getsize(appdir + "/" + content.path),
		'job': j,
		'analysis':analysis,
		'behavior': behavior,
		'rule':rule,
		'tags':tags,
		'matched':matched,
		#'capture': capture,
		'thumbnail':thumbnail,
		'headers': headers,
		'form':QueryForm(),
                'authform': AuthenticationForm(),
                'redirect': request.path,
	})
	return render_to_response("page.html", c) 

