from engine.simple_engine import SimpleEngine
from engine.minconflicts_engine import MinConflictsEngine
import datetime
import pytest


@pytest.mark.skip(reason='takes too long time')
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


@pytest.mark.skip(reason='takes too long time')
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


@pytest.mark.skip(reason='takes too long time')
def test_solve_minconflicts_ver_3():
    """test for solve
    """
    for i in range(1, 100):
        e = MinConflictsEngine(n=i, version=3)
        _ = e.solve()
        print(f'{i}:')
        print(f'  is solution: {e.has_solution()}')
        print(f'  duration: {e.debug_duration_seconds} sec')
        print(f'  steps: {e.debug_steps}')


@pytest.mark.skip(reason='takes too long time')
@pytest.mark.parametrize(['i', 'expected_result_num'], [(1, 1), (2, 0), (3, 0), (4, 2), (5, 10), (6, 4), (7, 40), (8, 92), (9, 352)])
def test_solve(i, expected_result_num):
    """test for solve()
    """
    e = SimpleEngine(n=i, take_one_solution=False)
    start_time = datetime.datetime.now()
    results = e.solve()
    end_time = datetime.datetime.now()
    duration_seconds = (end_time - start_time).seconds
    print(f'len(results) for {i}: {len(results)}, duration_seconds: {duration_seconds}')
    assert len(results) == expected_result_num


@pytest.mark.skip(reason='takes too long time')
def test_solve_a_solution():
    """test for solve
    """
    for i in range(1, 100):
        e = SimpleEngine(n=i)
        boards = e.solve()
        print(f'{i}:')
        if i < 40 and len(boards) != 0:
            boards[0].print()
    # e = MinConflictsEngine(n=2)
    # e.solve()
