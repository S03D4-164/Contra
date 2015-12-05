from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib import messages

from ..forms import *
from ..models import *
from ..tasks.ghost_task import *
from .auth import check_permission 

import ast, base64, json
try:
    from StringIO import StringIO as BytesIO
except ImportError:
    from io import StringIO
    from io import BytesIO
from PIL import Image, ImageOps


def create_b64thumb(image):
    thumb = None
    im = Image.open(image)
    #im.thumbnail((480,270))
    im = ImageOps.fit(im, (480,270), centering=(0.0, 0.0))
    #tmp = StringIO()
    tmp = BytesIO()
    im.save(tmp, format="PNG")
    thumb = base64.b64encode(tmp.getvalue())
    return thumb


def view(request, id):
    job = Job.objects.get(pk=id)

    if not check_permission(request, job.query.id):
        messages.warning(request, "Cannot access Job " + str(job.id))
        return redirect("/")

    if request.method == "POST":
        if "run" in request.POST:
            j = Job.objects.create(
                query = job.query,
                status = "Job Created",
                user_agent = job.ua,
                referer = job.referer,
                additional_headers = job.additional_headers,
                method = job.method,
                post_data = job.post_data,
                timeout = job.timeout,
                proxy = job.proxy
            )
            execute_job.delay(j.id)
            rc = progress(request, [j.id])
            return render_to_response("progress.html", rc)

    thumbnail = None
    if job.capture:
        thumbnail = create_b64thumb(appdir + "/" + job.capture.path)
    
    resource = job.resources.all().order_by("seq")
    notimage = job.resources.exclude(content__type__startswith="image").order_by("seq")
    image = job.resources.filter(content__type__startswith="image").order_by("seq")

    c = RequestContext(request, {
        'form': QueryForm(),
        'q': job.query,
        'j': job,
        'p': job.page,
        #'resource': job.resources.all().order_by("seq"),
        'resource': resource,
        'notimage': notimage,
        'image': image,
        'redirect': request.path,
        'thumbnail': thumbnail,
    })
    return render_to_response("job.html", c) 

