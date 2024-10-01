from asyncio import run
from aiohttp import ClientSession
import aiofiles

from typing import Callable, Awaitable
import logging

logger = logging.getLogger(__name__)


class NameFabric:
    def __init__(self) -> None:
        self._next_id = 0

    def next_txt(self) -> str:
        self._next_id += 1
        return f'{self._next_id}.txt'


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


async def save_article(name_fabric: NameFabric, root_dir: str, title: str, paragraphs: list[list[str]]):
    logger.debug(f'Writing file "{root_dir}"...')

    name = f'{root_dir}/{name_fabric.next_txt()}'
    text = '\n\n'.join('\n'.join(p) for p in paragraphs)

    async with aiofiles.open(name, 'w') as file:
        await file.write(f'{title}\n\n')
        await file.write(text)
