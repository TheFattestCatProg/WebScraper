from types import ModuleType
from aiohttp import ClientSession
from async_util import NameFabric, fetch
from html_parser import HtmlParser


class Env:
    def __init__(
            self, 
            session: ClientSession, 
            name_fabric: NameFabric, 
            rules: dict,
            mode_module: ModuleType
    ) -> None:
        self._session = session
        self._name_fb = name_fabric
        self._rules = rules
        self._mode_mod = mode_module


    @property
    def session(self):
        return self._session
    
    @property
    def nfb(self):
        return self._name_fb
    
    @staticmethod
    def panic(*args):
        print(*args)
        exit(1)
    

    async def url(self, url: str) -> HtmlParser:
        return HtmlParser(await fetch(self._session, url))
    

    async def rule(self, name: str, hp: HtmlParser):            
        try:
            cfg: dict = self._rules[name]
        except KeyError:
            self.panic(f'Cannot find rule with name \'{name}\'')
        
        try:
            mode: str = cfg['mode']
        except KeyError:
            self.panic(f'Cannot find parameter \'mode\' in rule \'{name}\'')

        try:
            func: callable = getattr(self._mode_mod, f'mode_{mode.replace('-', '_')}')
        except AttributeError:
            self.panic(f'Cannot find mode with name \'{mode}\' in rule \'{name}\'')

        args = { k: cfg[k] for k in cfg if k != 'mode' }
        
        try:
            await func(self, hp, **args)
        except TypeError as e:
            self.panic(f'Error during executing mode \'{name}\':', e.args[0])


    async def main_rule(self):
        try:
            main = self._rules['main']
        except KeyError:
            self.panic('Cannot find \'main\' rule')
        
        try:
            url = main['url']
        except KeyError:
            self.panic(f'Cannot find parameter \'url\' in rule \'main\'')

        try:
            next = main['next']
        except KeyError:
            self.panic(f'Cannot find parameter \'name\' in rule \'main\'')

        await self.rule(next, await self.url(url))



