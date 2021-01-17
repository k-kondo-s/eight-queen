
from models.model import Board
from typing import Dict
import time
import sys


class MinConflicts():
    # class variables
    COLUMN = 'column'
    DIAG_UP = 'diag_up'
    DIAG_DOWN = 'diag_down'

    def __init__(self, n: int) -> None:
        self.n: int = n

        self.MAX_STEPS: int = self.n * 100

        self.conflicts_num_dict: Dict[str, Dict[int, int]] = {MinConflicts.COLUMN: {}, MinConflicts.DIAG_UP: {}, MinConflicts.DIAG_DOWN: {}}
        for column in range(self.n):
            self.conflicts_num_dict[MinConflicts.COLUMN][column] = 0
        for diag_up in range(2 * self.n - 2 + 1):
            self.conflicts_num_dict[MinConflicts.DIAG_UP][diag_up] = 0
        for diag_down in range(- (self.n - 1), self.n - 1 + 1):
            self.conflicts_num_dict[MinConflicts.DIAG_DOWN][diag_down] = 0

        # variables for debug
        self.debug_start_time: float = None
        self.debug_end_time: float = None
        self.debug_duration_seconds: float = 0
        self.debug_steps: int = 0

    def solve(self) -> Board:
        """solve problem
        """
        # for debug
        self.debug_start_time = time.time()

        # do initial assignment of queens
        self.initialize_current_board()

        # loop for searching a solution until step reaches MAX_STEPS
        for step in range(self.MAX_STEPS):

            # return the solution if it's already had
            if self.has_solution():

                # for debug
                self.debug_end_time = time.time()
                self.debug_duration_seconds = self.debug_end_time - self.debug_start_time
                self.debug_steps = step

                # return
                return self.convert_to_board()

            # choose a next row we will deal with
            unit = self.choose_next_unit()

            # search the unit where the chosen queen will move
            next_unit = self.search_next_unit()

            # move to the next
            self.move(previous=unit, after=next_unit)

        # for debug
        self.debug_end_time = time.time()
        self.debug_duration_seconds = self.debug_end_time - self.debug_start_time
        self.debug_steps = self.MAX_STEPS

        # return
        return self.convert_to_board()

    def initialize_current_board(self) -> None:
        """initialize
        """
        pass

    def has_solution(self) -> bool:
        """check it has a solution
        """
        pass

    def convert_to_board(self) -> Board:
        """convert to Board
        """
        pass

    def choose_next_unit(self):
        """choose next one
        """
        pass

    def search_next_unit(self):
        """search next unit
        """
        pass

    def move(self, previous, after) -> None:
        """move
        """
        pass


if __name__ == '__main__':
    n = sys.argv[1] if len(sys.argv) >= 2 else 8
    e = MinConflicts(n=8)
    b = e.solve()
