from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from ..forms import *
from ..models import *

import ast

def view(request, id):
	page= Resource.objects.get(pk=id)
	headers = ast.literal_eval(page.headers)
	c = RequestContext(request, {
		'p': page,
		'capture': page.capture,
		'headers': headers,
	})
	return render_to_response("page.html", c) 

