from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

# Create your views here.

def sys_admin_login(request):
    return render(request, "base/admin_login.html")

def sys_admin_page(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return render(request, "sys_admin/index.html")
        else:
            return redirect("user_home")
    logout(request)
    return redirect("user_login")

def sys_admin_logout(request):
    return redirect("sys_admin_login")

def sys_admin_all_users(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return render(request, "sys_admin/all_users.html")
        else:
            return redirect("user_home")
    logout(request)
    return redirect("user_login")

def sys_admin_all_images(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return render(request, "sys_admin/all_images.html")
        else:
            return redirect("user_home")
    logout(request)
    return redirect("user_login")

def sys_admin_profile(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return render(request, "sys_admin/sys_admin_profile.html")
        else:
            return redirect("user_home")
    logout(request)
    return redirect("user_login")

def sys_admin_create_user(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return render(request, "sys_admin/create_user.html")
        else:
            return redirect("user_home")
    logout(request)
    return redirect("user_login")
