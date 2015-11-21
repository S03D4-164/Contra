from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from ..forms import *
from ..models import *
from .auth import check_permission

def view(request, id):
    w = Domain_Whois.objects.get(pk=id)

    c = RequestContext(request, {
        'form': QueryForm(),
        'authform': AuthenticationForm(),
        'redirect': request.path,
        'wd': w,
    })
    return render_to_response("whois_domain.html", c) 

