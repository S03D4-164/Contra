from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from ..forms import *
from ..models import *
from .auth import check_permission

def view(request, id):
    dns = DNSRecord.objects.get(pk=id)

    #c = RequestContext(request, {
    c = {
        'form': QueryForm(),
        'authform': AuthenticationForm(),
        'redirect': request.path,
        'dns': dns,
    }
    return render(request, "dns.html", c)

