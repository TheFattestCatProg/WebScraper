from typing import TypeVar, Iterable, Generic, Callable, Coroutine
from asyncio import gather

T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')
H = TypeVar('H')
class Stream(Generic[T]):
    def __init__(self, iter_: Iterable[T]) -> None:
        self._iter = iter(iter_)


    def filter(self, f: Callable[[T], bool] = lambda i: i) -> 'Stream[T]':
        return Stream(i for i in self._iter if f(i))
    

    def map(self, f: Callable[[T], U]) -> 'Stream[U]':
        return Stream(f(i) for i in self._iter)
    

    def flat_map(self, f: Callable[[T], Iterable[U]]) -> 'Stream[U]':
        usual_map = (f(i) for i in self._iter)
        return Stream(j for i in usual_map for j in i)
    

    def reduce(self, start: U, f: Callable[[U, T], U]) -> U:
        r = start

        for i in self._iter:
            r = f(r, i)
        
        return r
    

    async def awaitAll(self: 'Stream[Coroutine[H, U, V]]') -> 'Stream[V]':
        return Stream(i for i in await gather(*self._iter))
    

    def take(self, n: int) -> list[T]:
        return [next(self._iter) for _ in range(n)]
    

    def takes(self, n: int) -> 'Stream[T]':
        return Stream(self.take(n))


    def list(self) -> list[T]:
        return list(self._iter)
    
    
    def set(self) -> set[T]:
        return set(self._iter)


    def iter(self) -> Iterable[T]:
        return self._iter
    

    def one(self) -> T:
        return next(self._iter)
    

##### ================= #####
##### ===== TESTS ===== #####
##### ================= #####


def test_filter():
    assert Stream(range(10)).filter(lambda i: i % 2 == 0).list() == [0, 2, 4, 6, 8]


def test_map():
    assert Stream([1, 2, 3]).map(str).list() == ['1', '2', '3']


def test_flat_map():
    assert Stream([[1, 2], [3, 4, 5]]).flat_map(lambda i: i).list() == [1, 2, 3, 4, 5]


def test_reduce():
    assert Stream(range(1, 6)).reduce('', lambda i, j: i + str(j)) == '12345'


def test_take():
    assert Stream([1, 2, 3, 4, 5]).take(3) == [1, 2, 3]


def test_takes():
    assert Stream([1, 2, 3, 4, 5]).takes(3).list() == [1, 2, 3]


def test_one():
    assert Stream([1, 2, 3]).one() == 1