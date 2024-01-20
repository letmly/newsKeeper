from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database


# CallbackData для обработки callback-кнопок
class NewsCallback(CallbackData, prefix="my"):
    action: str
    news_id: int = 1
    page: int = 1


async def get_keyboard_news(message: types.Message, page: int = 1):
    news_list = await database.news_by_page(page)

    # Создаем клавиатуру с кнопками
    keyboard = InlineKeyboardBuilder()
    for news_item in news_list:
        button = InlineKeyboardButton(
            text=f"{news_item[1]}",
            callback_data=NewsCallback(action="view", news_id=news_item[0], page=page).pack()
        )
        keyboard.row(button)

    prev_b_act = "previous" if page > 1 else "nothing"
    prev_b_t = "◀" if page > 1 else ""
    prev_page_button = InlineKeyboardButton(
        text=prev_b_t,
        callback_data=NewsCallback(action=prev_b_act, page=page - 1).pack()
    )
    next_page_button = InlineKeyboardButton(
        text="▶",
        callback_data=NewsCallback(action="next", page=page + 1).pack()
    )
    keyboard.row(prev_page_button, next_page_button)

    # Отправляем клавиатуру с новостями в чат бота
    await message.edit_text(
        "Выберите новость",
        reply_markup=keyboard.as_markup()
    )


async def get_keyboard_details_news(message: types.Message, news_id, page):
    res = await database.news_details(news_id)
    details = res[0]

    news_title = details[1]
    news_article = details[2]
    news_data = details[3][0:10]
    news_url = details[4]
    details_text = f"**{news_title}**\n\n{news_article}\n\nДата: {news_data}\nСсылка: {news_url}\n"
    news_tone = details[5]

    if news_tone is not None:
        mentioned_persons = await database.persons_by_news(news_id)
        mentioned_attractions = await database.attrs_by_news(news_id)
        details_text += f"\nТональность новости: {news_tone}\n\nУпомянутые vip-персоны: {mentioned_persons}\n\nУпомянутые достопримечательности: {mentioned_attractions}"

    keyboard = InlineKeyboardBuilder()
    back_button = InlineKeyboardButton(
        text="Назад к новостям",
        callback_data=NewsCallback(action="back", page=page).pack()
    )
    keyboard.row(back_button)
    rewrite_button = InlineKeyboardButton(
        text="Переписать новость",
        callback_data=NewsCallback(action="rewrite", page=page, news_id=news_id).pack()
    )
    keyboard.row(rewrite_button)
    summarize_button = InlineKeyboardButton(
        text="Выделить главное",
        callback_data=NewsCallback(action="summarize", page=page, news_id=news_id).pack()
    )
    keyboard.row(summarize_button)

    await message.edit_text(
        text=f"Описание новости\n{details_text}",
        reply_markup=keyboard.as_markup()
    )


async def get_keyboard_rewrited_new(message: types.Message, news_id, page):
    res = await database.news_details(news_id)
    rewrited_article = await database.rewrite(res[0][2])

    keyboard = InlineKeyboardBuilder()
    button = InlineKeyboardButton(
        text="Вернуться к новости",
        callback_data=NewsCallback(action="view", news_id=news_id, page=page).pack()
    )
    keyboard.row(button)
    await message.edit_text(
        text=f"Новое описание: \n{rewrited_article}",
        reply_markup=keyboard.as_markup()
    )


async def get_keyboard_summarized_new(message: types.Message, news_id, page):
    res = await database.news_details(news_id)
    summarized_article = await database.summarize(res[0][2])

    keyboard = InlineKeyboardBuilder()
    button = InlineKeyboardButton(
        text="Вернуться к новости",
        callback_data=NewsCallback(action="view", news_id=news_id, page=page).pack()
    )
    keyboard.row(button)
    await message.edit_text(
        text=f"Главная информация: \n{summarized_article}",
        reply_markup=keyboard.as_markup()
    )


async def get_synonymous(message: types.Message, word: str):
    res = await database.syno_from_spark(word)
    if res is not None:
        await message.answer(f"Список найденных синонимов: {res}")
    else:
        await message.answer("похоже такого слова нет в словаре :(!")