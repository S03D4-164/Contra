from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from ..forms import *
from ..models import *

import ast, base64
from StringIO import StringIO
from PIL import Image, ImageOps

appdir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
)

def create_b64thumb(image):
	thumb = None
	#s = StringIO()
	#s.write(image)
        #im = Image.open(s)
        im = Image.open(image)
       	im.thumbnail((640,480))
	tmp = StringIO()
        im.save(tmp, format="PNG")
	thumb = base64.b64encode(tmp.getvalue())
	return thumb

def view(request, id):
	page= Resource.objects.get(pk=id)
	#capture = base64.b64decode(page.capture.base64)
	#thumbnail = create_b64thumb(capture)
	thumbnail = create_b64thumb(appdir + "/" + page.capture.path)

	headers = ast.literal_eval(page.headers)
	c = RequestContext(request, {
		'p': page,
		'capture': page.capture,
		'thumbnail':thumbnail,
		'headers': headers,
		'form':QueryForm(),
	})
	return render_to_response("page.html", c) 

