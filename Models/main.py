import configparser
import os
import random
import time

import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'Models.settings'
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from tg_bot_models.models import URLModels, Users, API, Proxy
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.users import GetFullUserRequest

config = configparser.ConfigParser()
config.read("config.ini")

api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']

main_client = TelegramClient(username, int(api_id), api_hash)
main_client.start()


async def activate_sessions(all_api, all_proxy):
    a = 0
    for api in all_api:
        proxy = all_proxy[a]
        proxy = {
            "proxy_type": "socks5",
            "addr": proxy.address,
            "port": proxy.port,
            "username": proxy.username,
            "password": proxy.password
        }
        client = TelegramClient(api.username, api_id=api.api_id, api_hash=api.api_hash, proxy=proxy)
        await client.start(phone=api.phone)
        a += 1


async def get_full(id):
    return await main_client(GetFullUserRequest(id))


async def get_users(channel, model_url):
    print(f'Start parsing {model_url.url}')
    offset_msg = 0
    limit_msg = 100
    users = Users.objects.all()
    finish_check_message = True
    a = True

    while finish_check_message:
        history = await main_client(GetHistoryRequest(
            peer=channel,
            offset_id=offset_msg,
            offset_date=None, add_offset=0,
            limit=limit_msg, max_id=0, min_id=0,
            hash=0))
        if not history.messages:
            break
        messages = history.messages
        if not model_url.inuse:
            model_url.inuse = True
            model_url.last_message = messages[0].id - 5000
            model_url.save()
        elif model_url.inuse and a:
            c = model_url.last_message
            model_url.last_message = messages[0].id
            model_url.save()
            a = False
        for message in messages:
            try:
                id = message.to_dict()['from_id']['user_id']
                if not users.filter(user_id=id):
                    full = await get_full(id)
                    username = full.users[0].username
                    Users.objects.create(user_id=id,
                                         username=username,
                                         find_chat=model_url.url)
                if message.id <= c:
                    finish_check_message = False
                    break
            except Exception:
                pass
        offset_msg = messages[-1].id


async def send_message_to_users(all_api, all_proxy, users):
    a = 0
    text = input('Введите текст рассылки\n')
    while users:
        mesage_count = 0
        proxy = all_proxy[a]
        api = all_api[a]
        proxy = {
            "proxy_type": "socks5",
            "addr": proxy.address,
            "port": proxy.port,
            "username": proxy.username,
            "password": proxy.password
        }
        client = TelegramClient(api.username, api_id=api.api_id, api_hash=api.api_hash, proxy=proxy)
        await client.start()
        while mesage_count < 4 and users:
            user = users[0]
            await client.send_message(user.username,
                                      text)
            user.need_send_message = False
            user.massage_send = True
            user.save()
            users = Users.objects.filter(need_send_message=True)
            mesage_count += 1
            time.sleep(3)
        a += 1


async def main():
    task = int(
        input('Вы уже актевировали сессии? Если нет, то введите 1, если акстивировали, то введите люой символ\n'))
    if task == 1:
        all_api = API.objects.all()
        all_proxy = Proxy.objects.all()
        await activate_sessions(all_api, all_proxy)
    task = int(input('Выбирите действие, которое хотите выполнить:\n'
                     '1 - Собр пользователей \n'
                     '2 Отправка пользователям сообщений\n'))
    if task == 1:
        while True:
            urls = URLModels.objects.all()
            for model_url in urls:
                url = model_url.url
                channel = await main_client.get_entity(url)
                await get_users(channel, model_url)
    elif task == 2:
        all_api = API.objects.all()
        all_proxy = Proxy.objects.all()
        users = Users.objects.filter(need_send_message=True)
        await send_message_to_users(all_api, all_proxy, users)


with main_client:
    main_client.loop.run_until_complete(main())
