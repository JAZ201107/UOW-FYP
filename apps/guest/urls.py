from django.urls import path
from apps.guest import views

urlpatterns = [
    path("guest_page/", views.upload_images, name="guest_page"),
]
