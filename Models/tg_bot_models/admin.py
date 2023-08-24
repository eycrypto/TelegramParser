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
    pass


@admin.register(Proxy)
class ProxyAdmin(admin.ModelAdmin):
    pass


@admin.register(SendMessage)
class SendMessageAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user_id', "user_username")

    list_filter = ['is_send']

    def user_id(self, obj):
        return obj.user.user_id

    def user_username(self, obj):
        return obj.user.username


@admin.register(SampleMessage)
class SampleMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'text')
    list_filter = ['id']
