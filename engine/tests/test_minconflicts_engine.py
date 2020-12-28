from engine.minconflicts_engine import MinConflictsEngine
import pytest


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
    assert e.get_conflicts_count(at=(0, 7)) == 3
    assert e.get_conflicts_count(at=(1, 7)) == 3
    assert e.get_conflicts_count(at=(2, 7)) == 2
    assert e.get_conflicts_count(at=(3, 7)) == 3
    assert e.get_conflicts_count(at=(4, 7)) == 4
    assert e.get_conflicts_count(at=(5, 7)) == 2
    assert e.get_conflicts_count(at=(6, 7)) == 3
    assert e.get_conflicts_count(at=(7, 7)) == 1

    # remove queen from (7, 7) and (3, 3)
    e.current_state[7][7] = False
    e.current_state[3][3] = False

    # tests that (7, 7) has no conflicts
    assert e.get_conflicts_count(at=(7, 7)) == 0


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

    # confirm that the next unit for (7, 7) is (7, 5)
    assert e.search_next_unit(unit=(7, 7)) == (7, 2)


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


@pytest.mark.skip(reason='takes too long time')
def test_solve_minconflicts():
    """test for solve
    """
    for i in range(1, 100):
        e = MinConflictsEngine(n=i)
        _ = e.solve()
        print(f'{i}:')
        print(f'  duration: {e.debug_duration_seconds} sec')
        print(f'  steps: {e.debug_steps}')


# @pytest.mark.skip(reason='takes too long time')
def test_solve_minconflicts_ver_2():
    """test for solve
    """
    for i in range(1, 100):
        e = MinConflictsEngine(n=i, version=2)
        _ = e.solve()
        print(f'{i}:')
        print(f'  is solution: {e.has_solution()}')
        print(f'  duration: {e.debug_duration_seconds} sec')
        print(f'  steps: {e.debug_steps}')


def test_million():
    """test when n = 1,000,000
    """
    for j in range(0, 7):
        i = 10 ** j
        e = MinConflictsEngine(n=i, version=2)
        _ = e.solve()
        print(f'{i}:')
        print(f'  is solution: {e.has_solution()}')
        print(f'  duration: {e.debug_duration_seconds} sec')
        print(f'  steps: {e.debug_steps}')
