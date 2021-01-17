from models.model import Engine, Board
from typing import Dict, List, Tuple, Set
import random
import time
from collections import deque


class MinConflictsEngine(Engine):
    COLUMN = 'column'
    DIAG_UP = 'diag_up'
    DIAG_DOWN = 'diag_down'

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
        # self.current_state: List[List[bool]] = [[False for _ in range(self.n)] for _ in range(self.n)]

        self.snapshot_state: List[List[bool]] = None
        # self.random_ratio = max(self.n, 100)
        self.random_ratio = 1

        self.conflicts_num_dict: Dict[str, Dict[int, int]] = {MinConflictsEngine.COLUMN: {},
                                                              MinConflictsEngine.DIAG_UP: {}, MinConflictsEngine.DIAG_DOWN: {}}
        for column in range(self.n):
            self.conflicts_num_dict[MinConflictsEngine.COLUMN][column] = 0
        for diag_up in range(2 * self.n - 2 + 1):
            self.conflicts_num_dict[MinConflictsEngine.DIAG_UP][diag_up] = 0
        for diag_down in range(- (self.n - 1), self.n - 1 + 1):
            self.conflicts_num_dict[MinConflictsEngine.DIAG_DOWN][diag_down] = 0

        self.queen_is: Dict[int, int] = {row: None for row in range(self.n)}

        self.history: List[Tuple[int, int]] = []
        self.history_offset_dict: Dict[int, int] = {row: 0 for row in range(self.n)}

        r = [i for i in range(self.n)]
        random.shuffle(r)
        self.queue: deque = deque(r)

        # variables for debug
        self.debug_start_time: float = None
        self.debug_end_time: float = None
        self.debug_duration_seconds: float = 0
        self.debug_steps: int = 0

    def solve(self, enable_print: bool = False) -> List[Board]:
        """solve problem

        Returns:
            boards (List[Boards]): the list of result boards
        """
        # for debug
        self.debug_start_time = time.time()

        # initialize current board
        self.initialize_current_board()

        # loop for searching a solution until step reaches max_steps
        for step in range(self.max_steps):

            # return the current board if it's already had a solution
            if self.has_solution():
                self.debug_steps = step
                return self.convert_to_boards(enable_print=enable_print)

            # choose a unit that conflicts to the other one
            unit = self.choose_one_conflicts()

            # search the unit that has the minimum conflicts count to the other
            next_unit = self.search_next_unit(unit=unit)

            # move to the next
            self.move(previous=unit, after=next_unit)

        # return the current board if step reaches max_steps
        self.debug_steps = self.max_steps
        return self.convert_to_boards(enable_print=enable_print)

    def choose_one_conflicts(self) -> Tuple[int, int]:
        """randomly choose a unit that conflicts to the other

        Returns:
            unit (Tuple[int, int]): a unit where a queen exists and has conflicts to someone
        """
        # r = [i for i in range(self.n)]
        # random.shuffle(r)
        # rows = deque(r)
        # while len(rows) != 0:
        for _ in range(self.n):

            row_num = self.queue.popleft()
            self.queue.append(row_num)

            # find column where a queen exists
            # column_num = self.current_state[row_num].index(True)
            column_num = self.queen_is[row_num]

            # check conflicts at the unit
            conflicts_count, _ = self.get_conflicts_count(at=(row_num, column_num))

            # if there is a conflict, return the unit
            if conflicts_count != 0:
                return (row_num, column_num)

    def search_next_unit(self, unit: Tuple[int, int], randomly: bool = True) -> Tuple[int, int]:
        """search a unit that has minimum conflicts count

        Args:
            previous (Tuple[int, int]): a unit
            randomly (bool): enable randomly choice from version 2. Default True
        Returns:
            next_unit (Tuple[int, int]): the next unit where a queen will move
        """
        given_row, given_column = unit

        current_conflicts_num = self.get_conflicts_count(at=unit)
        current_conflicts_unit = unit

        # # break ties randomly
        # if self.break_ties_randomly():
        #     column = random.randint(0, self.n - 1)
        #     return (given_row, column)

        if len(self.history) == 0 or self.break_ties_randomly():
            for _ in range(self.n):
                column = self.queue.popleft()
                self.queue.append(column)
                c = self.get_conflicts_count(at=(given_row, column))
                if current_conflicts_num > c:
                    if current_conflicts_num == 0:
                        return (given_row, column)
                    current_conflicts_num = c
                    current_conflicts_unit = (given_row, column)
            return current_conflicts_unit
        else:
            start_offset = self.history_offset_dict[given_row]
            end_offset = len(self.history) - 1
            columns = []
            for i in range(start_offset, end_offset + 1):
                h_row, h_column = self.history[i]
                columns.append(h_column)
                if h_row + h_column == given_row + given_column:
                    columns.append(h_row + h_column - given_row)
                if h_row - h_column == given_row - given_column:
                    columns.append(given_row - h_row + h_column)
            self.history_offset_dict[given_row] = end_offset

            random.shuffle(columns)
            for column in columns:
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
        columns = [i for i in range(self.n)]
        random.shuffle(columns)
        queue = deque(columns)

        for row in range(self.n):
            column = None
            min_conflicts_num = self.n
            reserved_queue = deque([])

            while len(queue) != 0:
                # print(f'queue: {queue}')
                current_column = queue.popleft()
                # print(f'popped: {current_column}')
                current_conflicts_num, _ = self.get_conflicts_count(at=(row, current_column))
                # print(f'current_conflicts_num: {current_conflicts_num}')

                if current_conflicts_num == -3:
                    column = current_column
                    while len(reserved_queue) != 0:
                        c = reserved_queue.popleft()
                        if c != column:
                            queue.append(c)
                    break

                if min_conflicts_num > current_conflicts_num:
                    column = current_column
                    min_conflicts_num = current_conflicts_num

                reserved_queue.append(current_column)

            # print(f'reserved_queue: {reserved_queue}')
            while len(reserved_queue) != 0:
                c = reserved_queue.popleft()
                if c != column:
                    queue.append(c)

            self.put_queen(at=(row, column))

    def has_solution(self) -> bool:
        """check if the current board is a solution

        Returns:
            (bool): True if it's a solution
        TODO: make O(n^2) O(n)
        """
        for row_num in range(self.n):
            # # it's not a solution if more than 2 queens exists on a same row
            # if sum(self.current_state[row_num]) != 1:
            #     return False

            # it's not a solution if a queen has some conflicts
            # column_num = self.current_state[row_num].index(True)
            column_num = self.queen_is[row_num]
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
        num = - 3
        diag_up = given_row + given_column
        diag_down = given_row - given_column
        num = num + self.conflicts_num_dict[MinConflictsEngine.COLUMN][given_column]
        num = num + self.conflicts_num_dict[MinConflictsEngine.DIAG_UP][diag_up]
        num = num + self.conflicts_num_dict[MinConflictsEngine.DIAG_DOWN][diag_down]
        return num, None

    def convert_to_boards(self, enable_print: bool) -> List[Board]:
        """convert current state to Board

        Returns:
            boards (List[Board]): current state descirbed as Board
        Note:
            it returns a list but its length is always 1
        """
        # for debug
        self.debug_end_time = time.time()
        if self.debug_start_time is not None:
            self.debug_duration_seconds = self.debug_end_time - self.debug_start_time

        if enable_print:
            b = Board(n=self.n)
            for k, v in self.queen_is.items():
                b.set_queen(at=(k, v))
            return [b]
        else:
            return None

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
        # self.current_state[given_row][given_column] = True
        self.queen_is[given_row] = given_column

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
        # self.current_state[given_row][given_column] = False

        self.history.append(at)

        self.conflicts_num_dict[MinConflictsEngine.COLUMN][given_column] -= 1
        self.conflicts_num_dict[MinConflictsEngine.DIAG_UP][given_row + given_column] -= 1
        self.conflicts_num_dict[MinConflictsEngine.DIAG_DOWN][given_row - given_column] -= 1
