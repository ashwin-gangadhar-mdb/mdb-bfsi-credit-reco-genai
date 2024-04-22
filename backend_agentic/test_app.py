import pytest

from stat_score_util import calculate_percentile_given_value, calculate_credit_score
from dummy import PrepareDummyCols
import pandas as pd

def test_calculate_percentile_given_value_mean():
    # Value at mean should be 0.5
    assert abs(calculate_percentile_given_value(100, 100, 10) - 0.5) < 1e-6

def test_calculate_percentile_given_value_above_mean():
    # Value above mean should be > 0.5
    assert calculate_percentile_given_value(120, 100, 10) > 0.5

def test_calculate_percentile_given_value_below_mean():
    # Value below mean should be < 0.5
    assert calculate_percentile_given_value(80, 100, 10) < 0.5



def test_calculate_credit_score_basic():
    ip = {
        "Repayment History": 1.0,
        "Credit Utilization": 0.8,
        "Credit History": 0.7,
        "Num Credit Inquiries": 0.5,
        "Outstanding": 0.6,
    }
    score = calculate_credit_score(ip)
    assert 300 <= score <= 850

if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main([__file__]))

