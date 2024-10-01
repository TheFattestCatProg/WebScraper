from asyncio import run
from aiohttp import ClientSession
import aiofiles

from typing import Callable, Awaitable
from util import NameFabric, Article
import logging

logger = logging.getLogger(__name__)


def hand_worker(hand: Callable[[ClientSession], Awaitable[None]]):
    async def g():
        async with ClientSession() as session:
            await hand(session)

    run(g())


async def fetch(session: ClientSession, url: str) -> str:
    logger.debug(f'Fetching "{url}"...')

    resp = await session.get(url)
    resp.raise_for_status()
    html = await resp.text()
    return html


async def save_splitted(name_fabric: NameFabric, root_dir: str, article: Article):
    logger.debug(f'Writing file "{root_dir}"...')

    name = f'{root_dir}/{name_fabric.next_txt()}'
    text = '\n\n'.join('\n'.join(p) for p in article.paragraphs)

    async with aiofiles.open(name, 'w') as file:
        await file.write(f'{article.title}\n\n')
        await file.write(text)
