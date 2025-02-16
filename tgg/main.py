import asyncio
import logging
from pprint import pprint

import sql
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, BotCommand, BotCommandScopeDefault
from config import TOKEN


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
)

sql.init_db()

dp = Dispatcher()

user_commands = [
    BotCommand(command='start', description='начало работы'),
    BotCommand(command='my_memes', description='показать мои мемы'),
]

@dp.message(CommandStart())
async def start_command(message: Message):
    await message.answer(
        "Привет! Отправь мне картинку (мем), и я сохраню её. Используй /my_memes, чтобы посмотреть свои мемы."
    )

@dp.message(Command('my_memes'))
async def show_my_memes(message: Message):
    user_id = str(message.from_user.id)
    memes = sql.get_user_memes(user_id)

    if not memes:
        await message.answer("У вас пока нет мемов. Отправьте картинку, чтобы добавить её!")
        return

    kb = [
        [InlineKeyboardButton(text=f"Мем {i + 1}", callback_data=f"meme_{i}")]
        for i in range(len(memes))
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await message.answer("Ваши мемы:", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("meme_"))
async def send_meme(call: CallbackQuery):
    user_id = str(call.from_user.id)
    meme_index = int(call.data.split("_")[1])
    memes = sql.get_user_memes(user_id)

    if meme_index < len(memes):
        file_id = memes[meme_index]
        await call.message.answer_photo(file_id)
    else:
        await call.answer("Мем не найден!")

@dp.message(F.photo)
async def add_meme(message: Message):
    user_id = str(message.from_user.id)
    mem_id = message.photo[-1].file_id

    sql.add_meme_to_db(user_id, mem_id)

    await message.answer("Мем сохранён! Используй /my_memes, чтобы посмотреть свои мемы.")

@dp.message()
async def all_message(message: Message):
    await message.answer("Я понимаю только команды и картинки. Попробуй /start или отправь мне мем!")

async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())

if __name__ == '__main__':
    asyncio.run(main())