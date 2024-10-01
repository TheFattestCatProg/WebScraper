from aiohttp import ClientSession
from async_util import *
from scrapper_base import ScrapperBase
from util import *
from html_parser import HtmlParser
import logging

URL = "https://eastern-lands.blogspot.com/"
SAVE_PATH = "results/eastern-lands/"
IGNORE_TAGS = ['table']


logging.basicConfig(format='%(levelname)s %(name)s -> %(message)s', level=logging.DEBUG)


class EasternLandsScrapper(ScrapperBase):
    async def scrap(self):
        await self.cyclic_a(await self.url_hp(URL), 'a.blog-pager-older-link', on_hub_page)


async def on_hub_page(scr: EasternLandsScrapper, hp: HtmlParser):
    articles = (await scr.hub_a(hp, '.post-title.entry-title > a')) \
                    .map(lambda hp: scr.article(hp, 'h3.post-title.entry-title', 'div.post-body.entry-content', IGNORE_TAGS))
    
    await scr.save_articles(articles)


async def main(session: ClientSession):
    await EasternLandsScrapper(session, NameFabric(), SAVE_PATH).scrap()


if __name__ == "__main__":
    hand_worker(main)