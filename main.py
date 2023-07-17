import configparser
import json


from telethon.sync import TelegramClient
import csv
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.users import GetFullUserRequest

# Считываем учетные данные
config = configparser.ConfigParser()
config.read("config.ini")

# Присваиваем значения внутренним переменным
api_id   = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']



client = TelegramClient(username, api_id, api_hash)

client.start()

async def get_full(id):
	return await client(GetFullUserRequest(id))

async def get_users(channel):
	offset_msg = 0
	limit_msg = 100
	users = {}
	all_messages = 0
	total_user_limit = int(input('Сколько ников пользователей вам нужно получить? '))

	while len(users) < total_user_limit:
		history = await client(GetHistoryRequest(
			peer=channel,
			offset_id=offset_msg,
			offset_date=None, add_offset=0,
			limit=limit_msg, max_id=0, min_id=0,
			hash=0))
		if not history.messages:
			break
		messages = history.messages
		for message in messages:
			all_messages +=1
			id = message.to_dict()['from_id']['user_id']
			if id not in users:
				full = await get_full(id)
				users[id] = full.users[0].username
			if len(users)>=total_user_limit:
				break
		offset_msg = messages[len(messages) - 1].id
	with open('user.csv', 'w') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(('ID', 'USERNAME'))
		for i in users:
			writer.writerow((i, users[i]))


async def main():
	url = 'https://t.me/CryptoBotRussian'
	channel = await client.get_entity(url)
	await get_users(channel)


with client:
	client.loop.run_until_complete(main())