from model.util import values
import pytest
import pandas as pd
import math

sample_df1 = pd.DataFrame.from_dict( {"A": [20, 30, 40], "B": [0, '', None]} )
sample_df2 = pd.DataFrame.from_dict( {"A": [20, 30, 40], "B": [1, 2, 3]} )


def test_value_eq():
    assert values.value_eq(None, None)
    assert values.value_eq(None,'')
    assert not values.value_eq("", " ")

    assert values.value_eq(1, 1.0)
    assert not values.value_eq(1, 0)
    assert values.value_eq(0, math.nan)

    assert not values.value_eq(sample_df1, 20.0)
    assert not values.value_eq(20.0, sample_df1)

    assert values.value_eq(2.000001, 2.0)

    assert values.value_eq(None, None, all_zero=False)
    assert values.value_eq(math.nan, math.nan, all_zero=False)
    assert not values.value_eq(None, 0, all_zero=False)
    assert not values.value_eq(None, math.nan, all_zero=False)


def test_df_value_eq():
    d3 = sample_df1.copy()

    assert values.value_eq(sample_df1, d3)
    assert values.value_eq(sample_df1, d3, all_zero=False)
    
    assert not values.value_eq(sample_df1, sample_df2)
    assert not values.value_eq(sample_df1, pd.concat([sample_df1, sample_df1]))

    d4 = sample_df1.copy()
    d4.columns = ["C", "D"]
    assert not values.value_eq(sample_df1, d4)

    d5 = sample_df1.copy()
    d5.index = ["a", "b", "c"]
    assert not values.value_eq(sample_df1, d5)


def test_stats():
    # filter_nans works?
    assert values.smean(sample_df1['B']) == 0
    # we get nan if we don't have enough values?
    assert math.isnan(values.s25_ile(sample_df1['B']))
    # we are indexing the result of quantiles properly?
    assert values.s75_ile(sample_df1['A']) == pytest.approx(40.0)