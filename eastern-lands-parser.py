URL = "https://eastern-lands.blogspot.com/"
SAVE_PATH = "results/eastern-lands/"
IGNORE_TAGS = ['table']

from aiohttp import ClientSession
from bs4 import Tag
from async_util import *
from util import *
from html_parser import HtmlParser
import logging


logging.basicConfig(format='%(levelname)s %(name)s -> %(message)s', level=logging.DEBUG)


# * Возможность добавлять парсеры для других сайтов с минимально возможной 
# переработкой уже существующего кода.
# * Возможность задавать параметры запуска с помощью файла 
# конфигурации или аргументов командной строки
# * Чистый код
# * Приветствуется наличие модульных тестов

#title = bs.select('h3.post-title.entry-title')[0].text.strip()
#body = bs.select('div.post-body.entry-content')[0]


def text(t: Tag, ignore_tags: list[str]) -> list[str]:
    r = []

    for i in t.children:
        if i.name in ignore_tags:
            continue

        if isinstance(i, str):
            if (d := i.strip()):
                r.append(d)
        else:
            r += text(i, ignore_tags)

    return r


def article(hp: HtmlParser, title_selector: str, body_selector: str, ignore_tags: list[str]) -> Article:
    title = hp.select(title_selector)[0].text.strip()
    body = hp.select(body_selector, text=True)[0]
    paragraphs = [sentences(i) for i in text(body, ignore_tags)]

    return Article(title, paragraphs)


async def scrap_url(session: ClientSession, url: str, name_fabric: NameFabric) -> str:
    html_parser = HtmlParser(await fetch(session, url))

    html_articles = (
        await html_parser.stream_select('.post-title.entry-title > a')
            .map(lambda i: fetch(session, i['href']))
            .awaitAll()
    )

    await html_articles \
        .map(HtmlParser) \
        .map(lambda h: article(h, 'h3.post-title.entry-title', 'div.post-body.entry-content', IGNORE_TAGS)) \
        .map(lambda a: save_splitted(name_fabric, SAVE_PATH, a)) \
        .awaitAll()
    
    next_url = html_parser.select('a.blog-pager-older-link')
    if next_url:
        return next_url[0]['href']


async def main(session: ClientSession):
    url = URL
    name_fabric = NameFabric()
    while url:
        url = await scrap_url(session, URL, name_fabric)


if __name__ == "__main__":
    hand_worker(main)