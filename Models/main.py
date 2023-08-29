import asyncio
import configparser
import os
import random
import time

import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'Models.settings'
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from tg_bot_models.models import URLModels, Users, API, Proxy, SendMessage, SampleMessage
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.users import GetFullUserRequest


async def activate_sessions(all_api):
    for api in all_api:
        proxy = api.proxy
        proxy = {
            "proxy_type": "socks5",
            "addr": proxy.address,
            "port": proxy.port,
            "username": proxy.username,
            "password": proxy.password
        }
        print(api.phone)
        client = TelegramClient(api.username, api_id=api.api_id, api_hash=api.api_hash, proxy=proxy)
        await client.start(phone=api.phone)
        await client.disconnect()


async def get_full(id, client):
    return await client(GetFullUserRequest(id))


async def get_users(channel, model_url, client):
    print(f'Start parsing {model_url.url}')
    offset_msg = 0
    limit_msg = 100
    users = Users.objects.all()
    finish_check_message = True
    a = True

    while finish_check_message:
        history = await client(GetHistoryRequest(
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
                    full = await get_full(id, client)
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


async def send_message_to_users(all_api, users):
    a = 0
    message_id = input('Введите ID сообщения\n')
    message_text = SampleMessage.objects.get(id=message_id).text
    for user in users:
        api = all_api[a]
        client = TelegramClient(api.username, api_id=api.api_id, api_hash=api.api_hash, proxy=api.proxy)
        await client.start()
        try:
            await client.send_message(user.user_id,
                                      message_text,
                                      parse_mode="markdown")

            user.need_send_message = False
            user.massage_send = True
            user.save()
            SendMessage.objects.create(
                user=user,
                message=message_text,
                is_send=True,
                error=None
            )
            print(f"User: {user.user_id}")
            time.sleep(5)
        except Exception as exc:
            SendMessage.objects.create(
                user=user,
                message=message_text,
                is_send=False,
                error=exc
            )
            time.sleep(5)
        a += 1
        await client.disconnect()


async def main():
    task = input('Вы уже активировали сессии? Если нет, то введите 1, если активировали, то введите любой символ\n')
    all_api = API.objects.all()
    if task == '1':
        await activate_sessions(all_api)
    task = int(input('Выбирите действие, которое хотите выполнить:\n'
                     '1 - Собр пользователей \n'
                     '2 - Отправка пользователям сообщений\n'))
    if task == 1:
        api = all_api[0]
        client = TelegramClient(api.username, api_id=api.api_id, api_hash=api.api_hash, proxy=api.proxy)
        await client.start(phone=api.phone)
        while True:
            urls = URLModels.objects.all()
            for model_url in urls:
                url = model_url.url
                channel = await client.get_entity(url)
                await get_users(channel, model_url, client)
    elif task == 2:
        users_amount = int(input('Введите количество пользователей\n'))
        url = input("Введите URL чата, в котором найден пользователь\n")
        all_api = API.objects.all()
        users = Users.objects.filter(
            find_chat=url)
        limited_users = []
        for user in users[:users_amount]:
            limited_users.append(user)
        await send_message_to_users(all_api, limited_users)


"https://t.me/+996703777111"

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
