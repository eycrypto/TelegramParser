import asyncio
import os
import random
import time

from telethon import functions, types
import django
from telethon.tl.functions.messages import SendReactionRequest

import bot_config

os.environ['DJANGO_SETTINGS_MODULE'] = 'Models.settings'
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from tg_bot_models.models import URLModels, Users, API, SendMessage, SampleMessage
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


async def send_message_to_users(all_api, users, url):
    global message_text
    a = 0

    message_id = input('- Введите ID сообщения\n'
                       'или\n'
                       '- Введите 0 если хотите отправить сообщение из группы\n')
    if message_id != '0':
        message_text = SampleMessage.objects.get(id=message_id).text
    else:
        message_text = "None"
    for user in users:
        try:
            api = all_api[a]
        except IndexError:
            a = 0
            api = all_api[a]
        proxy = api.proxy
        proxy = {
            "proxy_type": "socks5",
            "addr": proxy.address,
            "port": proxy.port,
            "username": proxy.username,
            "password": proxy.password
        }
        print(f"API_ID: {api.api_id}")
        print(f"API_USERNAME: {api.username}")
        print(f"API_PHONE_NUMBER: {api.phone}")
        print(f"API_PROXY_ADDRESS: {api.proxy.address}")
        client = TelegramClient(api.username, api_id=api.api_id, api_hash=api.api_hash, proxy=proxy)
        await client.start()
        try:
            if message_id == '0':
                all_dialogs = [d for d in await client.get_dialogs()]
                only_groups = list(filter(lambda d: d.is_group, all_dialogs))
                for group in only_groups:
                    if group.entity.id == int(bot_config.CHANNEL_ID_CHEQUES):
                        message = await client.get_messages(group)
                        await client.forward_messages(
                            user.username,
                            message[0],
                        )
                        user.massage_send = True
                        user.save()
                        SendMessage.objects.create(
                            api=api,
                            user=user,
                            message=message[0].reply_markup.rows[0].buttons[0].url,
                            is_send=True,
                            error=None
                        )
                        print(f"User: {user.username}\n")
                        await asyncio.sleep(10)
            else:
                await client.send_message(user.username,
                                          message_text,
                                          parse_mode="markdown")

                user.need_send_message = False
                user.massage_send = True
                user.save()
                SendMessage.objects.create(
                    api=api,
                    user=user,
                    message=message_text,
                    is_send=True,
                    error=None
                )
                print(f"User: {user.username}\n")
                await asyncio.sleep(10)
        except Exception as exc:
            print(exc)
            SendMessage.objects.create(
                api=api,
                user=user,
                message=message_text,
                is_send=False,
                error=exc
            )
            await asyncio.sleep(10)
        a += 1
        await client.disconnect()


async def reactions(chat, all_api):
    reactions = ['👍', '❤️', '👏', '🎉']
    for api in all_api:
        try:
            reaction = random.choice(reactions)
            reactions.remove(reaction)
        except IndexError:
            reactions = ['👍', '❤️', '👏', '🎉']
            reaction = random.choice(reactions)
        proxy = api.proxy
        proxy = {
            "proxy_type": "socks5",
            "addr": proxy.address,
            "port": proxy.port,
            "username": proxy.username,
            "password": proxy.password
        }
        print(f"API_ID: {api.api_id}")
        print(f"API_USERNAME: {api.username}")
        print(f"API_PHONE_NUMBER: {api.phone}")
        print(f"API_PROXY_ADDRESS: {api.proxy.address}")
        client = TelegramClient(api.username, api_id=api.api_id, api_hash=api.api_hash, proxy=proxy)
        await client.start()
        await client(functions.channels.JoinChannelRequest(
            channel=chat
        ))
        all_dialogs = [d for d in await client.get_dialogs()]
        only_groups = list(filter(lambda d: d.is_group, all_dialogs))
        only_channels = list(filter(lambda d: d.is_channel, all_dialogs))

        for group in only_groups:
            try:
                if group.entity.username == chat:
                    await client(SendReactionRequest(
                        peer=chat,
                        msg_id=group.message.id,
                        reaction=[types.ReactionEmoji(
                            emoticon=reaction
                        )]
                    ))
                    print(f"Channel: {group.entity.username}\n")
            except AttributeError:
                pass
        for channel in only_channels:
            try:
                if channel.entity.username == chat:
                    await client(SendReactionRequest(
                        peer=chat,
                        msg_id=channel.message.id,
                        reaction=[types.ReactionEmoji(
                            emoticon=reaction
                        )]
                    ))
                    print(f"Channel: {channel.entity.username}\n")
            except AttributeError:
                pass

        await client.disconnect()
        await asyncio.sleep(10)


