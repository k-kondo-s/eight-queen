from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Union


class Queen():
    pass


class Board():
    def __init__(self, n: int) -> None:
        """
        Args:
            n (int): length of the chess board
        """
        self.n: int = n
        self.board: List[List[Union[None, Queen]]] = None

        # initialize
        self.reset_board()

    def reset_board(self) -> None:
        """initialize board
        """
        # make n-chess board as a 2-dementional list
        self.board = [[None for _ in range(self.n)] for _ in range(self.n)]

    def has_queen(self, at: Tuple[int, int]) -> bool:
        """get value according to the coodinate
        Args:
            at (Tuple[int, int]): location (row, column)
        Returns:
            (bool): True if queen exists at the given place, else return False
        """
        row, column = at
        if self.board[row][column] is not None:
            return True
        return False

    def set_queen(self, at: Tuple[int, int]) -> None:
        """Set Queen onto the board
        Args:
            at (Tuple[int, int]): the place on the board where the queen is placed (row, column)
        """
        row_at, column_at = at
        self.board[row_at][column_at] = Queen()

    def remove_queen(self, at: Tuple[int, int]) -> None:
        """Remove Queen from the given place
        Args:
            at (Tuple[int, int]): the place where a queen will be removed from (row, column)
        """
        row_at, column_at = at
        self.board[row_at][column_at] = None

    def print(self) -> None:
        """Print the current state of the queens on the board
        """
        # insert a new line anyway
        print()

        # symbol of Queen on the board
        Q = 'Q'

        # maximum length of numbers as str
        max_len = len(str(self.n))

        # seperator
        sep = '-'.join(['-'.center(max_len, '-') for _ in range(self.n + 1)]) + '-'

        # print the top row
        top_row_list = [' '.center(max_len, ' ')]
        for i in range(self.n):
            top_row_list.append(str(i).center(max_len, ' '))
        top_row = '|'.join(top_row_list) + '|'
        print(top_row)
        print(sep)

        # print the board state
        for i in range(self.n):
            row_list = [str(i).center(max_len, ' ')]
            for j in self.board[i]:
                s = ' '.center(max_len, ' ') if j is None else Q.center(max_len, ' ')
                row_list.append(s)
            row = '|'.join(row_list) + '|'
            print(row)
            print(sep)


class Engine(metaclass=ABCMeta):
    @abstractmethod
    def solve(self, board: Board) -> List[Board]:
        pass
