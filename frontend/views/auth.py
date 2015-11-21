from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth.models import User

from ..forms import *

from ..logger import getlogger
logger = getlogger()

def check_permission(request, qid):
    query = Query.objects.get(pk=qid)
    owner = query.registered_by
    user = request.user
    if query.restriction == 0:
        if not user.is_authenticated():
            #messages.error(request, "Authentication required.")
            #return redirect("/")
            return False
        else:
            return True
    elif query.restriction == 1:
        permitted = False
        for g in user.groups.all():
            if g in owner.groups.all():
                permitted = True
                return True
        if not permitted:
            #messages.error(request, "You don't have permission.")
            #return redirect("/")
            return False
    elif query.restriction == 2:
        return True

    messages.error(request, "Permission check failed.")
    #return redirect("/")
    return False

def user(request):
    if not request.user.is_authenticated():
        messages.error(request, "Authentication required to access account information.")
        return redirect("/")

    if request.method == "POST":
        pform = SetPasswordForm(user=request.user, data=request.POST)
        if pform.is_valid():
            pform.save()
            messages.success(request, "Updated.")
        else:
            messages.warning(request, "Invalid Input.")
    rc = RequestContext(request, {
        'form': QueryForm(),
        'authform': AuthenticationForm(),
        'passform': SetPasswordForm(request.user),
        'redirect': request.path,
    })
    return render_to_response("account.html", rc)

def log_in(request, next="/"):
    try:
        next = request.GET.get("next")
    except Exception as e:
        logger.error(e)
    #authform = AuthenticationForm() 
    if request.method == "POST":
        authform = AuthenticationForm(request.POST)
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, "Login Succeeded.")
            else:
                messages.error(request, "Login Failed.")
        else:
            messages.error(request, "Login Failed.")

    return redirect("%s" % next)

def log_out(request):
    logout(request)
    messages.success(request, "Logout Succeeded.")
    next = "/"
    try:
        next = request.GET.get("next")
    except Exception as e:
        logger.error(e)
    return redirect(next) 
