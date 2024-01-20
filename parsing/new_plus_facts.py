import asyncio
import os
import shutil
import json

import Levenshtein
import aiomysql
from dotenv import load_dotenv


async def get_persons(pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT persons_id, persons_name FROM persons")
            all_persons = cursor.fetchall()
            res = await asyncio.gather(all_persons)
            return res


async def get_attractions(pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT attractions_id, attractions_name FROM attractions")
            all_attractions = cursor.fetchall()
            res = await asyncio.gather(all_attractions)
            return res


async def insert_persons_news(pool, st):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"INSERT INTO persons_news (persons_id, news_id) value ({st[0]}, {st[1]}) ON DUPLICATE KEY UPDATE news_id = news_id;")


async def insert_attrs_news(pool, st):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"INSERT INTO attractions_news (attractions_id, news_id) value ({st[0]}, {st[1]}) ON DUPLICATE KEY UPDATE news_id = news_id;")


def get_attrs_by_amount(amount: int, attrs):
    matching_attrs = []
    [matching_attrs.append(x) for x in attrs if len(x[1].split(' ')) == amount]
    return matching_attrs


def find_similar_attraction(mention, attractions):
    best_attr_match_id = None
    best_attr_similarity = 0
    mention = mention.lower()
    first_mention = mention.split(' ')[0]

    for possible_attr in attractions:
        poss_attr_id, poss_attr_text = possible_attr

        # if first_mention == poss_attr_text.lower().split(' ')[0]:
        similarity = Levenshtein.ratio(mention, poss_attr_text.lower())
        if similarity > best_attr_similarity:
            best_attr_similarity = similarity
            best_attr_match_id = poss_attr_id

    return best_attr_similarity, best_attr_match_id


def find_similar_person(mention, persons):
    best_pers_match_id = None
    best_pers_similarity = 0
    mention = mention.lower().split(' ')

    for possible_person in persons:
        poss_pers_id, poss_pers_text = possible_person
        poss_pers_text = poss_pers_text.lower().split(' ')

        # if mention[0] == poss_pers_text[0]:
        #     similarity = Levenshtein.ratio(mention[1], poss_pers_text[1])
        # elif mention[1] == poss_pers_text[0]:
        #     similarity = Levenshtein.ratio(mention[0], poss_pers_text[1])
        similarity = Levenshtein.ratio(mention[0], poss_pers_text[0]) + Levenshtein.ratio(mention[1], poss_pers_text[1])
        similarity2 = Levenshtein.ratio(mention[1], poss_pers_text[0]) + Levenshtein.ratio(mention[0], poss_pers_text[1])
        similarity = max(similarity, similarity2)


        if similarity > best_pers_similarity:
            best_pers_similarity = similarity
            best_pers_match_id = poss_pers_id

    return best_pers_similarity / 2, best_pers_match_id


async def main():
    pool = await aiomysql.create_pool(
        host=os.getenv("HOST"),
        port=int(os.getenv("PORT")),
        user=os.getenv("USER"),
        db=os.getenv("DATABASE"),
        password=os.getenv("PASSWORD"),
        loop=loop,
        autocommit=True
    )
    # Путь к JSON-файлу
    json_file_path = 'facts_ref.json'
    news_mentions = {}
    news_ids = []
    # Чтение
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        # Попробуем загрузить данные с учетом дополнительных квадратных скобок
        json_data = json.loads(json.dumps([json.loads(x) for x in json_file.read().split('][')]))

        # Проход по каждой записи в JSON-данных
        for entry in json_data:
            values = [fact["Field"][0]["Value"] for fact_group in entry.get("FactGroup", []) for fact in
                      fact_group.get("Fact", [])]
            news_id = entry.get("Url", "").replace("\\", "").replace(".txt", "")
            news_ids.append(news_id)
            news_mentions[f'{news_id}'] = values
    print(len(news_mentions))

    persons = await get_persons(pool)
    attractions = await get_attractions(pool)
    persons_news = []
    attractions_news = []
    # Проход по словарю
    for news_id, mentions in news_mentions.items():
        for mention in mentions:
            # print(news_id)
            # print(attractions_news)
            # print(persons_news)
            # разбиваем упоминание на слова
            words = mention.lower().split(' ')
            # потенциальные достопримечательности по кол-ву слов
            potential_attrs_matches = get_attrs_by_amount(len(words), attractions[0])

            sim, best_attr_match_id = find_similar_attraction(mention, potential_attrs_matches)

            # [print(f'{x},{sim}') for x in potential_attrs_matches if x[0] == best_attr_match_id]
            sim2 = 0
            if len(words) == 2:
                sim2, best_pers_match_id = find_similar_person(mention, persons[0])
                # [print(f'{x},{sim2}') for x in persons[0] if x[0] == best_pers_match_id]

                if sim > sim2 and best_attr_match_id is not None:
                    attractions_news.append([f'{best_attr_match_id}', news_id])

                elif best_pers_match_id is not None:
                    persons_news.append([f'{best_pers_match_id}', news_id])

            elif best_attr_match_id is not None:
                attractions_news.append([f'{best_attr_match_id}', news_id])

            # print(mention)
            # print(attractions_news)
            # print(persons_news)
            # print("----------")
    print(attractions_news[0])
    print(persons_news[0])

    put_a_n = [insert_attrs_news(pool, st) for st in attractions_news]
    put_p_n = [insert_persons_news(pool, st) for st in persons_news]
    #
    await asyncio.gather(*(put_a_n + put_p_n))
    pool.close()
    # await pool.wait_closed()


if __name__ == "__main__":
    load_dotenv("../.env.local")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
