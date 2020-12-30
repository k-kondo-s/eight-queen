from models.model import Engine, Board
from utils.util import stop_watch
from typing import List, Tuple
import random
import datetime


class MinConflictsEngine(Engine):
    @stop_watch
    def __init__(self,
                 n: int,
                 version: int = 1) -> None:
        """initialize instance

        Args:
            n (int): length of chess board
            max_steps (int): the maximum number of attempts within searching
            version (int): version
        """
        self.n: int = n
        self.version: int = version

        self.max_steps: int = self.n * 100
        self.result_boards: List[Board] = []
        self.current_state: List[List[bool]] = [[False for _ in range(self.n)] for _ in range(self.n)]

        self.snapshot_state: List[List[bool]] = None
        self.random_ratio = max(self.n, 100)

        # for version 3
        self.unit_on_next_step: Tuple[int, int] = None

        # variables for debug
        self.debug_start_time: datetime.datetime = None
        self.debug_end_time: datetime.datetime = None
        self.debug_duration_seconds: int = 0
        self.debug_steps: int = 0

    @stop_watch
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

            # choose a unit that conflicts to the other one
            unit = self.choose_one_conflicts()

            # search the unit that has the minimum conflicts count to the other
            next_unit = self.search_next_unit(unit=unit)

            # move to the next
            self.move(previous=unit, after=next_unit)

        # return the current board if step reaches max_steps
        self.debug_steps = self.max_steps
        return self.convert_to_boards()

    @stop_watch
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
            conflicts_count, _ = self.get_conflicts_count(at=(row_num, column_num))

            # if there is a conflict, return the unit
            if conflicts_count != 0:
                return (row_num, column_num)

            # remove row_num from rows
            rows.remove(row_num)

    @stop_watch
    def search_next_unit(self, unit: Tuple[int, int], randomly: bool = True) -> Tuple[int, int]:
        """search a unit that has minimum conflicts count

        Args:
            previous (Tuple[int, int]): a unit
            randomly (bool): enable randomly choice from version 2. Default True
        Returns:
            next_unit (Tuple[int, int]): the next unit where a queen will move
        """
        given_row, given_column = unit

        if self.version >= 2 and randomly:
            # break ties randomly
            if self.break_ties_randomly():
                column = random.choice([i for i in range(self.n)])
                return (given_row, column)

        # if no queen exists at the given unit, return itself
        if not self.current_state[given_row][given_column]:
            return (given_row, given_column)

        if self.version < 4:
            # remove the queen at the given unit
            self.current_state[given_row][given_column] = False

        # generate conflicts count list
        conflicts_count_list = []
        conflicts_unit_list = []
        for column in range(self.n):
            count, conflict_units = self.get_conflicts_count(at=(given_row, column))
            conflicts_count_list.append(count)
            conflicts_unit_list.append(conflict_units)

        if self.version < 4:
            # restore
            self.current_state[given_row][given_column] = True

        # get the minumum conflicts count and its unit
        min_conflicts_count = min(conflicts_count_list)

        if self.version >= 4:
            # choose arbitrarily one from the list in which items has conflicts
            min_column_list = list(filter(lambda i: conflicts_count_list[i] == min_conflicts_count, range(len(conflicts_count_list))))
            while len(min_column_list) != 0:
                column = random.choice(min_column_list)
                if column != given_column:
                    self.unit_on_next_step = None
                    return (given_row, column)
                min_column_list.remove(column)
        else:
            # return the unit that is different from the given one
            for column_num in range(self.n):
                if conflicts_count_list[column_num] == min_conflicts_count and column_num != given_column:
                    # for version 3
                    if self.version >= 3:
                        # randomly choose the next unit and store it into self.next_unit
                        if len(conflicts_unit_list[column_num]) != 0:
                            self.unit_on_next_step = random.choice(conflicts_unit_list[column_num])
                    return (given_row, column_num)

        # return itself otherwise
        self.unit_on_next_step = None
        return (given_row, given_column)

    @stop_watch
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

    @stop_watch
    def initialize_current_board(self) -> None:
        """initialize the current board
        """
        if self.version >= 4:
            # list of assignable column (= Domain of row)
            columns = [i for i in range(self.n)]
            for row in range(self.n):

                # choose one from columns
                column = random.choice(columns)

                # assign initial value using also min-conflicts
                self.current_state[row][column] = True
                next_unit = self.search_next_unit(unit=(row, column))
                self.move(previous=(row, column), after=next_unit)

                # remove assigned column from columns
                columns.remove(column)

        elif self.version >= 2:
            # assign queens minimizing each conflicts counts
            column = None
            for row in range(self.n):
                if column is None:
                    column = random.choice([i for i in range(self.n)])

                self.current_state[row][column] = True

                # search the unit that has the minimum conflicts count to the other
                next_unit = self.search_next_unit(unit=(row, column), randomly=False)

                # move to the next
                self.move(previous=(row, column), after=next_unit)

                # set current column (which must have conflicts more than 1)
                column = next_unit[1]
        else:
            # randomly choose a initial state that does not violate constraints
            # about rows and columns
            columns = [i for i in range(self.n)]
            for row in range(self.n):
                column = random.choice(columns)
                self.current_state[row][column] = True
                columns.remove(column)

    @stop_watch
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
            conflicts_count, _ = self.get_conflicts_count(at=(row_num, column_num))
            if conflicts_count != 0:
                return False

        # otherwise, it's a solution
        return True

    @stop_watch
    def get_conflicts_count(self, at: Tuple[int, int]) -> Tuple[int, List[Tuple[int, int]]]:
        """count the conflicts count for the given location

        Args:
            at (Tuple[int, int]): unit (row, column)
        Returns:
            count (int): conflicts count
            conflict_list (Tuple[int, int]): conflict items [(row, column), ...]
        Note:
            (from version 4) the number of conflicts is generated by each new direction that queens can attack from.
            for example, if two queens would attack from the same direction, then the conflicts is
            counted once.
        """
        if self.version >= 4:
            given_row, given_column = at

            # define return values
            conflicts_count = 0
            conflicts_units = []

            # counts conflicts on the same column to the given
            for row in range(given_row - 1, -1, -1):
                if self.current_state[row][given_column]:
                    conflicts_count += 1
                    conflicts_units.append((row, given_column))
                    break
            for row in range(given_row + 1, self.n):
                if self.current_state[row][given_column]:
                    conflicts_count += 1
                    conflicts_units.append((row, given_column))
                    break

            # counts conflicts on the same diagonal up to the RIGHT
            diag_up = given_row + given_column
            for row in range(given_row - 1, -1, -1):
                column = diag_up - row
                if (0 <= column < self.n) and self.current_state[row][column]:
                    conflicts_count += 1
                    conflicts_units.append((row, column))
                    break
            for row in range(given_row + 1, self.n):
                column = diag_up - row
                if (0 <= column < self.n) and self.current_state[row][column]:
                    conflicts_count += 1
                    conflicts_units.append((row, column))
                    break

            # counts conflicts on the same diagonal up to the LEFT
            diag_down = given_row - given_column
            for row in range(given_row - 1, -1, -1):
                column = row - diag_down
                if (0 <= column < self.n) and self.current_state[row][column]:
                    conflicts_count += 1
                    conflicts_units.append((row, column))
                    break
            for row in range(given_row + 1, self.n):
                column = row - diag_down
                if (0 <= column < self.n) and self.current_state[row][column]:
                    conflicts_count += 1
                    conflicts_units.append((row, column))
                    break

            return conflicts_count, conflicts_units

        else:
            given_row, given_column = at

            # define units that should be checked
            # units = None
            conflict_count = 0
            conflict_items_on_different_row = []

            # items in the given row should be checked, except for itself
            units = self.current_state[given_row].copy()
            units.pop(given_column)
            conflict_count += sum(units)

            # items in the given column should be checked, except for itself
            for row in range(self.n):
                if row != given_row and self.current_state[row][given_column]:
                    conflict_count += 1
                    conflict_items_on_different_row.append((row, given_column))

            # items on the diagonal should be checked, except for itself
            # the time complexity is now O(n)
            diag_up = given_row + given_column
            diag_down = given_row - given_column
            for row in range(self.n):
                if row == given_row:
                    continue

                column_up = diag_up - row
                if (0 <= column_up < self.n) and self.current_state[row][column_up]:
                    conflict_count += 1
                    conflict_items_on_different_row.append((row, column_up))

                column_down = row - diag_down
                if (0 <= column_down < self.n) and self.current_state[row][column_down]:
                    conflict_count += 1
                    conflict_items_on_different_row.append((row, column_down))

            # return
            return conflict_count, conflict_items_on_different_row

    @stop_watch
    def convert_to_boards(self) -> List[Board]:
        """convert current state to Board

        Returns:
            boards (List[Board]): current state descirbed as Board
        Note:
            it returns a list but its length is always 1
        """
        # for debug
        self.debug_end_time = datetime.datetime.now()
        if self.debug_start_time is not None:
            self.debug_duration_seconds = (self.debug_end_time - self.debug_start_time).seconds

        b = Board(n=self.n)
        for i in range(self.n):
            for j in range(self.n):
                if self.current_state[i][j] is True:
                    b.set_queen(at=(i, j))
        return [b]

    @stop_watch
    def break_ties_randomly(self) -> bool:
        """return True or False randomly

        Args:
            exponent (int): the indicator of uniform distribution
        """
        if random.randint(0, self.random_ratio) == 0:
            return True
        return False
