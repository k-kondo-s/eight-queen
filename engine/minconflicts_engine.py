from models.model import Engine, Board
from typing import List, Tuple
import math
import random
import datetime


class MinConflictsEngine(Engine):
    def __init__(self,
                 n: int,
                 max_steps: int = int(math.pow(10, 7))) -> None:
        """initialize instance

        Args:
            n (int): length of chess board
            max_steps (int): the maximum number of attempts within searching
        """
        self.n: int = n
        self.max_steps: int = max_steps

        self.result_boards: List[Board] = []
        self.current_state: List[List[bool]] = [[False for _ in range(self.n)] for _ in range(self.n)]

        self.snapshot_state: List[List[bool]] = None

        # variables for debug
        self.debug_start_time: datetime.datetime = None
        self.debug_end_time: datetime.datetime = None
        self.debug_duration_seconds: int = 0
        self.debug_steps: int = 0

    def solve(self) -> List[Board]:
        """solve problem

        Returns:
            boards (List[Boards]): the list of result boards
        """
        # for debug
        self.debug_start_time = datetime.datetime.now()

        # initialize current board
        self.initialize_current_board()

        # loop for searching a solution until step reaches max_steps
        for step in range(self.max_steps):

            # return the current board if it's already had a solution
            if self.has_solution():
                self.debug_steps = step
                return self.convert_to_boards()

            # return the current board if the current board is the same about 1,000 steps ago
            if step % 1000 == 0:
                if self.snapshot_state == self.current_state:
                    self.debug_steps = step
                    return self.convert_to_boards()
                self.snapshot_state = self.current_state.copy()

            # choose a unit that conflicts to the other one
            unit = self.choose_one_conflicts()

            # search the unit that has the minimum conflicts count to the other
            next_unit = self.search_next_unit(unit=unit)

            # move to the next
            self.move(previous=unit, after=next_unit)

        # return the current board if step reaches max_steps
        self.debug_steps = self.max_steps
        return self.convert_to_boards()

    def choose_one_conflicts(self) -> Tuple[int, int]:
        """randomly choose a unit that conflicts to the other

        Returns:
            unit (Tuple[int, int]): a unit where a queen exists and has conflicts to someone
        """
        rows = [i for i in range(self.n)]
        while len(rows) != 0:
            # randomly choose one from rows
            row_num = random.choice(rows)

            # find column where a queen exists
            column_num = self.current_state[row_num].index(True)

            # check conflicts at the unit
            conflicts_count = self.get_conflicts_count(at=(row_num, column_num))

            # if there is a conflict, return the unit
            if conflicts_count != 0:
                return (row_num, column_num)

            # remove row_num from rows
            rows.remove(row_num)

    def search_next_unit(self, unit: Tuple[int, int]) -> Tuple[int, int]:
        """search a unit that has minimum conflicts count

        Args:
            previous (Tuple[int, int]): a unit
        Returns:
            next_unit (Tuple[int, int]): the next unit where a queen will move
        """
        given_row, given_column = unit

        # if no queen exists at the given unit, return itself
        if not self.current_state[given_row][given_column]:
            return (given_row, given_column)

        # remove the queen at the given unit
        self.current_state[given_row][given_column] = False

        # generate conflicts count list
        conflicts_count_list = [self.get_conflicts_count(at=(given_row, column)) for column in range(self.n)]

        # restore
        self.current_state[given_row][given_column] = True

        # get the minumum conflicts count and its unit
        min_conflicts_count = min(conflicts_count_list)

        # return the unit different from the given one
        for column_num in range(self.n):
            if conflicts_count_list[column_num] == min_conflicts_count and column_num != given_column:
                return (given_row, column_num)

        # return itself otherwise
        return (given_row, given_column)

    def move(self, previous: Tuple[int, int], after: Tuple[int, int]) -> None:
        """move a queen to the next unit

        Args:
            previous (Tuple[int, int]): the previous unit
            after (Tuple[int, int]): the next unit where a queen will move
        """
        previous_row, previous_column = previous
        after_row, after_column = after

        # if there is no queen at the given unit, raise error
        if not self.current_state[previous_row][previous_column]:
            raise Exception(f'there is no queen at the previous unit {previous}')

        # move from the previous to the after
        self.current_state[previous_row][previous_column] = False
        self.current_state[after_row][after_column] = True

    def initialize_current_board(self) -> None:
        """initialize the current board
        """
        # randomly choose a initial state that does not violate constraints
        # about rows and columns
        columns = [i for i in range(self.n)]
        for row in range(self.n):
            column = random.choice(columns)
            self.current_state[row][column] = True
            columns.remove(column)

    def has_solution(self) -> bool:
        """check if the current board is a solution

        Returns:
            (bool): True if it's a solution
        """
        for row_num in range(self.n):
            # it's not a solution if more than 2 queens exists on a same row
            if sum(self.current_state[row_num]) != 1:
                return False

            # it's not a solution if a queen has some conflicts
            column_num = self.current_state[row_num].index(True)
            conflicts_count = self.get_conflicts_count(at=(row_num, column_num))
            if conflicts_count != 0:
                return False

        # otherwise, it's a solution
        return True

    def get_conflicts_count(self, at: Tuple[int, int]) -> int:
        """count the conflicts count for the given location

        Args:
            at (Tuple[int, int]): unit (row, column)
        Returns:
            count (int): conflicts count
        """
        given_row, given_column = at

        # define units that should be checked
        units = None

        # items in the given row should be checked, except for itself
        units = self.current_state[given_row].copy()
        units.pop(given_column)

        # items in the given column should be checked, except for itself
        for row in range(self.n):
            if row != given_row:
                units.append(self.current_state[row][given_column])

        # items on the diagonal should be checked, except for itself
        diag_up = given_row + given_column
        diag_down = given_row - given_column
        for row in range(self.n):
            for column in range(self.n):
                if row == given_row and column == given_column:
                    continue
                if row + column == diag_up or row - column == diag_down:
                    units.append(self.current_state[row][column])

        # sum the conflicts
        sum_result = sum(units)

        # return
        return sum_result

    def convert_to_boards(self) -> List[Board]:
        """convert current state to Board

        Returns:
            boards (List[Board]): current state descirbed as Board
        Note:
            it returns a list but its length is always 1
        """
        # for debug
        self.debug_end_time = datetime.datetime.now()
        if self.debug_end_time is not None:
            self.debug_duration_seconds = (self.debug_end_time - self.debug_start_time).seconds

        b = Board(n=self.n)
        for i in range(self.n):
            for j in range(self.n):
                if self.current_state[i][j] is True:
                    b.set_queen(at=(i, j))
        return [b]
