from models.model import Board
from engine.simple_engine import SimpleEngine
import pytest
import datetime


def test_is_collided():
    """test fo is_collided
    """
    b = Board(n=4)
    b.set_queen(at=(0, 0))
    b.set_queen(at=(1, 2))
    b.set_queen(at=(2, 1))
    b.set_queen(at=(3, 3))
    b.print()
    e = SimpleEngine(board=b)
    r = e.validate(board=b)
    print(r)
    b = Board(n=5)
    b.set_queen(at=(0, 0))
    b.set_queen(at=(3, 1))
    b.set_queen(at=(1, 2))
    b.set_queen(at=(4, 3))
    b.set_queen(at=(2, 4))
    b.print()
    e = SimpleEngine(board=b)
    r = e.validate(board=b)
    print(r)


@pytest.mark.parametrize('i', [i for i in range(11)])
def test_solve(i):
    """test for solve()
    """
    b = Board(n=i)
    e = SimpleEngine(board=b)
    start_time = datetime.datetime.now()
    results = e.solve(board=b)
    end_time = datetime.datetime.now()
    duration_seconds = (end_time - start_time).seconds
    print(f'len(results) for {i}: {len(results)}, duration_seconds: {duration_seconds}')
