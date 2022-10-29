"""Mathematical and other operations on values.

These functions simplify common operations, and/or help reproduce consistent behavior with the original Excel models."""
from typing import List
import math
import statistics
import pandas as pd
import pytest
import re


def round_away(x: float) -> int:
    """excel rounds away from zero on breakeven
    so 0.5 ==> 1.0, -0.5 ==> -1.0
    python2 does the same, but python3 does not, hence this code
    copied almost verbatim from https://github.com/python/cpython/blob/master/Python/pymath.c#L71
    """
    absx = math.fabs(x)
    y = math.floor(absx)
    if absx - y >= 0.5:
        y += 1.0
    return int(math.copysign(y, x))


def pseudo_nan(x) -> bool:
    """Return true if x is NaN, None or the empty string"""
    # And don't choke if it isn't a number at all.
    return x is None or x == '' or (isinstance(x, float) and math.isnan(x))


def pseudo_zero(x) -> bool:
    """Return true if `x` is "like zero" in certain contexts.
    
    This partially mimics the behavior of Excel formulas, but is more broad: zero, empty
    string, None and NaN are all considered "like zero"."""
    return x == 0 or pseudo_nan(x)


def value_eq(v1, v2, all_zero=True, thresh=1e-6) -> bool:
    """Return True if v1 is equal or 'very close to' value v2.
    Params v1 and v2 may be numeric, strings, or pandas DataFrames.
    
    For simple values:
    If all_zero is True (the default), 0, NaN, None and the empty string are all treated as equal.
    Otherwise, numeric values are considered equal if their difference is less than `thresh`.
   
    For DataFrames:
    Indices must be identical in value
    The simple values within must all be value_eq.
    """

    # Take care of the DataFrames
    if isinstance(v1, pd.DataFrame):
        return isinstance(v2, pd.DataFrame) and df_value_eq(v1, v2, all_zero, thresh)

    if isinstance(v2, pd.DataFrame):
        return False

    # Now back to simple types
    if isinstance(v1, str) and isinstance(v2, str):
        return (v1 == v2)
    
    if all_zero:
        if pseudo_zero(v1):
            v1 = 0.0
    
        if pseudo_zero(v2):
            v2 = 0.0

    return (v1 is None and v2 is None) or (v1 == pytest.approx(v2, abs=thresh, rel=1e-6, nan_ok=True))


def df_value_eq(v1: pd.DataFrame, v2: pd.DataFrame, all_zero=True, thresh=1e-6) -> bool:
    """Compare dataframes using @value_eq for value comparisons"""
    if not v1.index.equals(v2.index):
        return False
    if not v1.columns.equals(v2.columns):
        return False
    
    # Pandas does great things to make application of functions to a *single* DataFrame easy and efficient,
    # but there really isn't anything to make it easy to implement your own binary function across *two* dataframes...
    for col in v1.columns:
        for x1,x2 in zip(v1[col],v2[col]):
            if not value_eq(x1,x2,all_zero,thresh):
                return False
    return True


def df_drop_empty_columns(df: pd.DataFrame, keep: List[str]=None) -> pd.DataFrame:
    """Drop columns that are empty, using the generalized @pseudo_zero definition of empty.
    If argument `keep` is supplied, it should be a list of names of columns to keep even if they are empty.
    
    To get the empty columns back again, you can use `df.reindex(columns=<list of all columns>)`"""
    new_cols = []
    keep = keep or []
    for col in df:
        if col in keep:
            new_cols.append(col)
        elif not df[col].apply(pseudo_zero).all():
            new_cols.append(col)
    return df.reindex(columns=new_cols)
    


def zero_df_like(likedf: pd.DataFrame) -> pd.DataFrame:
    """Return a dataframe the same dimensions as `likedf`, filled with zeros."""
    newdf = pd.DataFrame([0]).reindex_like(likedf)
    newdf[:] = 0.0
    return newdf


"""Statistics over a set of estimates for some quantity.  

All summary statistics take a list/iterator/etc. of floating point values as arguments.  All will ignore any existing None/NaN values in the data,
and all will return NaN if the list is empty or doesn't have enough values to compute.
"""


def filter_nans(vs):
    return [ x for x in vs if not pseudo_nan(x) ]

def smin(vs):
    vs = filter_nans(vs)
    return min(vs) if len(vs) else math.nan

def smax(vs):
    vs = filter_nans(vs)
    return max(vs) if len(vs) else math.nan

def smean(vs):
    vs = filter_nans(vs)
    return statistics.mean(vs) if len(vs) else math.nan

def smedian(vs):
    vs = filter_nans(vs)
    return statistics.median(vs) if len(vs) else math.nan


def s25_ile(vs):
    vs = filter_nans(vs)
    if len(vs) > 2:
        quiles = statistics.quantiles(vs)
        return quiles[0]
    else:
        return math.nan

def s75_ile(vs):
    vs = filter_nans(vs)
    if len(vs) > 2:
        quiles = statistics.quantiles(vs)
        return quiles[2]
    else:
        return math.nan

def percentile_rank(vs, v, extended=True):
    """Compares `v` to the set of values `vs`.  If `extended` is True (the default), we allow results greater than 1 or less than 0 if `v`
    is outside the range of `vs`, and also linearly interpolate the rank between the two nearest values of `vs`"""
    vs = filter_nans(vs)
    if len(vs):
        vs.sort()
        i=0
        for i, vx in enumerate(vs):
            if vx > v:
                break
        rank = i / len(vs)
        if extended:
            if v < vs[0] or v > vs[-1]:
                range = (vs[-1] - vs[0])
                if vs < vs[0]:
                    rank = (vs - vs[0]) / range
                else:
                    rank = (vs - vs[1]) / range
            elif i > 0:
                rank2 = (i-1) / len(vs)
                interp = (v - vs[i-1]) / (vs[i] - vs[i-1])
                rank = rank2 + interp * (rank - rank2)
        return rank
    else:
        return math.nan



def spvar(vs):
    """Compute the population variance of the non-nan members of vs."""
    # We implement population variance rather than sample variance because we are usually computing 
    # the variance across a complete set of estimates.
    vs = filter_nans(vs)
    return statistics.pvariance(vs) if len(vs) else math.nan

def ssdev(vs):
    """Compute the population standard deviation of non-nan members of vs."""
    vs = filter_nans(vs)
    return statistics.stdev(vs) if len(vs) else math.nan

def slow_dev(vs, n=1, minzero=False):
    """Return `mean - n*std` for non-nan members of vs.  If `minzero` is True (the default), the returned number will not be less than zero."""
    vs = filter_nans(vs)
    if len(vs):
        r = statistics.mean(vs) - (n*statistics.stdev(vs))
        r = 0 if minzero and r < 0 else r
        return r
    else:
        return math.nan

def shi_dev(vs, n=1):
    """Return `mean + n*std` for non-nan members of vs."""
    vs = filter_nans(vs)
    return statistics.mean(vs) + ((n*statistics.stdev(vs)) if len(vs) else math.nan)
    


# Oddballs

def compact_string(s):
    """Simplify whitespace for a more compact string"""
    return re.sub(r"\s+"," ", s)

