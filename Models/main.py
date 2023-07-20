import configparser
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'Models.settings'
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from tg_bot_models.models import URLModels, Users
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.users import GetFullUserRequest

config = configparser.ConfigParser()
config.read("config.ini")

api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']

client = TelegramClient(username, api_id, api_hash)

client.start()


async def get_full(id):
    return await client(GetFullUserRequest(id))


async def get_users(channel, model_url):
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
            model_url.last_message = messages[0].id + 1
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
                    if message.id == model_url.last_message:
                        finish_check_message = False
                        break
            except Exception:
                pass
        offset_msg = messages[-1].id


async def main():
    while True:
        urls = URLModels.objects.all()
        for model_url in urls:
            url = model_url.url
            channel = await client.get_entity(url)
            await get_users(channel, model_url)


with client:
    client.loop.run_until_complete(main())
