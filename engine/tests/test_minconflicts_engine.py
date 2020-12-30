from engine.minconflicts_engine import MinConflictsEngine
import pytest
import random


def test_get_conflicts_count():
    """test for get_conflicts_count
    """
    # define current state
    state = [
        [False, False, False, False, True, False, False, False],
        [True, False, False, False, False, False, False, False],
        [False, False, False, False, False, True, False, False],
        [False, False, False, True, False, False, False, False],
        [False, True, False, False, False, False, False, False],
        [False, False, False, False, False, False, True, False],
        [False, False, True, False, False, False, False, False],
        [False, False, False, False, False, False, False, True]
    ]

    # initialize instance
    e = MinConflictsEngine(n=8)
    e.current_state = state

    # tests
    assert e.get_conflicts_count(at=(0, 7)) == (3, [(7, 7), (2, 5)])
    assert e.get_conflicts_count(at=(1, 7)) == (3, [(7, 7), (6, 2)])
    assert e.get_conflicts_count(at=(2, 7)) == (2, [(7, 7)])
    assert e.get_conflicts_count(at=(3, 7)) == (3, [(7, 7), (0, 4)])
    assert e.get_conflicts_count(at=(4, 7)) == (4, [(7, 7), (2, 5), (5, 6)])
    assert e.get_conflicts_count(at=(5, 7)) == (2, [(7, 7)])
    assert e.get_conflicts_count(at=(6, 7)) == (3, [(7, 7), (5, 6)])
    assert e.get_conflicts_count(at=(7, 7)) == (1, [(3, 3)])

    # remove queen from (7, 7) and (3, 3)
    e.current_state[7][7] = False
    e.current_state[3][3] = False

    # tests that (7, 7) has no conflicts
    assert e.get_conflicts_count(at=(7, 7)) == (0, [])

    # for version 4
    # version 4 engine does not count queens on the same row
    # define current state
    state = [
        [False, False, False, False, True, False, False, False],
        [True, False, False, False, False, False, False, False],
        [False, False, False, False, False, True, False, False],
        [False, False, False, True, False, False, False, False],
        [False, True, False, False, False, False, False, False],
        [False, False, False, False, False, False, True, False],
        [False, False, True, False, False, False, False, False],
        [False, False, False, False, False, False, False, True]
    ]

    # initialize instance
    e = MinConflictsEngine(n=8, version=4)
    e.current_state = state

    # tests
    assert e.get_conflicts_count(at=(0, 7)) == (2, [(7, 7), (2, 5)])
    assert e.get_conflicts_count(at=(1, 7)) == (2, [(7, 7), (6, 2)])
    assert e.get_conflicts_count(at=(2, 7)) == (1, [(7, 7)])
    assert e.get_conflicts_count(at=(3, 7)) == (2, [(7, 7), (0, 4)])
    assert e.get_conflicts_count(at=(4, 7)) == (3, [(7, 7), (5, 6), (2, 5)])
    assert e.get_conflicts_count(at=(5, 7)) == (1, [(7, 7)])
    assert e.get_conflicts_count(at=(6, 7)) == (2, [(7, 7), (5, 6)])
    assert e.get_conflicts_count(at=(7, 7)) == (1, [(3, 3)])

    # remove queen from (7, 7) and (3, 3)
    e.current_state[7][7] = False
    e.current_state[3][3] = False

    # tests that (7, 7) has no conflicts
    assert e.get_conflicts_count(at=(7, 7)) == (0, [])


def test_has_solution():
    """test for has_solution
    """
    # define current state that is not solution
    not_solution = [
        [False, False, False, False, True, False, False, False],
        [True, False, False, False, False, False, False, False],
        [False, False, False, False, False, True, False, False],
        [False, False, False, True, False, False, False, False],
        [False, True, False, False, False, False, False, False],
        [False, False, False, False, False, False, True, False],
        [False, False, True, False, False, False, False, False],
        [False, False, False, False, False, False, False, True]
    ]

    # initialize instance
    e = MinConflictsEngine(n=8)
    e.current_state = not_solution

    # confirm it's not solution
    assert not e.has_solution()

    # define current state that is a solution
    solution = [
        [True, False, False, False, False, False, False, False],
        [False, False, False, False, True, False, False, False],
        [False, False, False, False, False, False, False, True],
        [False, False, False, False, False, True, False, False],
        [False, False, True, False, False, False, False, False],
        [False, False, False, False, False, False, True, False],
        [False, True, False, False, False, False, False, False],
        [False, False, False, True, False, False, False, False]
    ]
    e.current_state = solution

    # confirm it has a solution
    assert e.has_solution()


