import datetime
from models.model import Board
from typing import Tuple
from functools import wraps

# make True if measure how long each function takes time
ENABLE_STOP_WATCH = False


def validate(board: Board) -> bool:
    """validate result
    Args:
        board (Board): board
    Returns:
        (bool): True if it's valid else False
    """
    n = board.n
    for row in range(n):
        for column in range(n):
            if is_collided(at=(row, column), board=board):
                return False
    return True


def is_collided(at: Tuple[int, int], board: Board) -> bool:
    """check collision for the given queen
    Args:
        at (Tupe[int, int]): the place of queen (row, column)
        boad (Board): Board
    Returns:
        (bool): True if the given queen can collide to the other one, else False
    """
    n = board.n

    # return False constantly if no queen exists at the given place
    if not board.has_queen(at=at):
        return False

    given_row, given_column = at
    for i in range(n):
        check_columns = [given_column]
        if i != given_row:
            # check diagonal
            distance = abs(i - given_row)
            if given_column - distance >= 0:
                check_columns.append(given_column - distance)
            if given_column + distance < n:
                check_columns.append(given_column + distance)
        else:
            # check all items in the given row except for itself
            check_columns = [k for k in range(n)]
            check_columns.remove(given_column)
        # check
        for column in check_columns:
            if board.has_queen(at=(i, column)):
                return True
    return False


def stop_watch(func):
    """stop watch wrapper
    """
    @wraps(func)
    def wrapper(*args, **kargs):
        if ENABLE_STOP_WATCH:
            start_time = datetime.datetime.now()
            result = func(*args, **kargs)
            duration_milliseconds = (datetime.datetime.now() - start_time) / datetime.timedelta(milliseconds=1)
            print(f'{func.__name__}: {duration_milliseconds}')
            return result
        else:
            return func(*args, **kargs)
    return wrapper
