from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from ..forms import *
from ..models import *
from .auth import check_permission

def view(request, id):
    w = IP_Whois.objects.get(pk=id)

    c = {
        'form': QueryForm(),
        'authform': AuthenticationForm(),
        'redirect': request.path,
        'wi': w,
    }
    return render(request, "whois_ip.html", c) 

