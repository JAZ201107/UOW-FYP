from django.urls import path
from . import views

urlpatterns = [
    path("sys_admin_login/", views.sys_admin_login, name="sys_admin_login"),
    path("sys_admin_home/", views.sys_admin_page, name="sys_admin_home"),
    path("sys_admin_logout/", views.sys_admin_logout, name="sys_admin_logout"),

    path("sys_admin_profile", views.sys_admin_profile, name="sys_admin_profile"),
    path("sys_admin_all_users", views.sys_admin_all_users, name="sys_admin_all_users"),
    path("sys_admin_all_images", views.sys_admin_all_images, name="sys_admin_all_images"),
    path("sys_admin_create_user", views.sys_admin_create_user, name="sys_admin_create_user"),
]
