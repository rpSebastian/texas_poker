from django.contrib import admin
from .models import Room, Room_Person

# Register your models here.

admin.site.register([Room, Room_Person])

