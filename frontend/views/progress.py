from django.shortcuts import render_to_response, render
from django.template import RequestContext

from ..forms import *
from ..models import *
import re, logging

def view(request):
    c = None
    if request.method == "GET":
        jobs = request.GET.getlist("job[]")
        if not jobs:
            jobs = request.GET.get("job")
        c = main(request, jobs)
    #return render_to_response("progress.html", rc)
    return render(request, "progress.html", c)

    
def main(request, jobs):
    job = Job.objects.filter(pk__in=jobs).order_by("pk")

    status = None
    for j in job:
        if re.search("(^Completed|^Error)", str(j.status)):
            pass
        else:
            status = "Processing"
    if status == None:
        status = "Finished"

    #rc = RequestContext(request, {
    c = {
        'form': QueryForm(),
        'job': job,
        'status': status,
    }
    return c

