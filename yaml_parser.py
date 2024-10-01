# Build parser from yaml-config & run
# to run: python [this-file] cfg.yaml

from argparse import ArgumentParser
from aiohttp import ClientSession
import yaml

from async_util import NameFabric, hand_worker
from html_parser import HtmlParser
from scrapper_base import ScrapperBase

import logging

logging.basicConfig(format='%(levelname)s %(name)s -> %(message)s', level=logging.DEBUG)


arg_parser = ArgumentParser()
arg_parser.add_argument('filename')


def bad_rule(*args):
    print("Bad rule: ", *args)
    exit(1)


def load_yaml(path: str):
    with open(path, 'r') as file:
        return yaml.safe_load(file)


class YamlScrapper(ScrapperBase):
    def __init__(self, session: ClientSession, name_fb: NameFabric, root_dir: str, cfg: dict) -> None:
        super().__init__(session, name_fb, root_dir)
        self._cfg = cfg

    @property
    def config(self):
        return self._cfg

    async def scrap(self):
        main_cfg = self.config['main']
        await route(self, await self.url_hp(main_cfg['url']), main_cfg['goto'])


async def route(scr: YamlScrapper, hp: HtmlParser, rule: str):
    curr_cfg = scr.config[rule]

    match curr_cfg['mode']:
        case 'cyclic':
            await mode_cyclic(scr, hp, curr_cfg['selector'], curr_cfg['goto'])
        case 'hub':
            await mode_hub(scr, hp, curr_cfg['selector'], curr_cfg['goto'])
        case 'article':
            await mode_article(scr, hp, curr_cfg['selector-title'], curr_cfg['selector-body'], curr_cfg['ignore'])
        case r:
            bad_rule(r)


async def mode_cyclic(scr: YamlScrapper, hp: HtmlParser, selector: str, goto: str):
    await scr.cyclic_a(hp, selector, lambda s, h: route(s, h, goto))


async def mode_hub(scr: YamlScrapper, hp: HtmlParser, selector: str, goto: str):
    await (await scr.hub_a(hp, selector)).map(lambda h: route(scr, h, goto)).awaitAll()


async def mode_article(scr: YamlScrapper, hp: HtmlParser, sel_title: str, sel_body: str, ignore: list[str]):
    await scr.save_article(scr.article(hp, sel_title, sel_body, ignore))


def main():
    args = arg_parser.parse_args()
    cfg = load_yaml(args.filename)

    async def hand(session: ClientSession):
        await YamlScrapper(session, NameFabric(), cfg['main']['dir'], cfg).scrap()

    hand_worker(hand)


if __name__ == "__main__":
    main()