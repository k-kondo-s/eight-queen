from models.model import Board, Engine
from typing import List, Tuple
from itertools import permutations


class SimpleEngine(Engine):
    def __init__(self, board: Board) -> None:
        self.board: Board = board
        self.n: int = self.board.n
        self.results: List[Board] = []

    def solve(self, board: Board) -> List[Board]:
        """solve problem using greedy search algolithm
        Args:
            board (Board): Board
        Returns:
            results (List[Board]): results
        """
        self.board = board
        self.n = self.board.n

        # greedy search
        for seq in permutations([i for i in range(self.n)]):
            b = Board(n=self.n)
            for j in range(self.n):
                b.set_queen(at=(j, seq[j]))
            if self.validate(board=b):
                self.results.append(b)
        return self.results

    def validate(self, board: Board) -> bool:
        """validate result
        Args:
            board (Board): board
        Returns:
            (bool): True if it's valid else False
        """
        for row in range(self.n):
            for column in range(self.n):
                if self.is_collided(at=(row, column), board=board):
                    return False
        return True

    def is_collided(self, at: Tuple[int, int], board: Board) -> bool:
        """check collision for the given queen
        Args:
            at (Tupe[int, int]): the place of queen (row, column)
            boad (Board): Board
        Returns:
            (bool): True if the given queen can collide to the other one, else False
        """
        # return True constantly if a queen exists at the given place
        if not board.exists(at=at):
            return False

        given_row, given_column = at
        for i in range(self.n):
            check_columns = [given_column]
            if i != given_row:
                # check diagonal
                distance = abs(i - given_row)
                if given_column - distance >= 0:
                    check_columns.append(given_column - distance)
                if given_column + distance < self.n:
                    check_columns.append(given_column + distance)
            else:
                # check all items in the given row except for itself
                check_columns = [k for k in range(self.n)]
                check_columns.remove(given_column)
            # check
            for column in check_columns:
                if board.exists(at=(i, column)):
                    return True
        return False
