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
    need_send_message = models.BooleanField(default=False, verbose_name='Нужно ли отправить сообщение пользователю')
    massage_send = models.BooleanField(default=False, verbose_name='Пользователю отправлено сообщение')


class Proxy(models.Model):
    address = models.CharField(max_length=32, blank=True, null=True, verbose_name='Адресс прокси')
    port = models.IntegerField(default=0, blank=True, null=True, verbose_name='Порт прокси')
    username = models.CharField(max_length=64, blank=True, null=True, verbose_name='Имя пользователя прокси')
    password = models.CharField(max_length=128, blank=True, null=True, verbose_name='Пароль пользователя прокси')

    def __str__(self):
        return f"{self.address} {self.port}"


class API(models.Model):
    username = models.CharField(max_length=64, verbose_name='Имя пользователя')
    phone = models.CharField(max_length=64, verbose_name='Номер телефона(должн начинаться с +')
    api_id = models.CharField(max_length=16, verbose_name='id API Telegram')
    api_hash = models.CharField(max_length=64, verbose_name='hash API Telegram')
    use = models.BooleanField(default=True, verbose_name='Нужно ли использовать API для рассылки сообщений', null=True)
    proxy = models.ForeignKey('Proxy', on_delete=models.CASCADE, related_name='proxy', blank=True, null=True,
                              verbose_name='Прокси')

    def __str__(self):
        return f"API_ID: {self.api_id}***API_USERNAME: {self.username}"


class SendMessage(models.Model):
    api = models.ForeignKey('API', on_delete=models.CASCADE, related_name='api_message',
                            verbose_name='API, с которого отправлено сообщение', null=True)
    user = models.ForeignKey('Users', on_delete=models.CASCADE, related_name='user',
                             verbose_name='Пользователь, которому отправлено сообщение')
    message = models.CharField(max_length=2048, verbose_name='Текст сообщения')
    is_send = models.BooleanField(verbose_name='Отправлено ли сообщение')
    error = models.CharField(null=True, blank=True, max_length=128, verbose_name='Ошибка, если есть')


class SampleMessage(models.Model):
    text = models.TextField(verbose_name='Текст')
    error = models.CharField(null=True, blank=True, max_length=128, verbose_name='Ошибка, если есть')
