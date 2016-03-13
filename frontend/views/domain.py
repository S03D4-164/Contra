from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from ..forms import *
from ..models import *
#from .auth import check_permission

import requests

def view(request, id):
    domain = Domain.objects.get(pk=id)
    dw = Domain_Whois.objects.filter(domain=domain)

    dform = DomainConfigForm(instance=domain)
    if request.method == "POST":
        if "update" in request.POST:
            dform = DomainConfigForm(request.POST)
            if dform.is_valid():
                w = dform.cleaned_data["whitelisted"]
                domain.whitelisted = w
                domain.save()
                messages.success(request, "Updated.")
    #c = RequestContext(request, {
    c = {
        'form': QueryForm(),
        'authform': AuthenticationForm(),
        'redirect': request.path,
        'domain': domain,
        'dw': dw,
        'dform': dform,
    }
    return render(request, "domain.html", c)

