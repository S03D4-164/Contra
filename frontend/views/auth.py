from django.shortcuts import render, redirect
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm, UserChangeForm
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

    u = User.objects.get(username=request.user)
    if request.method == "POST":
        pform = SetPasswordForm(user=u, data=request.POST)
        if pform.is_valid():
            pform.save()
            messages.success(request, "Password Updated.")
        #else:
        #    messages.warning(request, "Invalid Password.")

        mform = UserEmailForm(request.POST)
        if mform.is_valid():
            m = mform.cleaned_data["email"]
            if m != u.email:
                u.email = m
                u.save()
                messages.success(request, "Email Address Updated.")
        else:
            messages.warning(request, "Invalid Email Address.")
        return redirect(".")

    #rc = RequestContext(request, {
    c = {
        'form': QueryForm(),
        'authform': AuthenticationForm(),
        'passform': SetPasswordForm(request.user),
        'emailform': UserEmailForm(instance=u),
        'redirect': request.path,
    }
    #return render_to_response("account.html", rc)
    return render(request, "account.html", c)

def log_in(request, next="/"):
    try:
        next = request.GET.get("next")
        if not next:
            next = "/"
    except Exception as e:
        logger.error(e)
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
    else:
        rc = RequestContext(request, {
            'authform': AuthenticationForm(),
        })
        return render_to_response("login.html", rc)

def log_out(request):
    logout(request)
    messages.success(request, "Logout Succeeded.")
    next = "/"
    try:
        next = request.GET.get("next")
    except Exception as e:
        logger.error(e)
    return redirect(next) 
