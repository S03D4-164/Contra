from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from ..forms import *
from ..models import *
from .auth import check_permission

def search(sform):
    url = sform.cleaned_data["url"]
    ip = sform.cleaned_data["ip"]
    payload = sform.cleaned_data["payload"]
    webapp = sform.cleaned_data["webapp"]

    res = Resource.objects.all()
    print(res)
    if url:
        res = res.filter(url__url__iregex=url)
    if ip:
        res = res.filter(host_info__host_dns__a__ip__iregex=ip)
    if payload:
        res = res.filter(content__content__iregex=payload)
    if webapp:
        res = res.filter(webapp__in=webapp)

    return res

def view(request):
    sform = SearchForm()
    user = request.user
    query = Query.objects.filter(restriction=2)
    if user.is_authenticated():
        query = Query.objects.filter(restriction=2) | Query.objects.filter(restriction=0)
        try:
            query = Query.objects.filter(restriction=2) \
                | Query.objects.filter(restriction=0) \
                | Query.objects.filter(registered_by__groups__in=user.groups.all())
        except:
            pass

    r = None
    if request.method == "POST":
        sform = SearchForm(request.POST)
        if sform.is_valid():
            result = search(sform)
            r_ids = Job.objects.filter(query=query).values_list('resources', flat=True)
            r = result.filter(id__in=r_ids).distinct()

    #c = RequestContext(request, {
    c = {
        'form': QueryForm(),
        'authform': AuthenticationForm(),
        'redirect': request.path,
        'resource': r,
        'sform': sform,
    }
    return render(request, "search.html", c)

