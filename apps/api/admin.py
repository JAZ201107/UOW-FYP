from django.contrib import admin

# Register your models here.
from apps.api.models import User
admin.site.register(User)