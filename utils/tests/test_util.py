from models.model import Board
from utils.util import is_collided, validate


def test_is_collided():
    """test for is_collided
    """
    # case 1: collided
    b = Board(n=2)
    b.set_queen(at=(0, 0))
    b.set_queen(at=(0, 1))
    b.set_queen(at=(1, 0))
    assert is_collided(at=(0, 0), board=b)
    assert is_collided(at=(0, 1), board=b)
    assert is_collided(at=(1, 0), board=b)

    # case 2: no collided
    b = Board(n=2)
    b.set_queen(at=(0, 0))
    assert not is_collided(at=(0, 0), board=b)
    assert not is_collided(at=(0, 1), board=b)
    assert not is_collided(at=(1, 0), board=b)


def test_validate():
    """test for validate
    """
    # True
    b = Board(n=3)
    b.set_queen(at=(0, 0))
    b.set_queen(at=(1, 2))
    assert validate(board=b)

    # False
    b = Board(n=3)
    b.set_queen(at=(0, 0))
    b.set_queen(at=(1, 2))
    b.set_queen(at=(2, 1))
    assert not validate(board=b)
