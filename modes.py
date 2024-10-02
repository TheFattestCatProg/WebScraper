from async_util import fetch, save_article
from env import Env
from html_parser import HtmlParser
from streams import Stream
from util import paragraphs, sentences


# webscrapper.py can use functions with prefix mode_
# basic func decl: mode_name(env: Env, hp: HtmlParser, **kwargs)


async def mode_hub(
        env: Env, hp: HtmlParser, 
        /, *, 
        sel: str, next: str
):
    htmls = await hp.stream_select(sel).map(lambda i: env.url(i['href'])).awaitAll()
    await htmls.map(lambda h: env.rule(next, h)).awaitAll()


async def mode_loop(
        env: Env, hp: HtmlParser, 
        /, *, 
        sel: str, next: str
):
    url_hp = hp

    while True:
        await env.rule(next, url_hp)

        next_url = url_hp.select(sel)
        if not next_url: break

        url_hp = await env.url(next_url[0]['href'])


async def mode_article(
        env: Env, hp: HtmlParser, 
        /, *, 
        sel_title: str, sel_body: str, ignore: list[str],
        dir: str
):
    title = hp.select(sel_title)[0].text.strip()
    body = hp.select(sel_body)[0]
    pars = Stream(paragraphs(body, ignore)).map(sentences).filter().iter()

    await save_article(env.nfb, dir, title, pars)