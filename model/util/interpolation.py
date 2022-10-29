"""Implements different interoplation methods:
     * linear
     * 2nd order polynomial
     * 3rd order polynomial
     * exponential

  This Python file does not correspond to one of the modules in the original
  Excel implementation of the models. It provides the implementation for
  interpolation methods used in the Adoption Data and TAM Data modules.
"""

import numpy as np
import pandas as pd


def linear_trend(data):
    """Linear trend model.
       Provides implementation for 'Adoption Data'!BY50:CA96 & 'TAM Data' columns BX:BZ
       Arguments: data is a pd.Series used to provide the x+y for curve fitting.
    """

    years = np.arange(2014, 2061)
    years_idx = pd.Index(years, name="Year")
    columns = ["x", "constant", "adoption"]
    data_clean = data.dropna()

    if data_clean.empty: 
        return pd.DataFrame(np.nan, columns=columns, dtype=np.float64, index=years_idx)

    y = data_clean.values
    x = data_clean.index - 2014

    if x.size == 0 or y.size == 0: 
        return pd.DataFrame(np.nan, columns=columns, dtype=np.float64, index=years_idx)

    (slope, intercept) = np.polyfit(x, y, 1)

    n_years = len(years)
    offsets = np.arange(n_years)

    x = offsets * slope
    constant = np.full(n_years, intercept)
    adoption = x + constant

    return pd.DataFrame(np.column_stack([x,constant, adoption]), columns=columns,
                                  dtype=np.float64, index=years_idx)

def poly_degree2_trend(data):
    """2nd degree polynomial trend model.
       Provides implementation for 'Adoption Data'!CF50:CI96 & 'TAM Data' columns CE:CH
       Arguments: data is a pd.Series used to provide the x+y for curve fitting.
    """

    years = np.arange(2014, 2061)
    years_idx = pd.Index(years, name="Year")
    columns = ['x^2', 'x', 'constant', 'adoption']
    data_clean = data.dropna()

    if data_clean.empty: 
        return pd.DataFrame(np.nan, columns=columns, dtype=np.float64, index=years_idx)

    y = data_clean.values
    x = data_clean.index - 2014

    if x.size == 0 or y.size == 0: 
        return pd.DataFrame(np.nan, columns=columns, dtype=np.float64, index=years_idx)

    (c2, c1, intercept) = np.polyfit(x, y, 2)
    n_years = len(years)
    offsets = np.arange(n_years)

    x2 = (offsets ** 2) * c2
    x = offsets * c1
    constant = np.full(n_years, intercept)
    adoption = x + x2 + constant

    return pd.DataFrame(np.column_stack([x2, x, constant, adoption]), columns=columns,
                                  dtype=np.float64, index=years_idx)



def poly_degree3_trend(data):
    """3rd degree polynomial trend model.
       Provides implementation for 'Adoption Data'!CN50:CR96 & 'TAM Data' columns CM:CQ
       Arguments: data is a pd.Series used to provide the x+y for curve fitting.
    """

    years = np.arange(2014, 2061)
    years_idx = pd.Index(years, name="Year")
    columns = ['x^3', 'x^2', 'x', 'constant', 'adoption']
    data_clean = data.dropna()

    if data_clean.empty: 
        return pd.DataFrame(np.nan, columns=columns, dtype=np.float64, index=years_idx)

    y = data_clean.values
    x = data_clean.index - 2014

    if x.size == 0 or y.size == 0: 
        return pd.DataFrame(np.nan, columns=columns, dtype=np.float64, index=years_idx)

    (c3, c2, c1, intercept) = np.polyfit(x, y, 3)
    n_years = len(years)
    offsets = np.arange(n_years)

    x3 = (offsets ** 3) * c3
    x2 = (offsets ** 2) * c2
    x = offsets * c1
    constant = np.full(n_years, intercept)
    adoption = x + x2 + x3 + constant

    return pd.DataFrame(np.column_stack([x3, x2, x, constant, adoption]), columns=columns,
                                  dtype=np.float64, index=years_idx)



def exponential_trend(data):
    """exponential trend model.
       Provides implementation for 'Adoption Data'!CW50:CY96 & 'TAM Data' columns CV:CX
       Arguments: data is a pd.Series used to provide the x+y for curve fitting.
    """
    years = np.arange(2014, 2061)
    years_idx = pd.Index(years, name="Year")
    columns = ['coeff', 'e^x', 'adoption']
    data_clean = data.dropna()

    if data_clean.empty: 
        return pd.DataFrame(np.nan, columns=columns, dtype=np.float64, index=years_idx)

    y = np.log(data_clean.values)
    x = data_clean.index - 2014

    if x.size == 0 or y.size == 0: 
        return pd.DataFrame(np.nan, columns=columns, dtype=np.float64, index=years_idx)

    (ce, coeff) = np.polyfit(x, y, 1)
    n_years = len(years)
    offsets = np.arange(n_years)

    ex = np.exp(offsets * ce)
    coeff = np.full(n_years, np.exp(coeff))
    adoption = ex * coeff

    return pd.DataFrame(np.column_stack([coeff, ex, adoption]), columns=columns,
                                  dtype=np.float64, index=years_idx)



def single_trend(data):
    """Single source model.
       Returns the data from the single source, packaged into a DataFrame compatible
       with the other trend algorithms.
    """
    result = pd.DataFrame(0, index=np.arange(2014, 2061),
            columns=['constant', 'adoption'], dtype=np.float64)
    result.index.name = 'Year'
    result.loc[:, 'constant'] = data.dropna()
    result.loc[:, 'adoption'] = data.dropna()
    return result


def trend_algorithm(data, trend):
    """Fit of data via one of several trend interpolation algorithms."""
    t = trend.lower()
    if t == "linear": return linear_trend(data=data)
    if t == "2nd poly" or t == "2nd_poly" or t == "degree2":
        return poly_degree2_trend(data=data)
    if t == "3rd poly" or t == "3rd_poly" or t == "degree3":
        return poly_degree3_trend(data=data)
    if t == "exponential" or t == "exp":
        return exponential_trend(data=data)
    if t == "single" or t == "single source":
        return single_trend(data)
    raise ValueError('invalid trend algorithm: ' + str(trend))


