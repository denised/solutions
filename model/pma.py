"""Parameter Meta Analysis is one of the original key features of the Project Drawdown approach to modeling.
The basic idea is to collect published research and estimates of values for a parameter, and then choose the value to use
in a scenario from a statistical aggregation of those estimates."""


from pathlib import Path
import dataclasses
import math
import pandas as pd
import yaml
import typing
import model.util.values as values
from model.util.solution_files import raw_pma_data


PMA_Estimate_Attributes = ['Index', 'Value', 'Citation', 'Link', 'Raw Value', 'Raw Units', 'Notes', 'SubDomain']
"""Recognized attributes for PMA estimates.  They have the following meanings:
* Index: index value of the entry, may correspond to references in PMA notes
* Value: the value of the estimate, in PMA units
* Citation: citation information for the source of the estimate
* Link: link information for the citation and/or source of the estimate
* Raw Value: the originally published value, if it is different than Value (e.g. different
  units, or other required conversion)
* Raw Units: the originally published units, if different than the PMA units.
* Notes: any other notes about this estimate
* SubDomain: Sometimes estimates are varied by location, AEZ, or other partition.  The
  SubDomain field may have a comma-separated list of identifiers of those attributes.  Most
  estimates do not use this feature, but an example might be something like: 
    `SubDomain: Latin America, Suburban`"""


@dataclasses.dataclass
class ParameterMetaAnalysis:
    """Meta-analysis of multiple data sources, providing backing data for choice of a scalar parameter."""

    parameter_name : str = None
    """The parameter name this PMA provides backing data for.  Should be one of the parameters in a Params object, such as `conv_first_cost_efficiency_rate`.
    If None, no standard parameter (currently) exists for this data."""
    title: str = None
    """An English language title for PMAs of non-standard parameters"""
    notes : str = None
    """Optional notes for this PMA as a whole"""
    units : str = None
    """A standardized name for the units of this parameter.  Data may have been published in different units, but will always be converted to
    this unit for analysis."""
    estimates : pd.DataFrame = None
    """The main data: a pandas DataFrame with columns defined in @PMA_Estimate_Attributes"""

    @classmethod
    def load_pma(cls, path) -> "ParameterMetaAnalysis":
        """Construct a PMA from a yaml file"""
        raw_pma = raw_pma_data(Path(path))
        # reconstruct the dataframe
        if raw_pma['estimates']:
            raw_pma['estimates'] = pd.DataFrame.from_dict(raw_pma['estimates'])
        return ParameterMetaAnalysis(**raw_pma)
    
    @classmethod
    def load_pma_directory(cls, dirpath) -> typing.List["ParameterMetaAnalysis"]:
        """Load and return an array of all PMA that are defined in the indicated directory"""
        all_pma_raw_data = raw_pma_data(Path(dirpath))
        result = []
        for raw_pma in all_pma_raw_data:
            if raw_pma['estimates']:
                raw_pma['estimates'] = pd.DataFrame.from_dict(raw_pma['estimates'])      
            result.append(ParameterMetaAnalysis(**raw_pma))     
        

    def quantiles(self):
        """Return a set of quantile values over this PMA data."""
        if self.estimates:
            vs = self.estimates['Value']
            return {
                'min': values.smin(vs),
                '25%': values.s25_ile(vs),
                'median': values.smedian(vs),
                '75%': values.s75_ile(vs),
                'max': values.smax(vs)
            }
        else:
            return {
                'min': math.nan,
                '25%': math.nan,
                'median': math.nan,
                '75%': math.nan,
                'max': math.nan                
            }
    
    def low_mean_high(self):
        """Return the set of mean-stdev, stdev, mean+stdev for this PMA data."""
        if self.estimates:
            vs = self.estimates['Value']
            return {
                'low': values.slow_dev(vs),
                'mean': values.smean(vs),
                'hi': values.shi_dev(vs)
            }
        else:
            return {
                'low': math.nan,
                'mean': math.nan,
                'hi': math.nan           
            } 

    def percentile_rank(self, val):
        """The percentile rank returns the position of `val` compared to the dataset.  Since PMAs tend to have few datapoints,
        we extend the definition to include a linear interpolation of `val` between """   
        # TODO
        pass   


    def _to_yaml_form(self):
        """Convert self to structure appropriate for converstion to yaml"""
        dat = self.to_dict()
        if isinstance(dat['estimates'], pd.DataFrame):
            dat['estimates'] = dat['estimates'].to_dict()
        return dat
    
    def to_yaml(self):
        the_data = self._to_yaml_form()
        return yaml.safe_dump(the_data, sort_keys=False)
