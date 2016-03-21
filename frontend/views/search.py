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
    date_from = sform.cleaned_data["date_from"]
    date_to = sform.cleaned_data["date_to"]
    signature = sform.cleaned_data["signature"]

    res = Resource.objects.all()
    #print(res)
    if date_from:
        res = res.filter(created_at__gte=date_from)
    if date_to:
        res = res.filter(created_at__lte=date_to)
    if url:
        res = res.filter(url__url__iregex=url)
    if ip:
        res = res.filter(host_info__host_dns__a__ip__iregex=ip)
    if payload:
        res = res.filter(content__content__iregex=payload)
    if webapp:
        res = res.filter(webapp__in=webapp)
    if signature:
        res = res.filter(analysis__rule__in=signature)

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

    p = None
    r = None
    if request.method == "POST":
        sform = SearchForm(request.POST)
        if sform.is_valid():
            result = search(sform)
            r_ids = Job.objects.filter(query__in=query).values_list('resources', flat=True)
            r = result.filter(id__in=r_ids).distinct()
            p_ids = Job.objects.filter(query__in=query).values_list('page', flat=True)
            p = result.filter(id__in=p_ids).distinct()

    c = {
        'form': QueryForm(),
        'authform': AuthenticationForm(),
        'redirect': request.path,
        'resource': r,
        'sform': sform,
    }
    return render(request, "search.html", c)

