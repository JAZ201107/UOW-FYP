from django.urls import path
from apps.user import views

urlpatterns = [
    path("login/", views.user_login, name='user_login'),
    path("register/", views.user_register, name="register"),
    path("user/home/", views.user_home, name="user_home"),
    path("", views.user_logout, name="user_logout"),

    # check history
    path("user/history/", views.user_history, name="user_history"),

    # user profile
    path("user/profile", views.user_profile, name="user_profile"),

    # user IoT
    path("user/IoT", views.user_IoT, name="user_IoT"),

    # user upload image
    path("user/upload", views.user_upload, name="user_upload")
]
