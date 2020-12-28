from engine.simple_engine import SimpleEngine
import pytest
import datetime


@pytest.mark.parametrize(['i', 'expected_result_num'], [(1, 1), (2, 0), (3, 0), (4, 2), (5, 10), (6, 4), (7, 40), (8, 92), (9, 352)])
def test_solve(i, expected_result_num):
    """test for solve()
    """
    e = SimpleEngine(n=i)
    start_time = datetime.datetime.now()
    results = e.solve()
    end_time = datetime.datetime.now()
    duration_seconds = (end_time - start_time).seconds
    print(f'len(results) for {i}: {len(results)}, duration_seconds: {duration_seconds}')
    assert len(results) == expected_result_num
