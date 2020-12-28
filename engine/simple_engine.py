from models.model import Board, Engine
from utils.util import validate
from typing import List
from itertools import permutations


class SimpleEngine(Engine):
    def __init__(self, n: int, take_one_solution: bool = True) -> None:
        self.n: int = n
        self.results: List[Board] = []
        self.take_one_solution: bool = take_one_solution

    def solve(self) -> List[Board]:
        """solve problem using greedy search algolithm
        Args:
            board (Board): Board
        Returns:
            results (List[Board]): results
        """
        # greedy search
        for seq in permutations([i for i in range(self.n)]):
            b = Board(n=self.n)
            for j in range(self.n):
                b.set_queen(at=(j, seq[j]))
            if validate(board=b):
                self.results.append(b)
                # return early if requires taking a solution
                if self.take_one_solution:
                    break
        return self.results
