import os
import httpx
import aiomysql
from dotenv import load_dotenv


# Функция для создания асинхронного подключения к базе данных
async def create_db_pool():
    load_dotenv("../.env.local")
    return await aiomysql.create_pool(
        host=os.getenv("HOST"),
        port=int(os.getenv("PORT")),
        user=os.getenv("USER"),
        db=os.getenv("DATABASE"),
        password=os.getenv("PASSWORD"),
        autocommit=True
    )


async def news_by_page(page):
    if page < 0:
        print("wrong page")
        return []
    else:
        pool = await create_db_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Получаем последние новости из базы данных
                await cursor.execute(f"SELECT * FROM news ORDER BY date_time DESC LIMIT 10 OFFSET {(page - 1) * 10};")
                news_list = await cursor.fetchall()
                return news_list


async def persons_by_news(news_id):
    pool = await create_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                f'SELECT persons.persons_name from persons JOIN persons_news ON persons.persons_id = persons_news.persons_id WHERE persons_news.news_id = {news_id};')
            persons = await cursor.fetchall()
            if len(persons):
                res = [person for person in persons[0]]
                return res
            else:
                return ""


async def attrs_by_news(news_id):
    pool = await create_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                f'SELECT attractions.attractions_name from attractions JOIN attractions_news ON attractions.attractions_id = attractions_news.attractions_id WHERE attractions_news.news_id = {news_id};')
            attractions = await cursor.fetchall()
            if len(attractions):
                res = res = [attr for attr in attractions[0]]
                return res
            else:
                return ""


async def news_details(news_id: int):
    pool = await create_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            # Получаем последние новости из базы данных
            await cursor.execute(f"SELECT * FROM news WHERE news_id =  {news_id};")
            details = await cursor.fetchall()
            return details


async def get_new_article(text_to_rewrite):
    url = 'https://api.aicloud.sbercloud.ru/public/v2/rewriter/predict'
    headers = {'Content-Type': 'application/json'}
    data = {
        "instances": [
            {
                "text": f"{text_to_rewrite[:1000]}",
                "temperature": 0.9,
                "top_k": 50,
                "top_p": 0.7,
                "range_mode": "bertscore"
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        return response.json()["prediction_best"]["bertscore"]


async def rewrite(news_article):
    res = await get_new_article(news_article)
    return res


async def get_summarized(text_to_sum):
    url = 'https://api.aicloud.sbercloud.ru/public/v2/summarizator/predict'
    headers = {'Content-Type': 'application/json'}
    data = {
        "instances": [
            {
                "text": f"{text_to_sum[:1000]}",
                "num_beams": 5,
                "num_return_sequences": 3,
                "length_penalty": 0.5
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        return response.json()["prediction_best"]["bertscore"]


async def summarize(news_article):
    res = await get_summarized(news_article)
    return res


async def syno_from_spark(word):
    url = 'localhost'
    headers = {'Content-Type': 'application/json'}
    data = {
        "word": f"{word}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        res = await response.json()["prediction_best"]["bertscore"]

    return res
