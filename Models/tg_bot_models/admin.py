from django.contrib import admin
from .models import URLModels, Users, API, Proxy


@admin.register(URLModels)
class URLAdmin(admin.ModelAdmin):
    list_display = ('pk', 'url')


@admin.register(Users)
class URLAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username')
    list_filter = ['need_send_message', 'massage_send']


@admin.register(API)
class APIAdmin(admin.ModelAdmin):
    pass
@admin.register(Proxy)
class ProxyAdmin(admin.ModelAdmin):
    pass

