from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from ..forms import *
from ..models import *
from ..tasks.job_task import *
from .progress import main as progress
from .auth import check_permission


def _query_job(query, form):
    ua = form.cleaned_data["user_agent"]
    referer = form.cleaned_data["referer"]
    proxy = form.cleaned_data["proxy"]
    if proxy:
        proxy = parse_url(proxy)
    additional_headers = form.cleaned_data["additional_headers"]
    method = form.cleaned_data["method"]
    post_data = form.cleaned_data["post_data"]
    timeout = form.cleaned_data["timeout"]
    job = Job.objects.create(
        query = query,
        status = "Job Created",
        user_agent = ua,
        referer = referer,
        additional_headers = additional_headers,
        method = method,
        post_data = post_data,
        timeout = timeout,
    )
    if proxy:
        job.proxy = proxy
        job.save()
    return job

def view(request, id):
    query = Query.objects.get(pk=id)

    if not check_permission(request, query.id):
        messages.error(request, "Cannot access Query " + str(query.id))
        return redirect("/")

    cform = QueryConfigForm(instance=query)
    if request.method == "POST":
        if "run" in request.POST:
            form = QueryRunForm(request.POST)
            if form.is_valid():
                j = _query_job(query, form)
                execute_job.delay(j.id)
                rc = progress(request, [j.id])
                return render_to_response("progress.html", rc) 
        elif "delete" in request.POST:
            query.delete()
            return redirect("/")
        elif "update" in request.POST:
            cform = QueryConfigForm(request.POST)
            if cform.is_valid():
                interval = cform.cleaned_data["interval"]
                counter = cform.cleaned_data["counter"]
                restriction = cform.cleaned_data["restriction"]
                query.interval = interval
                query.counter = counter
                query.restriction = restriction
                query.save()

    job = Job.objects.filter(query=query)

    c = RequestContext(request, {
        'form': QueryForm(),
        'authform': AuthenticationForm(),
        'redirect': request.path,
        'qrform': QueryRunForm(),
        'q': query,
        'job': job,
        'cform': cform,
    })
    return render_to_response("query.html", c) 

