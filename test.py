from asyncio import run

from aiohttp import ClientSession
from bs4 import Tag

from async_util import fetch, hand_worker
from html_parser import HtmlParser


def text(t: Tag, ignore_tags: list[str] = []) -> list[str]:
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

async def main(session: ClientSession):
    hp = HtmlParser(await fetch(session, 'https://eastern-lands.blogspot.com/2019/03/blog-post.html'))

    l = hp.stream_select('div.post-body.entry-content').one()
    for i in text(l, ['table']):
        print('!!!', i)


if __name__ == "__main__":
    hand_worker(main)