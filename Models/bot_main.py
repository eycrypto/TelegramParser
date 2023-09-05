from bot_config import dp
from aiogram.utils import executor
import os
import django

from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
import bot_config
from bot_config import bot

os.environ['DJANGO_SETTINGS_MODULE'] = 'Models.settings'
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()
from tg_bot_models.models import API


class FormStates(StatesGroup):
    link = State()
    button_text = State()
    text = State()


async def fsm_start(message: types.Message):
    all_api = API.objects.all()
    usernames = []
    for user in all_api:
        usernames.append(user.username)
        print(user.username)

    if message.from_user.username in usernames:
        await message.reply("Отправьте ссылку на чек")
        await FormStates.link.set()
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text="У вас нету доступа к боту"
        )


async def load_link(message: types.Message,
                    state: FSMContext):
    async with state.proxy() as data:
        data["link"] = message.text

    await FormStates.next()
    await message.reply("Отправьте текст для кнопки")


async def load_button_text(message: types.Message,
                           state: FSMContext):
    async with state.proxy() as data:
        data["button_text"] = message.text

    await FormStates.next()
    await message.reply("Отправьте текст для сообщения")


async def load_text(message: types.Message,
                    state: FSMContext):
    async with state.proxy() as data:
        markup = InlineKeyboardMarkup()
        link_button = InlineKeyboardButton(
            text=data['button_text'],
            url=data['link']
        )
        markup.add(
            link_button
        )

    await bot.send_message(
        chat_id=bot_config.CHANNEL,
        text=message.text,
        reply_markup=markup
    )

    await state.finish()


async def start_button(message: types.Message):
    print(message.chat.id)
    all_api = API.objects.all()
    usernames = []
    for user in all_api:
        usernames.append(user.username)
        print(user.username)

    if message.from_user.username in usernames:
        await bot.send_message(
            chat_id=message.chat.id,
            text="Для создания поста с чеком нажмите на комманду /add_post"
        )
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text="У вас нету доступа к боту"
        )


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_button, commands=['start'])

    dp.register_message_handler(fsm_start, commands=['add_post'])
    dp.register_message_handler(load_link, content_types=["text"],
                                state=FormStates.link)
    dp.register_message_handler(load_button_text, content_types=["text"],
                                state=FormStates.button_text)
    dp.register_message_handler(load_text, content_types=["text"],
                                state=FormStates.text)


register_handlers(dp=dp)

if __name__ == "__main__":
    executor.start_polling(dp,
                           skip_updates=True)
