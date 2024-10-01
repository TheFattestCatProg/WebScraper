from bs4 import Tag
from streams import Stream


def isquote(c: str) -> bool:
    return c in ('"', "'", '«', '»')


def sentences(text: str) -> list[str]:
    sentences = []
    begin_index = 0
    quote_opened = False

    text = f' {text.rstrip()} '

    for i, (c1, c2) in enumerate(zip(text, text[1:])):
        if isquote(c2):
            quote_opened = not quote_opened

        if c2.isspace() and c1 == '.' and not quote_opened:
            if d := text[begin_index:i].strip():
                sentences.append(d)
            begin_index = i + 1

    if begin_index != len(text) - 1:
        if d := text[begin_index:].strip():
            sentences.append(d)

    return sentences


def paragraphs(tag: Tag | str, ignore_tags: list[str]) -> list[str]:
    if isinstance(tag, str):
        if (d := tag.strip()):
            return [ d ]
        else:
            return []

    is_text = False

    for i in tag.children:
        if isinstance(i, str) and i.strip():
            is_text = True
        elif i.name == 'p':
            is_text = False
            break

    if is_text:
        return Stream(tag.text.split('\n')) \
                .map(str.strip)             \
                .filter()                   \
                .list()

    return Stream(tag.children) \
            .filter(lambda i: i.name not in ignore_tags)    \
            .flat_map(lambda i: paragraphs(i, ignore_tags)) \
            .list()


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

def test_sentences_7():
    assert sentences('.') == []