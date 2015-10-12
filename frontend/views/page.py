from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from ..forms import *
from ..models import *
from ..tasks.thug_task import content_analysis
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
	tmp = StringIO()
        im.save(tmp, format="PNG")
	thumb = base64.b64encode(tmp.getvalue())
	return thumb

def view(request, id):
	page= Resource.objects.get(pk=id)

	jp = Job_Resource.objects.get(resource=page)
        if not check_permission(request, jp.job.query.id):
                messages.error(request, "Cannot access Page " + str(page.id))
                return redirect("/")

	jr = Job_Resource.objects.filter(resource=page)

	analysis = None
	try:
		analysis = Analysis.objects.get(content=page.content)
	except Exception as e:
		logger.error(e)
	if request.method == "POST":
		logger.debug(request.POST)
		if "analysis" in request.POST:
			result = content_analysis(page.id)
			if result:
				analysis = Analysis.objects.filter(content=page.content)
				for a in analysis:
					a.delete()
				analysis, created = Analysis.objects.get_or_create(
					content = page.content,
					result = result
				)
				if analysis:
					page.analysis = analysis
	thumbnail = None
	if page.capture:
		thumbnail = create_b64thumb(appdir + "/" + page.capture.path)

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

	headers = ast.literal_eval(page.headers)
	c = RequestContext(request, {
		'p': page,
		'size':os.path.getsize(appdir + "/" + page.content.path),
		'job': jr,
		'analysis':analysis,
		'behavior': behavior,
		'rule':rule,
		'tags':tags,
		'matched':matched,
		'capture': page.capture,
		'thumbnail':thumbnail,
		'headers': headers,
		'form':QueryForm(),
                'authform': AuthenticationForm(),
                'redirect': request.path,
	})
	return render_to_response("page.html", c) 

