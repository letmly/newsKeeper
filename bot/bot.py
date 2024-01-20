import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from dotenv import load_dotenv

import news_obs

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")


@dp.message(Command("news"))
async def news_handler(message: types.Message) -> None:
    """
    This handler receives messages with `/news` command
    """
    try:
        message = await message.answer("Выгрузка новостей")
        # Отправляем клавиатуру с новостями в чат бота
        await news_obs.get_keyboard_news(message=message)

    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Ooops!")


@dp.message(Command("synonymous"))
async def synonymous_handler(message: types.Message, command: CommandObject) -> None:
    try:
        message = await message.answer("Поиск синонимов...")
        # Отправляем клавиатуру с новостями в чат бота
        await news_obs.get_synonymous(message=message, word=command.args)

    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("похоже такого слова нет в словаре :(!")



# Обработка callback-кнопоки детального просмотра новости
@dp.callback_query(news_obs.NewsCallback.filter(F.action == "view"))
async def process_view_news(callback_query: types.CallbackQuery, callback_data: news_obs.NewsCallback):
    news_id = int(callback_data.news_id)
    page = int(callback_data.page)
    await news_obs.get_keyboard_details_news(message=callback_query.message, news_id=news_id, page=page)


# Обработка callback-кнопки "Вернуться назад"
@dp.callback_query(news_obs.NewsCallback.filter(F.action == "back"))
async def process_back_to_news_list(callback_query: types.CallbackQuery, callback_data: news_obs.NewsCallback):
    page = int(callback_data.page)
    await news_obs.get_keyboard_news(message=callback_query.message, page=page)


# Обработка callback-кнопки перехода на предыдущую страницу
@dp.callback_query(news_obs.NewsCallback.filter(F.action == "previous"))
async def process_previous_page(callback_query: types.CallbackQuery, callback_data: news_obs.NewsCallback):
    page = int(callback_data.page)
    await news_obs.get_keyboard_news(message=callback_query.message, page=page)


# Обработка callback-кнопки перехода на следующую страницу
@dp.callback_query(news_obs.NewsCallback.filter(F.action == "next"))
async def process_next_page(callback_query: types.CallbackQuery, callback_data: news_obs.NewsCallback):
    page = int(callback_data.page)
    await news_obs.get_keyboard_news(message=callback_query.message, page=page)


# Обработка callback-кнопки рерайтинга
@dp.callback_query(news_obs.NewsCallback.filter(F.action == "rewrite"))
async def process_rewrite(callback_query: types.CallbackQuery, callback_data: news_obs.NewsCallback):
    news_id = int(callback_data.news_id)
    page = int(callback_data.page)
    await news_obs.get_keyboard_rewrited_new(message=callback_query.message, news_id=news_id, page=page)


# Обработка callback-кнопки суммаризации
@dp.callback_query(news_obs.NewsCallback.filter(F.action == "summarize"))
async def process_summarize(callback_query: types.CallbackQuery, callback_data: news_obs.NewsCallback):
    news_id = int(callback_data.news_id)
    page = int(callback_data.page)
    await news_obs.get_keyboard_summarized_new(message=callback_query.message, news_id=news_id, page=page)


async def main() -> None:
    load_dotenv("../.env.local")
    TOKEN = os.getenv('BOT_TOKEN')
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


# Запуск бота
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
