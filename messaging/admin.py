from django.contrib import admin
from . import models

admin.site.register(models.Inquiry)
admin.site.register(models.Notification)


