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

        # initialize
        self.initialize_board()

    def initialize_board(self) -> None:
        """initialize board
        """
        # make n-chess board as a 2-dementional list
        self.board: List[Union[None, Queen]] = [[None for _ in range(self.n)] for _ in range(self.n)]

    def set_queen(self, at: Tuple[int, int]) -> None:
        """Set Queen onto the board
        Args:
            at (Tuple[int, int]): the place on the board where the queen is placed (row, column)
        """
        row_at, column_at = at
        self.board[row_at][column_at] = Queen()

    def print(self) -> None:
        """Print the current state of the queens on the board
        """
        # symbol of the Queen
        Q = 'Q'

        # maximum length of numbers as str
        max_len = len(str(self.n))

        # seperator
        sep = '-'.join(['-'.center(max_len, '-') for _ in range(self.n + 1)])

        # show the top row
        top_row_list = [' '.center(max_len, ' ')]
        for i in range(self.n):
            top_row_list.append(str(i).center(max_len, ' '))
        top_row = '|'.join(top_row_list) + '|'
        print(top_row)
        print(sep)

        # show the board
        for i in range(self.n):
            row_list = [str(i).center(max_len, ' ')]
            for j in self.board[i]:
                s = ' '.center(max_len, ' ') if j is None else Q.center(max_len, ' ')
                row_list.append(s)
            row = '|'.join(row_list) + '|'
            print(row)
            print(sep)


if __name__ == '__main__':
    b = Board(n=8)
    b.set_queen(at=(2, 3))
    b.print()
    b.initialize_board()
    b.print()
