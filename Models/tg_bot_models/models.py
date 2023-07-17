from django.db import models


class URLModels(models.Model):
    url = models.URLField(verbose_name='URL')
    inuse = models.BooleanField(default=False, verbose_name='использовался ли этот url ранее')
    last_message = models.IntegerField(default=0, verbose_name='Последнее прочитанное соощение')


class Users(models.Model):
    user_id = models.IntegerField(verbose_name='ID пользователя')
    username = models.CharField(max_length=128, null=True, verbose_name='Имя пользователя')
    find_chat = models.URLField(verbose_name='URL чата, в котором найден пользователь')
    date = models.DateField(auto_now_add=True, verbose_name='Дата добавления пользователя')
