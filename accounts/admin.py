from django.contrib import admin
from django.apps import  apps
from django.contrib.admin.sites import AlreadyRegistered

from .models import *

# Register your models here.
for model in apps.get_app_config('accounts').get_models():
	try:
		admin.site.register(model)
	except AlreadyRegistered:
		pass
