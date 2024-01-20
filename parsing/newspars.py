import aiohttp
import aiomysql
from dotenv import load_dotenv
import os
import asyncio
from bs4 import BeautifulSoup
import re


async def pars_content(text, url):
    soup = BeautifulSoup(text, "lxml")
    title = soup.find("h1", class_ = "title-block").getText()
    date_time = soup.find("meta", itemprop = "datePublished").get("content")
    article_data = soup.find("article", class_ = "item block")
    article = " ".join([p.text for p in article_data.find_all("p")])

    return [title, article, date_time, url]


async def pars_links(content):
    pattern = re.compile(r'^/[a-z]+/[a-z-\d]+.html$')
    soup = BeautifulSoup(content, "lxml")
    articles = soup.find("div", class_ = "feed feed-items")

    return [link.get("href") for link in articles.find_all("a", href = pattern)]


async def pars_news(session, pool, link):
    url = f'https://gorvesti.ru/{link}'
    async with session.get(url) as response:
        text = await response.text()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                page = await pars_content(text, url)
                await cur.execute("INSERT INTO news (title, article, date_time, url) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE title = title;", page)


async def main():
    pool = await aiomysql.create_pool(
        host = os.getenv("HOST"),
        port = int(os.getenv("PORT")),
        user = os.getenv("USER"),
        db = os.getenv("DATABASE"),
        password = os.getenv("PASSWORD"),
        loop = loop,
        autocommit = True
    )
    types = ["politics","economics","business","society","culture","medical","sport","spectator","accidents","crime","education","blagoustr","kommunalka","infrastructure","transport","amazing"]
    async with aiohttp.ClientSession() as session:
        for type in types:
            for page in range(1, 101):
                base_url = f'https://gorvesti.ru/{type}/{page}'
                async with session.get(base_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        links = await pars_links(content)
                        tasks = [pars_news(session, pool, link) for link in links]
                        await asyncio.gather(*tasks)

    pool.close()
    await pool.wait_closed()


if __name__ == "__main__":
    load_dotenv("../.env.local")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

