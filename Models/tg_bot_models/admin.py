from django.contrib import admin
from .models import URLModels, Users
@admin.register(URLModels)
class URLAdmin(admin.ModelAdmin):
    list_display = ('pk', 'url')


@admin.register(Users)
class URLAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username')