def test_initialize_current_board():
    """test for initialize_current_board
    """
    e = MinConflictsEngine(n=8)
    e.initialize_current_board()

    # confirm the sum of True in a row equals to 1
    for row in e.current_state:
        assert sum(row) == 1

    # confirm the sum of True in a column equals to 1
    for column_num in range(e.n):
        assert sum([e.current_state[i][column_num] for i in range(e.n)])


def test_choose_one_conflicts():
    """test for choose_one_conflicts
    """
    not_solution = [
        [False, False, False, False, True, False, False, False],
        [True, False, False, False, False, False, False, False],
        [False, False, False, False, False, True, False, False],
        [False, False, False, True, False, False, False, False],
        [False, True, False, False, False, False, False, False],
        [False, False, False, False, False, False, True, False],
        [False, False, True, False, False, False, False, False],
        [False, False, False, False, False, False, False, True]
    ]
    e = MinConflictsEngine(n=8)
    e.current_state = not_solution

    # confirm it returns the one in the list
    assert e.choose_one_conflicts() in [(3, 3), (7, 7)]


def test_search_next_unit():
    """test for search_next_unit
    """
    not_solution = [
        [False, False, False, False, True, False, False, False],
        [True, False, False, False, False, False, False, False],
        [False, False, False, False, False, True, False, False],
        [False, False, False, True, False, False, False, False],
        [False, True, False, False, False, False, False, False],
        [False, False, False, False, False, False, True, False],
        [False, False, True, False, False, False, False, False],
        [False, False, False, False, False, False, False, True]
    ]
    e = MinConflictsEngine(n=8)
    e.current_state = not_solution

    # confirm that the next unit for (7, 7) is (7, 2)
    assert e.search_next_unit(unit=(7, 7)) == (7, 2)

    # if version 3, there must be some unit in next_unit
    e3 = MinConflictsEngine(n=8, version=3)
    e3.current_state = not_solution
    assert e3.search_next_unit(unit=(7, 7), randomly=False) == (7, 2)
    assert e3.unit_on_next_step == (6, 2)


def test_move():
    """test for move
    """
    state = [
        [True, False, False],
        [False, False, False],
        [False, False, True]
    ]
    e = MinConflictsEngine(n=3)
    e.current_state = state

    # confirm there occurs some errors
    with pytest.raises(Exception):
        e.move(previous=(0, 2), after=(0, 1))
        e.move(previous=(0, 0), after=(3, 3))

    # confirm (0, 0) is moved to (0, 2)
    e.move(previous=(0, 0), after=(0, 2))
    assert not e.current_state[0][0]
    assert e.current_state[0][2]


def test_solve_minconflicts_simple():
    """test for solve
    """
    for i in range(1, 9):
        e = MinConflictsEngine(n=i)
        b = e.solve()
        assert len(b) == 1


def test_solve_minconflicts_simple_for_ver2():
    """test for solve
    """
    for i in range(1, 9):
        e = MinConflictsEngine(n=i, version=2)
        b = e.solve()
        assert len(b) == 1


def test_solve_minconflicts_simple_for_ver3():
    """test for solve
    """
    for i in range(1, 9):
        e = MinConflictsEngine(n=i, version=3)
        b = e.solve()
        assert len(b) == 1


