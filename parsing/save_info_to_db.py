import aiohttp
import aiomysql
from dotenv import load_dotenv
import os
import asyncio
from bs4 import BeautifulSoup
import re

from tone_model_creating.nlt_model_usage import get_tone

attractions = [
    "Мамаев курган",
    "Памятник «Родина-мать зовет!»",
    "Музей-заповедник «Сталинградская битва»",
    "Памятник-ансамбль «Героям Сталинградской битвы»",
    "Аллея Героев",
    "Скульптура «Скорбь матери»",
    "Набережная 62-й Армии",
    "Волгоградский планетарий",
    "Новый экспериментальный театр",
    "НЭТ",
    "Волжская ГЭС",
    "Пожарный пароход «Гаситель»",
    "Дом Павлова и мемориальная стена",
    "Музей изобразительных искусств имени Машкова",
    "Мемориальный комплекс «Лысая гора»",
    "Памятник Михаилу Паникахе",
    "Площадь Павших Борцов",
    "Мельница Гергардта",
    "Фонтан «Искусство»",
    "Фонтан «Дружбы народов»",
    "Памятник мирным жителям Сталинграда",
    "Речной вокзал",
    "Храм Иоанна Предтечи",
    "Парк Победы",
    "Музыкальный театр",
    "Памятник российскому казачеству «Казачья Слава»",
    "Памятник Петру и Февронии",
    "Стена Родимцева",
    "Остров Людникова",
    "Старая Сарепта",
    "Музей музыкальных инструментов",
    "Музей Сталина",
    "Областной краеведческий музей",
    "Музей Волго-Донского судоходного канала",
    "Площадь Чекистов и памятник чекистам",
    "Памятник собакам-истребителям танков",
    "Бронекатер БК-13",
    "Подземный трамвай",
    "Памятник морякам-североморцам",
    "Памятник Александру Невскому",
    "Храм Всех Святых на Мамаевом кургане",
    "Казанский кафедральный собор",
    "Музей «Память»",
    "Пожарная каланча",
    "Комсомольский сад",
    "Ботанический сад ВГПУ",
    "Парк Гагарина",
    "Волгоградский танцующий мост",
    "Детская железная дорога",
    "Мемориальное кладбище русских и немецких солдат",
    "Нулевой километр Волгограда",
    "Памятник Герою Советского Союза Виктору Хользунову"
]

persons = [
    "Бочаров Андрей",
    "Блошкин Александр",
    "Ларин Александр",
    "Бахин Валерий",
    "Костенко Денис",
    "Дорждеев Александр",
    "Кравченко Александр",
    "Харичкин Евгений",
    "Сиваков Александр",
    "Лисименко Наталья",
    "Воронин Игорь",
    "Горняков Сергей",
    "Глухов Алексей",
    "Иванов Роман",
    "Москвичев Евгений",
    "Лихачев Виталий",
    "Савченко Олег",
    "Вельможко Дмитрий",
    "Романов Виктор",
    "Семенов Василий",
    "Самохин Андрей",
    "Семисотов Николай",
    "Василевский Виктор",
    "Марченко Владимир",
    "Ирина Соловьева",
    "Шевцов Геннадий",
    "Шкарин Владимир",
    "Волоцков Алексей",
    "Мержоева Зина",
    "Писемская Анна",
    "Колесников Владлен",
    "Феодор Казанов",
    "Плотников Владимир",
    "Васильев Анатолий",
    "Голдобин Игорь",
    "Малашкин Александр",
    "Четвериков Сергей",
    "Треглазов Петр",
    "Иванов Василий",
    "Любавин Николай",
    "Нургалиев Ренат",
    "Сафонов Дмитрий",
    "Струк Михаил",
    "Керашев Асланбек",
    "Летунов Андрей",
    "Себелев Анатолий",
    "Струк Владимир",
    "Чехов Юрий",
    "Светлана Чиженькова",
    "Дмитрий Возжаев",
    "Александр Волоцков",
    "Олег Николаев",
    "Андрей Гимбатов",
    "Ирина Пешкова",
    "Максим Решетов",
    "Эльдор Азизов",
    "Михаил Битюцкий",
    "Роман Лучников",
    "Юрий Тупиков",
    "Владимир Петров",
    "Александр Бондаренко",
    "Сахаров Евгений",
    "Шурыгин Виктор",
    "Цуканов Алексей",
    "Шарифов Руслан",
    "Сивокоз Алексей",
    "Алтухов Евгений",
    "Быкадорова Галина",
    "Семенова Наталья",
    "Гасанов Руслан",
    "Бакулин Анатолий",
    "Костров Сергей",
    "Иванов Александр",
    "Савина Лариса",
    "Седов Юрий",
    "Просвернин Александр",
    "Рогачев Сергей",
    "Сударев Юрий",
    "Шефатов Владимир",
    "Шабунин Михаил",
    "Калашников Дмитрий",
    "Александр Навроцкий",
    "Медведев Дмитрий",
    "Ростовщиков Валерий",
    "Черепахин Вячеслав",
    "Грачев Михаил",
    "Зубарева Ольга",
    "Бухтина Татьяна",
    "Иващенко Владимир",
    "Стрельцова Наталья",
    "Фоминых Артем",
    "Гусева Ирина",
    "Ефимов Владимир",
    "Исинбаева Елена",
    "Гончаров Юрий",
    "Гречина Валентина",
    "Клочков Александр",
    "Князев Евгений",
    "Воронин Владимир",
    "Сычев Олег"
]


async def insert_attractions(pool, attraction):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO attractions (attractions_name) VALUES (%s) ON DUPLICATE KEY UPDATE attractions_name = attractions_name;",
                attraction)


async def insert_persons(pool, person):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO persons (persons_name) VALUES (%s) ON DUPLICATE KEY UPDATE persons_name = persons_name;",
                person)


async def get_news(pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT news_id, article FROM news")
            all_news = cursor.fetchall()
            res = await asyncio.gather(all_news)
            return res


async def get_news_to_tone(pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("select distinct n.news_id, n.article from news as n left join attractions_news as an on n.news_id = an.news_id left join persons_news as pn on n.news_id = pn.news_id where an.attractions_id is not null or pn.persons_id is not null;")
            all_news = cursor.fetchall()
            res = await asyncio.gather(all_news)
            return res


async def put_tone(pool, tone):
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(f"update news set sentiment = '{tone[1]}' where news_id = {tone[0]};")


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
    # all_news = await get_news(pool)
    # # print(all_news[0])
    # output_directory = 'news_texts'
    # os.makedirs(output_directory, exist_ok=True)
    # for new in all_news[0]:
    #     print(new[0])
    #     file_path = os.path.join(output_directory, f"{new[0]}.txt")
    #     with open(file_path, 'w', encoding='utf-8') as file:
    #         file.write(new[1])

    news_to_tone = await get_news_to_tone(pool)
    tones = get_tone(list(news_to_tone[0]))
    tasks = [put_tone(pool, tone) for tone in tones]
    await asyncio.gather(*tasks)

    pool.close()
    await pool.wait_closed()


if __name__ == "__main__":
    load_dotenv("../.env.local")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
