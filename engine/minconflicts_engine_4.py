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
        self.conflicts_num_dict: Dict[str, Dict[int, int]] = {MinConflictsEngine.COLUMN: {},
                                                              MinConflictsEngine.DIAG_UP: {}, MinConflictsEngine.DIAG_DOWN: {}}
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
        
        current_conflicts_num = self.get_conflicts_count(at=unit)
        current_conflicts_unit = unit

        # break ties randomly
        if self.break_ties_randomly():
            column = random.randint(0, self.n - 1)
            return (given_row, column)

        random.shuffle(self.all_list)
        for column in self.all_list:
            c = self.get_conflicts_count(at=(given_row, column))
            if current_conflicts_num > c:
                if current_conflicts_num == 0:
                    return (given_row, column)
                current_conflicts_num = c
                current_conflicts_unit = (given_row, column)
        return current_conflicts_unit

    def move(self, previous: Tuple[int, int], after: Tuple[int, int]) -> None:
        """move a queen to the next unit

        Args:
            previous (Tuple[int, int]): the previous unit
            after (Tuple[int, int]): the next unit where a queen will move
        """
        previous_row, previous_column = previous
        after_row, after_column = after

        # move from the previous to the after
        self.remove_queen(at=(previous_row, previous_column))
        self.put_queen(at=(after_row, after_column))

    def initialize_current_board(self, debug_row=None) -> None:
        """initialize the current board
        """
        # list of assignable column (= Domain of row)
        columns = [i for i in range(self.n)]
        for row in range(self.n):

            # choose one from columns
            column = random.choice(columns)

            # assign initial value using also min-conflicts
            next_unit = self.search_next_unit(unit=(row, column), randomly=False)
            self.put_queen(at=next_unit)

            # remove assigned column from columns
            columns.remove(column)

    def has_solution(self) -> bool:
        """check if the current board is a solution

        Returns:
            (bool): True if it's a solution
        TODO: make O(n^2) O(n)
        """
        for row_num in range(self.n):
            # it's not a solution if more than 2 queens exists on a same row
            if sum(self.current_state[row_num]) != 1:
                return False

            # it's not a solution if a queen has some conflicts
            column_num = self.current_state[row_num].index(True)
            conflicts_count, _ = self.get_conflicts_count(at=(row_num, column_num))
            if conflicts_count > 0:
                return False

        # otherwise, it's a solution
        return True

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

        given_row, given_column = at
        num = self.conflicts_num_dict[MinConflictsEngine.COLUMN][given_column] - 1
        num += self.conflicts_num_dict[MinConflictsEngine.DIAG_UP][given_row + given_column] - 1
        num += self.conflicts_num_dict[MinConflictsEngine.DIAG_DOWN][given_row - given_column] - 1
        return num, None

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

    def break_ties_randomly(self) -> bool:
        """return True or False randomly

        Args:
            exponent (int): the indicator of uniform distribution
        """
        if random.randint(0, self.random_ratio) == 0:
            return True
        return False

    def put_queen(self, at: Tuple[int, int]) -> None:
        """put queen on the board

        also, update conflicts table

        Args:
            at (Tuple[int, int]): the place where the given queen is putted
        """
        given_row, given_column = at

        # put queen
        self.current_state[given_row][given_column] = True

        self.conflicts_num_dict[MinConflictsEngine.COLUMN][given_column] += 1
        self.conflicts_num_dict[MinConflictsEngine.DIAG_UP][given_row + given_column] += 1
        self.conflicts_num_dict[MinConflictsEngine.DIAG_DOWN][given_row - given_column] += 1

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

        self.conflicts_num_dict[MinConflictsEngine.COLUMN][given_column] -= 1
        self.conflicts_num_dict[MinConflictsEngine.DIAG_UP][given_row + given_column] -= 1
        self.conflicts_num_dict[MinConflictsEngine.DIAG_DOWN][given_row - given_column] -= 1