def test_get_updated_items():
    """test for put_queen
    """
    e = MinConflictsEngine(n=3)
    assert set(e.get_updated_items(at=(0, 0))) == {(1, 0), (2, 0), (1, 1), (2, 2)}
    assert set(e.get_updated_items(at=(0, 1))) == {(1, 1), (2, 1), (1, 0), (1, 2)}
    assert set(e.get_updated_items(at=(0, 2))) == {(1, 2), (2, 2), (1, 1), (2, 0)}
    assert set(e.get_updated_items(at=(1, 0))) == {(0, 0), (2, 0), (0, 1), (2, 1)}
    assert set(e.get_updated_items(at=(1, 1))) == {(0, 1), (2, 1), (0, 0), (2, 2), (0, 2), (2, 0)}
    assert set(e.get_updated_items(at=(1, 2))) == {(0, 2), (2, 2), (0, 1), (2, 1)}
    assert set(e.get_updated_items(at=(2, 0))) == {(0, 0), (1, 0), (1, 1), (0, 2)}
    assert set(e.get_updated_items(at=(2, 1))) == {(0, 1), (1, 1), (1, 0), (1, 2)}
    assert set(e.get_updated_items(at=(2, 2))) == {(0, 2), (1, 2), (0, 0), (1, 1)}


def test_put_and_remove_queen():
    """test for put_queen and remove_queen
    """
    e = MinConflictsEngine(n=3)

    e.put_queen(at=(1, 1))
    assert e.conflicts_table == [[1, 1, 1], [0, 0, 0], [1, 1, 1]]
    e.put_queen(at=(0, 1))
    assert e.conflicts_table == [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
    e.put_queen(at=(2, 1))
    assert e.conflicts_table == [[1, 1, 1], [2, 2, 2], [1, 1, 1]]
    e.remove_queen(at=(2, 1))
    assert e.conflicts_table == [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
    e.put_queen(at=(2, 0))
    assert e.conflicts_table == [[2, 1, 1], [2, 2, 1], [1, 1, 1]]
    e.remove_queen(at=(2, 0))
    assert e.conflicts_table == [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
    e.put_queen(at=(2, 2))
    assert e.conflicts_table == [[1, 1, 2], [1, 2, 2], [1, 1, 1]]
    e.remove_queen(at=(0, 1))
    assert e.conflicts_table == [[1, 1, 2], [0, 1, 1], [1, 1, 1]]
    e.put_queen(at=(0, 0))
    assert e.conflicts_table == [[1, 1, 2], [1, 2, 1], [2, 1, 1]]
    e.remove_queen(at=(0, 0))
    assert e.conflicts_table == [[1, 1, 2], [0, 1, 1], [1, 1, 1]]
    e.put_queen(at=(0, 2))
    assert e.conflicts_table == [[1, 1, 2], [0, 2, 2], [1, 1, 2]]

    # test for conflicts dict is valid
    # TODO: delete
    # assert e.conflicts_dict == {0: {0: set(), 1: {1, 0}, 2: {2}, 3: set(), 4: set(), 5: set(), 6: set()},
    #                             1: {0: {0}, 1: set(), 2: {2, 1}, 3: set(), 4: set(), 5: set(), 6: set()},
    #                             2: {0: set(), 1: {1, 0}, 2: {2}, 3: set(), 4: set(), 5: set(), 6: set()}}

    # try put and remove queens for 100 times and confirm the last state is all zeros
    for _ in range(100):
        e = MinConflictsEngine(n=8)
        columns = [random.randint(0, 7) for _ in range(8)]
        items = list(zip([i for i in range(8)], columns))
        for item in items:
            e.put_queen(at=item)
        while len(items) != 0:
            item = random.choice(items)
            e.remove_queen(at=item)
            items.remove(item)
        assert e.conflicts_table == [[0 for _ in range(8)] for _ in range(8)]


def test_solve_minconflicts_simple_for_ver4():
    """test for solve
    """
    for i in range(1, 9):
        e = MinConflictsEngine(n=i, version=4)
        b = e.solve()
        assert len(b) == 1


def test_solve_minconflicts_simple_for_ver5():
    """test for solve
    """
    for i in range(1, 9):
        e = MinConflictsEngine(n=i, version=5)
        b = e.solve()
        assert len(b) == 1
