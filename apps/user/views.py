from django.shortcuts import render, redirect
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import requests


# Create your views here.

def user_login(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect("sys_admin_home")
        else:
            # set session
            request.session['user_email'] = request.user.email
            user_email = request.user.email
            return redirect("user_home", email=user_email)
    else:
        return render(request, "base/login.html")


def user_register(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect("sys_admin_home")
        else:
            return redirect("user_home")
    else:
        form = CreateUserForm()
        if request.method == "POST":
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data["username"]
                messages.success(request, "Account Created Successfully For " + user)
                return redirect('')
        context = {
            'form': form
        }
        return render(request, "user/register.html", context=context)


def user_home(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect("sys_admin_home")
        else:
            return render(request, "user/index.html")
    logout(request)
    return redirect("user_login")


@login_required(login_url="user_login")
def user_logout(request):
    logout(request)
    return render(request, "base/login.html")


def user_history(request):
    if request.user.is_authenticated:
        user_email = request.user.email
        if request.user.is_admin:
            return redirect("sys_admin_home")
        else:
            return render(request, "user/history.html", {'user_email': user_email})
    logout(request)
    return redirect("user_login")


def user_profile(request):
    if request.user.is_authenticated:
        user_email = request.user.email
        if request.user.is_admin:
            return redirect("sys_admin_home")
        else:
            return render(request, "user/profile.html", {'user_email': user_email})
    logout(request)
    return redirect("user_login")


def user_IoT(request):
    if request.user.is_authenticated:
        user_email = request.user.email
        if request.user.is_admin:
            return redirect("sys_admin_home")
        else:
            return render(request, "user/profile.html", {'user_email': user_email})
    logout(request)
    return redirect("user_login")


def user_upload(request):
    if request.user.is_authenticated:
        user_email = request.user.email
        if request.user.is_admin:
            return redirect("sys_admin_home")
        else:
            return render(request, "user/upload.html", {'user_email': user_email})
    logout(request)
    return redirect("user_login")
