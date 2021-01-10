from models.model import Engine, Board
from utils.util import stop_watch
from typing import Dict, List, Tuple, Set
import random
import datetime


class MinConflictsEngine(Engine):
    COLUMN = 'column'
    DIAG_UP = 'diag_up'
    DIAG_DOWN = 'diag_down'

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

        # constant
        self.all_list: List[int] = [i for i in range(self.n)]

        self.max_steps: int = self.n * 100
        self.result_boards: List[Board] = []
        self.current_state: List[List[bool]] = [[False for _ in range(self.n)] for _ in range(self.n)]

        self.snapshot_state: List[List[bool]] = None
        self.random_ratio = max(self.n, 100)

        # variables to manage conflicts count, which makes the time complexity O(n)
        self.conflicts_table: List[List[int]] = [[0 for _ in range(self.n)] for _ in range(self.n)]
        # TODO: いらんかも
        self.conflicts_dict: Dict[int, Dict[int, Set[int]]] = {row: {attaks: set() for attaks in range(0, 7)} for row in range(self.n)}
        for row in self.conflicts_dict.keys():
            self.conflicts_dict[row][0] = {column for column in range(self.n)}
        
        # from version 6
        self.conflicts_num_dict: Dict[str, Dict[int, int]] = {MinConflictsEngine.COLUMN: {}, MinConflictsEngine.DIAG_UP: {}, MinConflictsEngine.DIAG_DOWN: {}}
        for column in range(self.n):
            self.conflicts_num_dict[MinConflictsEngine.COLUMN][column] = 0
        for diag_up in range(2 * self.n - 2 + 1):
            self.conflicts_num_dict[MinConflictsEngine.DIAG_UP][diag_up] = 0
        for diag_down in range(- (self.n - 1), self.n - 1 + 1):
            self.conflicts_num_dict[MinConflictsEngine.DIAG_DOWN][diag_down] = 0

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
        TODO: this function actually needs only row information, while column's one is not needed, so it needs to be modified to fit into it
        """
        given_row, given_column = unit

        if self.version >= 2 and randomly:
            # break ties randomly
            if self.break_ties_randomly():
                column = random.randint(0, self.n - 1)
                return (given_row, column)

        if self.version < 5:
            # if no queen exists at the given unit, return itself
            # Note: it can be deleted, so it is no longer needed to set True to the (row, column) beforehand
            if not self.current_state[given_row][given_column]:
                return (given_row, given_column)

        if self.version < 4:
            # remove the queen at the given unit
            self.current_state[given_row][given_column] = False

        if self.version >= 6:
            min_count = self.n
            count_list = []
            for column in range(self.n):
                current_count = self.conflicts_num_dict[MinConflictsEngine.COLUMN][column]
                current_count += self.conflicts_num_dict[MinConflictsEngine.DIAG_UP][given_row + column]
                current_count += self.conflicts_num_dict[MinConflictsEngine.DIAG_DOWN][given_row - column]
                if current_count < min_count:
                    count_list.append((column, current_count))
                    min_count = current_count
            random.shuffle(count_list)
            for column, c in count_list:
                if c == min_count:
                    return (given_row, column)
            
        elif self.version >= 5:
            min_conflict_count_ver5 = min(self.conflicts_table[given_row])
            random.shuffle(self.all_list)
            for column in self.all_list:
                if self.conflicts_table[given_row][column] == min_conflict_count_ver5:
                    return (given_row, column)
            # for i in range(self.n):
            #     column = (given_column + i) % self.n
            #     if self.conflicts_table[given_row][column] == min_conflict_count_ver5:
            #         return (given_row, column)
        else:
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
        if self.version >= 5:
            self.remove_queen(at=(previous_row, previous_column))
            self.put_queen(at=(after_row, after_column))
        else:
            self.current_state[previous_row][previous_column] = False
            self.current_state[after_row][after_column] = True

    @stop_watch
    def initialize_current_board(self, debug_row=None) -> None:
        """initialize the current board
        """
        if self.version >= 6:
            for row in range(self.n):
                if debug_row is not None and debug_row == row:
                    return None
                
                # debug
                column = 0
                if row != 0:
                    column = self.current_state[row - 1].index(True)
                next_unit = self.search_next_unit(unit=(row, column), randomly=False)
                self.put_queen(at=next_unit)



                # column = row * 2
                # if column >= self.n:
                #     column = 2 * (row - (((self.n + 1) // 2))) + 3
                # if row == self.n - 1:
                #     column = 1
                # self.put_queen(at=(row, column))

        elif self.version >= 4:
            # list of assignable column (= Domain of row)
            columns = [i for i in range(self.n)]
            for row in range(self.n):

                # choose one from columns
                column = random.choice(columns)

                # assign initial value using also min-conflicts
                if self.version >= 5:
                    next_unit = self.search_next_unit(unit=(row, column), randomly=False)
                    self.put_queen(at=next_unit)
                else:
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
        TODO: make O(n^2) O(n)
        """
        if self.version >= 6:
            for row in range(self.n):
                column = self.current_state[row].index(True)
                if self.conflicts_num_dict[MinConflictsEngine.COLUMN][column] != 1:
                    return False
                if self.conflicts_num_dict[MinConflictsEngine.DIAG_UP][row + column] != 1:
                    return False
                if self.conflicts_num_dict[MinConflictsEngine.DIAG_DOWN][row - column] != 1:
                    return False
        else:
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
        if self.version >= 6:
            given_row, given_column = at
            current_count = self.conflicts_num_dict[MinConflictsEngine.COLUMN][given_column]
            current_count += self.conflicts_num_dict[MinConflictsEngine.DIAG_UP][given_row + given_column]
            current_count += self.conflicts_num_dict[MinConflictsEngine.DIAG_DOWN][given_row - given_column]
            return current_count, None

        if self.version >= 5:
            given_row, given_column = at
            return self.conflicts_table[given_row][given_column], None

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

    @stop_watch
    def put_queen(self, at: Tuple[int, int]) -> None:
        """put queen on the board

        also, update conflicts table

        Args:
            at (Tuple[int, int]): the place where the given queen is putted
        """
        given_row, given_column = at

        # put queen
        self.current_state[given_row][given_column] = True

        if self.version >= 6:
            self.conflicts_num_dict[MinConflictsEngine.COLUMN][given_column] += 1
            self.conflicts_num_dict[MinConflictsEngine.DIAG_UP][given_row + given_column] += 1
            self.conflicts_num_dict[MinConflictsEngine.DIAG_DOWN][given_row - given_column] += 1
        else:
            # update conflicts table
            items = self.get_updated_items(at=at)
            for item in items:
                row, column = item
                # TODO
                # count = self.conflicts_table[row][column]

                # remove column from conflict_dict
                # TODO:
                # self.conflicts_dict[row][count].remove(column)

                # update conflicts count
                new_count = self.conflicts_table[row][column] + 1
                self.conflicts_table[row][column] = new_count

                # add column to conflict_dict
                # TODO
                # self.conflicts_dict[row][new_count].add(column)

    @stop_watch
    def remove_queen(self, at: Tuple[int, int]) -> None:
        """remove queen on the board

        also, update conflicts table

        Args:
            at (Tuple[int, int]): the place where the queen will be removed
        Note:
            This function updates conflicts_table
            This also considers the care in `put_queen` function
        """
        given_row, given_column = at

        # remove queen
        self.current_state[given_row][given_column] = False

        if self.version >= 6:
            self.conflicts_num_dict[MinConflictsEngine.COLUMN][given_column] -= 1
            self.conflicts_num_dict[MinConflictsEngine.DIAG_UP][given_row + given_column] -= 1
            self.conflicts_num_dict[MinConflictsEngine.DIAG_DOWN][given_row - given_column] -= 1
        else:
            # update conflicts table
            items = self.get_updated_items(at=at)
            for item in items:
                row, column = item
                # TODO
                # count = self.conflicts_table[row][column]

                # remove column from conflict_dict
                # TODO
                # self.conflicts_dict[row][count].remove(column)

                # update conflicts count
                new_count = self.conflicts_table[row][column] - 1
                self.conflicts_table[row][column] = new_count

                # add column to conflict_dict
                # TODO
                # self.conflicts_dict[row][new_count].add(column)

    def get_updated_items(self, at: Tuple[int, int]) -> List[Tuple[int, int]]:
        """get items that have possiblity to be updated on conflicts table

        Args:
            at (Tuple[int, int]): the place to be putted
        Returns:
            columns (List[Tuple[int, int]]): list of columns that might be updated on conflicts table
        Note:
            This function updates conflicts_table.
            There are only 3 situations when putting a new queen on a line (column or diagonals):
                (1): no queen exists on each side
                (2): a queen exists on one side
                (3): two queens exist on each side
            When we put a new queen, we have to update conflicts table considering the above situations.
        """
        given_row, given_column = at

        # update conflicts_table
        updated_items = []

        # first, check items to be updated on the same column
        conflicts_rows = []
        for row in range(given_row - 1, -1, -1):
            if self.current_state[row][given_column]:
                conflicts_rows.append(row)
                break
        for row in range(given_row + 1, self.n):
            if self.current_state[row][given_column]:
                conflicts_rows.append(row)
                break
        if len(conflicts_rows) == 2:
            # the queen is between two queens, so do nothing
            pass
        elif len(conflicts_rows) == 1:
            target_row = conflicts_rows[0]
            # there is a queen on one side, so update conflict table
            updated_items += [(r, given_column) for r in range(min(given_row, target_row), max(given_row, target_row) + 1)]
            updated_items.remove((given_row, given_column))
        else:
            # there is no queen before putting a new, so update conflict table
            updated_items += [(r, given_column) for r in range(0, self.n)]
            updated_items.remove((given_row, given_column))

        # second, check items to be updated on the diag up
        conflicts_rows_diag_up = []
        diag_up = given_row + given_column
        for row in range(given_row - 1, -1, -1):
            column = diag_up - row
            if column < 0 or self.n <= column:
                break
            if self.current_state[row][column]:
                conflicts_rows_diag_up.append(row)
                break
        for row in range(given_row + 1, self.n):
            column = diag_up - row
            if column < 0 or self.n <= column:
                break
            if self.current_state[row][column]:
                conflicts_rows_diag_up.append(row)
                break
        if len(conflicts_rows_diag_up) == 2:
            pass
        elif len(conflicts_rows_diag_up) == 1:
            target_row = conflicts_rows_diag_up[0]
            updated_items += [(r, diag_up - r) for r in range(min(given_row, target_row), max(given_row, target_row) + 1)]
            updated_items.remove((given_row, given_column))
        else:
            start_row = max(0, diag_up - self.n + 1)
            end_row = min(diag_up, self.n - 1)
            updated_items += [(r, diag_up - r) for r in range(start_row, end_row + 1)]
            updated_items.remove((given_row, given_column))

        # last, check items to be updated on the diag down
        conflicts_rows_diag_down = []
        diag_down = given_row - given_column
        for row in range(given_row - 1, -1, -1):
            column = row - diag_down
            if column < 0 or self.n <= column:
                break
            if self.current_state[row][column]:
                conflicts_rows_diag_down.append(row)
                break
        for row in range(given_row + 1, self.n):
            column = row - diag_down
            if column < 0 or self.n <= column:
                break
            if self.current_state[row][column]:
                conflicts_rows_diag_down.append(row)
                break
        if len(conflicts_rows_diag_down) == 2:
            pass
        elif len(conflicts_rows_diag_down) == 1:
            target_row = conflicts_rows_diag_down[0]
            updated_items += [(r, r - diag_down) for r in range(min(given_row, target_row), max(given_row, target_row) + 1)]
            updated_items.remove((given_row, given_column))
        else:
            start_row = max(diag_down, 0)
            end_row = min(diag_down + self.n, self.n)
            updated_items += [(r, r - diag_down) for r in range(start_row, end_row)]
            updated_items.remove((given_row, given_column))

        return updated_items

    def print_conflicts_table(self):
        """Print conflicts table
        """
        # insert a new line anyway
        print()

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
            for j in range(self.n):
                s = str(self.conflicts_table[i][j]).center(max_len, ' ')
                row_list.append(s)
            row = '|'.join(row_list) + '|'
            print(row)
            print(sep)
