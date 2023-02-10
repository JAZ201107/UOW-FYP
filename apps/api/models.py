from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils import timezone
import datetime

from .managers import CustomUserManager


# Create your models here.
# This Model is used to user login
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


def user_image_upload(instance, filename):
    return '/'.join(['images', 'user_profile_images', instance.email, filename])


class UserProfileModel(models.Model):
    """This Model store the basic information of user"""
    user_name = models.TextField(default="NoBody")
    user_email = models.CharField(unique=True, max_length=100)
    user_phone_number = models.TextField(null=True)
    user_address = models.TextField(null=True)


# Upload The Images to Database
def upload_file_name(instance, filename):
    """Upload Image to different folder according to username"""
    return '/'.join(['images', instance.user_email, filename])


class ReceiveImageModel(models.Model):
    """This Model Receive the Image User Upload as well as Use's email"""
    user_email = models.TextField()
    image = models.ImageField(upload_to=upload_file_name)


class UserDetectedImageModel(models.Model):
    """This Model Store Information of the user and uploaded images"""
    user_email = models.TextField()
    origin_image_url = models.TextField()
    detect_image_url = models.TextField()
    counted_number = models.IntegerField()
    uploaded_time = models.DateField(auto_now=True, blank=True)
