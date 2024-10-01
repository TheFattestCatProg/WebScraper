from asyncio import run

from aiohttp import ClientSession
from bs4 import Tag

from async_util import NameFabric, fetch, hand_worker, save_article
from html_parser import HtmlParser
from streams import Stream
from util import sentences, paragraphs


async def main(session: ClientSession):
    # 'https://eastern-lands.blogspot.com/2019/03/blog-post.html'
    # 'https://eastern-lands.blogspot.com/2021/05/blog-post.html'
    # 'https://eastern-lands.blogspot.com/2024/07/dungeonmastery-as-soulcraft.html'

    hp = HtmlParser(await fetch(session, 'https://eastern-lands.blogspot.com/2021/05/blog-post.html'))

    l = hp.stream_select('div.post-body.entry-content').one()

    t = paragraphs(l, ['table'])

    #for i in t:
    #    print('!!!', i)

    sents = Stream(t).map(sentences).filter().list()

    for i in sents:
        print('%%%%%%', i)

    await save_article(NameFabric(), 'results', '111', sents)


if __name__ == "__main__":
    hand_worker(main)