async def leaving_comment(chat, all_api):
    text = input('Введите сообщение которое хотите оставить под постом\n')
    sent_history = False
    for api in all_api:
        proxy = api.proxy
        proxy = {
            "proxy_type": "socks5",
            "addr": proxy.address,
            "port": proxy.port,
            "username": proxy.username,
            "password": proxy.password
        }
        print(f"API_ID: {api.api_id}")
        print(f"API_USERNAME: {api.username}")
        print(f"API_PHONE_NUMBER: {api.phone}")
        print(f"API_PROXY_ADDRESS: {api.proxy.address}")
        client = TelegramClient(api.username, api_id=api.api_id, api_hash=api.api_hash, proxy=proxy)
        await client.start()
        me = await client.get_me()
        await client(functions.channels.JoinChannelRequest(
            channel=chat
        ))
        all_dialogs = [d for d in await client.get_dialogs()]
        only_channels = list(filter(lambda d: d.is_channel, all_dialogs))
        for channel in only_channels:
            try:
                if channel.entity.username == chat:
                    async for m in client.iter_messages(chat, reply_to=channel.message.id):
                        if m.from_id.user_id == me.id:
                            sent_history = True

                    if sent_history:
                        pass
                    else:
                        await client.send_message(
                            entity=channel.entity.username,
                            message=text,
                            comment_to=channel.message,
                            parse_mode="markdown"
                        )
                        print(f"API_ID: {api.api_id}")
                        print(f"API_USERNAME: {api.username}")
                        print(f"API_PHONE_NUMBER: {api.phone}")
                        print(f"API_PROXY_ADDRESS: {api.proxy.address}")
                        print(f"Channel: {channel.entity.username}\n")
                        await asyncio.sleep(10)
            except AttributeError as e:
                print(e)
                pass


async def main():
    task = input('Вы уже активировали сессии? Если нет, то введите 1, если активировали, то введите любой символ\n')
    all_api = API.objects.filter(use=True)
    if task == '1':
        await activate_sessions(all_api)
    task = int(input('Выберите действие, которое хотите выполнить:\n'
                     '1 - Собр пользователей \n'
                     '2 - Отправка пользователям сообщений\n'
                     '3 - Поставить реакцию/коммент под постом Канала\n'
                     ))
    if task == 1:
        api = all_api[0]
        proxy = api.proxy
        proxy = {
            "proxy_type": "socks5",
            "addr": proxy.address,
            "port": proxy.port,
            "username": proxy.username,
            "password": proxy.password
        }
        client = TelegramClient(api.username, api_id=api.api_id, api_hash=api.api_hash, proxy=proxy)
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
        users = Users.objects.filter(find_chat=url,
                                     massage_send=False)
        limited_users = []
        for user in users[:users_amount]:
            if not user.username:
                pass
            else:
                limited_users.append(user)
        await send_message_to_users(all_api, limited_users, url=url)

    elif task == 3:
        channel_id = input('Введите Username Канала\n')
        action = int(input('Выберите дальнейшие действия\n'
                           '1 - Оставить реакцию под постом\n'
                           '2 - Оставить комментарии под постом\n'))

        if action == 1:
            await reactions(chat=channel_id, all_api=all_api)
        elif action == 2:
            await leaving_comment(chat=channel_id, all_api=all_api)
        else:
            print("Выберите 1 или 2")
    else:
        print("Выберите 1, 2 или 3")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
