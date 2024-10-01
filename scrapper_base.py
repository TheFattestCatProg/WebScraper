from typing import Callable
from aiohttp import ClientSession
from async_util import NameFabric, fetch, save_article
from dataclasses import dataclass as dt

from html_parser import HtmlParser
from streams import Stream
from util import sentences, paragraphs

@dt
class Article:
    title: str
    pars: list[list[str]]


class ScrapperBase:
    def __init__(self, session: ClientSession, name_fb: NameFabric, root_dir: str) -> None:
        self._session = session
        self._name_fb = name_fb
        self._root_dir = root_dir


    async def scrap(self):
        raise NotImplementedError


    @property
    def session(self):
        return self._session
    

    def article(self, hp: HtmlParser, title_selector: str, body_selector: str, ignore_tags: list[str]) -> Article:
        title = hp.select(title_selector)[0].text.strip()
        body = hp.select(body_selector, text=True)[0]
        pars = Stream(paragraphs(body, ignore_tags)).map(sentences).filter().list()

        return Article(title, pars)
    
    
    async def save_article(self, a: Article):
        await save_article(self._name_fb, self._root_dir, a.title, a.pars)
    

    async def save_articles(self, a: Stream[Article]):
        await a.map(lambda a: save_article(self._name_fb, self._root_dir, a.title, a.pars)).awaitAll()
    

    async def hub_a(self, hp: HtmlParser, url_selector: str) -> Stream[HtmlParser]:
        return (
            await hp.stream_select(url_selector)
                    .map(lambda i: i['href'])
                    .map(lambda u: fetch(self.session, u))
                    .awaitAll()
        ).map(HtmlParser)
    

    async def cyclic_a(self, hp: HtmlParser, next_selector: str, on_frame: Callable[['ScrapperBase', HtmlParser], None]):
        url_hp = hp

        while True:
            await on_frame(self, url_hp)

            next_url = url_hp.select(next_selector)
            if not next_url: break

            url_hp = await self.url_hp(next_url[0]['href'])


    async def url_hp(self, url: str) -> HtmlParser:
        return HtmlParser(await fetch(self.session, url))
