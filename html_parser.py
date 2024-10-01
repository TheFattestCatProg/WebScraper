from typing import Any
from bs4 import BeautifulSoup, Tag
from streams import Stream


class HtmlParser(BeautifulSoup):
    def __init__(self, html: str):
        super().__init__(html, features='html.parser')


    def stream_select(
            self, 
            selector: str, 
            namespaces: Any | None = None,
            limit: int | None = None,
            **kwargs
    ) -> Stream[Tag]:
        return Stream(self.select(selector, namespaces, limit, **kwargs))