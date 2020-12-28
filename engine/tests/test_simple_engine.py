from engine.simple_engine import SimpleEngine
import pytest
import datetime


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
