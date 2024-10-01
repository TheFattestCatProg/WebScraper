import dataclasses
import logging

logger = logging.getLogger(__name__)

Sentence = str

@dataclasses.dataclass(repr=True)
class Article:
    title: str
    paragraphs: list[list[Sentence]]


class NameFabric:
    def __init__(self) -> None:
        self._next_id = 0

    def next_txt(self) -> str:
        self._next_id += 1
        return f'{self._next_id}.txt'


def isquote(c: str) -> bool:
    return c in ('"', "'", '«', '»')


def sentences(text: str) -> list[Sentence]:
    sentences = []
    begin_index = 0
    quote_opened = False

    text = f' {text.rstrip()} '

    for i, (c1, c2) in enumerate(zip(text, text[1:])):
        if isquote(c2):
            quote_opened = not quote_opened

        if c2.isspace() and c1 == '.' and not quote_opened:
            sentences.append(text[begin_index:i].strip())
            begin_index = i + 1

    if begin_index != len(text) - 1:
        sentences.append(text[begin_index:].strip())

    return sentences


##### ================= #####
##### ===== TESTS ===== #####
##### ================= #####


def test_sentences_1():
    assert sentences('abc. def. dfs.') == ['abc', 'def', 'dfs']

def test_sentences_2():
    assert sentences('abc. def. dfs') == ['abc', 'def', 'dfs']

def test_sentences_3():
    assert sentences('abc. def, dfs') == ['abc', 'def, dfs']

def test_sentences_4():
    assert sentences('abc. fds "Kek...!@!!!1. asd" - sad. kek.') == ['abc', 'fds "Kek...!@!!!1. asd" - sad', 'kek']

def test_sentences_5():
    assert sentences('«fda. f. .... !». abc') == ['«fda. f. .... !»', 'abc']

def test_sentences_6():
    assert sentences('abc kek.ru. kek') == ['abc kek.ru', 'kek']