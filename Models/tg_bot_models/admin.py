from django.contrib import admin
from .models import (
    URLModels,
    Users,
    API,
    Proxy,
    SendMessage,
    SampleMessage
)


@admin.register(URLModels)
class URLAdmin(admin.ModelAdmin):
    list_display = ('pk', 'url')


@admin.register(Users)
class URLAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username')
    list_filter = ['need_send_message', 'massage_send']


@admin.register(API)
class APIAdmin(admin.ModelAdmin):
    list_display = ('pk', "username", 'phone', "use", "proxy")


@admin.register(Proxy)
class ProxyAdmin(admin.ModelAdmin):
    list_display = ('pk', "address", 'port', "username", "password")


@admin.register(SendMessage)
class SendMessageAdmin(admin.ModelAdmin):
    list_display = ('pk', "api", 'user_id', "user_username")

    list_filter = ['is_send']

    def user_id(self, obj):
        return obj.user.user_id

    def user_username(self, obj):
        return obj.user.username

    def api(self, obj):
        return obj.api.api_id


@admin.register(SampleMessage)
class SampleMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'text')
    list_filter = ['id']
