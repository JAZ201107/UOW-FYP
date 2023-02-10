from django.urls import path
from apps.api.views import user_views, account_views, image_views, basic_views
from knox.views import LogoutView, LogoutAllView
from rest_framework import routers

from apps.api import views

# router = routers.DefaultRouter()
# router.register('images', user_views.ImageViewSet, basename='image')

urlpatterns = [
    path("api/", basic_views.getRoutes),  # show all REST API other user can use
    path("api/users/", user_views.UserList.as_view(), name='users'),
    path("api/users/<int:pk>/", user_views.UserDetail.as_view()),
    path("api/registeruser/", user_views.UserRegistration.as_view(), name='registeruser'),
    path("api/loginuser/", account_views.LoginView.as_view(), name='loginuser'),
    path("api/verifytoken/", account_views.verify_token, name='verifyuser'),
    path("api/logout/", LogoutView.as_view()),
    path("api/logout-all/", LogoutView.as_view()),
    path("api/images/upload", image_views.ReceiveImageModelView.as_view()),  # Image REST API
    path("api/users/info", views.user_views.UserProfileView.as_view()),  # Return the User Profile Information
    path("api/users/history", views.user_views.UserDetectedImageView.as_view()),  # Return all images user uploaded
    path("api/users/allusers", views.account_views.GetAllUserAndImages.as_view())
]
