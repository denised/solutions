"""Main test driver for solution testing."""

import pytest
import pandas as pd
from tools import excel_tools as xlt
from model.solution import Solution

class BaseSolutionTester:
    """All Solution tests derive from this class."""
 
    # ############################
    # Parameters that can be overridden by individual solution test classes
    # Note: intermediate test classes (like those appearing below) may add
    # additional parameters, but must not alter these parameters.

    solution_name = None
    """Every solution test *must* override the solution_name attribute"""
    
    scenarios_to_test = None
    """By default, all scenarios are tested.  To restrict testing to a subset
    of scenarios, override this parameter with the list (either by name or index).
    For example, to test only the first scenario, set `self.scenarios_to_test = [0]`"""

    _patched = False     # See pytest_generate_tests below.
    
    # ############################
    # general test infrastructure

    @pytest.fixture(scope='class')
    def scenario_names(self):
        slist = Solution.scenario_list(self.solution_name)
        if self.scenarios_to_test is not None:
            temp = self.scenarios_to_test
            if len(temp) and isinstance(temp[0], int):
                temp = [slist[i] for i in temp]
            slist = temp
        return slist
    
    @classmethod 
    def scenario_count(cls):
        if cls.scenarios_to_test is not None:
            return len(cls.scenarios_to_test)
        else:
            return Solution.scenario_count(cls.solution_name)

    # This is a hack to work around a limitation in pytest.
    # The effect is to set the params on the scenario_number fixture below
    # to the correct value.  Don't look too closely or your eyes will hurt.
    # (The limitation is that pytest params can only be specified statically, but
    # we want them defined per-solution.  So the first chance after the tests
    # are collected but before they are parameterized, we sneak in and replace
    # the parameter value with the correct one.)
    @pytest.hookimpl(tryfirst=True)
    def pytest_generate_tests(self,metafunc):
        if hasattr(metafunc.cls, '_patched') and not metafunc.cls._patched:
            fparams = getattr(metafunc,'_arg2fixturedefs',None)
            if fparams and 'scenario_number' in fparams:
                fixture = fparams['scenario_number'][0]
                num_scenarios = metafunc.cls.scenario_count()
                fixture.params = range(num_scenarios)  # this is the override
                metafunc.cls._patched = True

    # The scenario_number fixture controls iteration through all the scenarios
    # we will test.  Its list of values gets set the hook above.
    # Most tests won't use this fixture directly, but will simply reference
    # the scenario fixture below.
    @pytest.fixture(scope='class',params=[0,1])
    def scenario_number(self,request):
        return request.param
    
    @pytest.fixture(scope='class')
    def scenario(self, scenario_number, scenario_names):
        """The loaded scenario that is currently being tested."""
        this_name = scenario_names[scenario_number]
        print(f'\nBeginning {self.solution_name}:"{this_name}"\n')
        soln = Solution(self.solution_name, scenario_names=[this_name])
        return soln.scenarios[0]
    
    # This fixture just loops over the regions, so tests can be parameterized by region instead
    # of spelled out individually.
    @pytest.fixture(scope='function',params=[
        'World',
        'OECD90',
        'Eastern Europe',
        'Asia (Sans Japan)',
        'Middle East and Africa',
        'Latin America',
        'China',
        'India',
        'EU',
        'USA'])
    def region(self, request, scenario):
        """Region iterator.  Use in tests that need to be repeated for each region"""
        # Scenario is requested to make sure this parameter loops *inside* scenario.
        # That isn't actually a requirement to do, but it makes the output easier to understand
        return request.param

    
    def diff_test(self, actual, expected, thresh=None):
        """Fail the test if diff is not empty"""
        diff = xlt.df_differ(actual, expected, thresh)
        if diff:
            pytest.fail( f'{len(diff)} values differed, beginning with: \n{diff[:min(10,len(diff))]}')

    # ######################
    # end BaseSolutionTester
    

# The following classes group tests for each different spreadsheet tab.  
# They will be incorporated by RSSSolutionTester or LandSolutionTester below,
# but they can also be inherited directly by any solutions that don't quite fit
# into those frameworks

class SolutionTAMTester(BaseSolutionTester):
    # Tests of the TAM sheet

    @pytest.fixture(scope='class')
    def expected_tm(self, scenario):
        """All the data on the TAM Data sheet in a single pandas DataFrame"""
        return xlt.solution_expected_results(self.solution_name, scenario.scenario, "TAM Data")
    

    tam_adjust_columns = 0
    """Some solutions, first noticed with ImprovedCookStoves, have a smaller set of columns to
    hold data sources and this shifts all of the rest of the columns to the left.
    In those cases, override tam_adjust_columns to the required amount (usually -4).
    """
    
    # Adjust column range according to need.
    def tam_adjust(self, erange):
        if self.tam_adjust_columns:
            erange = xlt.range_shift(column_shift=self.tam_adjust_columns)
        return erange


    tm_forecast_min_max_sd_locations = {
            'World': 'W46:Y94',
            'OECD90': 'W164:Y212',
            'Eastern Europe': 'W228:Y276',
            'Asia (Sans Japan)': 'W291:Y339',
            'Middle East and Africa': 'W354:Y402',
            'Latin America': 'W417:Y465',
            'China': 'W480:Y528',
            'India': 'W544:Y592',
            'EU': 'W608:Y656',
            'USA': 'W673:Y721'
        }
    def test_tm_forecast_min_max_sd(self, scenario, region, expected_tm):
        actual = scenario.tm.forecast_min_max_sd(region=region)
        eloc = self.tam_adjust(self.tm_forecast_min_max_sd_locations[region])
        expected = xlt.excel_range_from_df(expected_tm, eloc)
        self.diff_test(actual, expected)
    
    tm_forecast_low_med_high_locations = {
            'World': 'AA46:AC94',
            'OECD90': 'AA164:AC212',
            'Eastern Europe': 'AA228:AC276',
            'Asia (Sans Japan)': 'AA291:AC339',
            'Middle East and Africa': 'AA354:AC402',
            'Latin America': 'AA417:AC465',
            'China': 'AA480:AC528',
            'India': 'AA544:AC592',
            'EU': 'AA608:AC656',
            'USA': 'AA673:AC721'
        }
    def test_tm_forecast_low_med_high( self, scenario, region, expected_tm ):
        actual = scenario.tm.forecast_low_med_high( region=region )
        eloc = self.tam_adjust( self.tm_forecast_low_med_high_locations[region] )
        expected = xlt.excel_range_from_df( expected_tm, eloc )
        self.diff_test( actual, expected )


    # These are the locations for 'Linear' only; we use additions to get
    # the other trends.
    tm_forecast_trend_locations = {
            'World': 'BX50:BZ96',
            'OECD90': 'BX168:BZ214',
            'Eastern Europe': 'BX232:BZ278',
            'Asia (Sans Japan)': 'BX295:BZ341',
            'Middle East and Africa': 'BX358:BZ404',
            'Latin America': 'BX421:BZ467',
            'China': 'BX484:BZ530',
            'India': 'BX548:BZ594',
            'EU': 'BX612:BZ658',
            'USA': 'BX677:BZ723'        
    }
    def test_tm_forcast_trend(self, scenario, region, expected_tm ):
        # This test covers all of the trends Linear, Degree2, Degree3 and Exponential
        # It will fail at the first failure.

        # Linear test
        actual = scenario.tm.forecast_trend(region=region, trend='Linear')
        linearloc = self.tam_adjust( self.tm_forecast_trend_locations[region] )
        expected = xlt.excel_range_from_df( expected_tm, linearloc )
        self.diff_test( actual, expected )

        # For the others, the situation is more complicated:
        # If the TAM/Adoption data being analyzed is very close to linear, then the 2nd/3rd order
        # polynomial and exponential curve fits degenerate to where only the x^1 and constant terms
        # matter and the higher order terms do not.
        #
        # For example in biochar, Excel and Python both come up with {x}=1.57e+07 & const=1.049e+09
        # For degree2, Python comes up with -1.15e-09 while Excel decides it is -1.32e-09, but
        # it doesn't matter because they are 16 orders of magnitude less than the {x} term.
        #
        # If the data is very close to linear, skip comparing the higher order curve fits.
        actual = scenario.tm.forecast_trend(region=region, trend='Degree2')
        mask_unstable_data = ( abs( actual.loc[2015, 'x'] / actual.loc[2015, 'x^2'] ) > 1e12 )

        degree2loc = xlt.range_shift( linearloc, column_shift=7, width_set=4 )
        expected = xlt.excel_range_from_df( expected_tm, degree2loc )
        if mask_unstable_data:
            actual['x^2'] = 0
            expected[0] = 0
        self.diff_test( actual, expected )

        actual = scenario.tm.forecast_trend(region=region, trend='Degree3')
        degree3loc = xlt.range_shift( degree2loc, column_shift=8, width_set=5 )
        expected = xlt.excel_range_from_df( expected_tm, degree3loc )
        if mask_unstable_data:
            actual['x^3'] = 0
            actual['x^2'] = 0
            expected[0] = 0
            expected[1] = 0
        self.diff_test( actual, expected )

        actual = scenario.tm.forecast_trend(region=region, trend='Exponential')
        exploc = xlt.range_shift( degree3loc, column_shift=9, width_set=3 )
        expected = xlt.excel_range_from_df( expected_tm, exploc )
        if mask_unstable_data:
            actual['e^x'] = 0
            expected[1] = 0
        self.diff_test( actual, expected )


class SolutionOperatingCostTester(BaseSolutionTester):

    def test_oc_online(cls):
        assert True

class RSSSolutionTester(SolutionTAMTester, SolutionOperatingCostTester):
        
    pass

class LANDSolutionTester(SolutionOperatingCostTester):
    pass


# import solution.factory

# solutions = solution.factory.all_solutions_scenarios()

# @pytest.mark.slow
# @pytest.mark.parametrize("name,constructor,scenarios",
#     [(name,) + solutions[name] for name in solutions.keys()],
#     ids=list(solutions.keys())
# )
# def test_solutions(name, constructor, scenarios):
#     for scenario in scenarios:
#         obj = constructor(scenario=scenario)
#         assert obj.scenario == scenario
#         assert obj.name

#         # a few solutions currently fail and are skipped while we investigate.
#         skip = ['Car Fuel Efficiency', 'Electric Vehicles', 'Insulation']
#         # a few more solutions have cached values from Drawdown2020 which are incorrect for
#         # the BookEdition scenarios, or vice-versa.
#         skip += ['Farmland Restoration', 'Afforestation', 'Bamboo', 'Nutrient Management',
#                  'Perennial Bioenergy Crops', 'Silvopasture', 'Managed Grazing',
#                  'Tropical Tree Staples', 'Temperate Forest Restoration', 'SRI',
#                  'Multistrata Agroforestry', 'Improved Rice', 'Regenerative Agriculture',
#                  'Grassland Protection', 'Peatland Protection', 'IP Forest Management',
#                  'Tree Intercropping', 'Mangrove Protection', 'Conservation Agriculture',
#                  'Forest Protection', 'Aircraft Fuel Efficiency', 'Bike Infrastructure',
#                  'Composting', 'Alternative Cements']
#         if obj.name not in skip:
#             errstr = f"{obj.name}: {scenario} : {obj.ac.incorrect_cached_values}"
#             assert len(obj.ac.incorrect_cached_values) == 0, errstr

#     # check default scenario
#     obj = constructor(scenario=None)
#     assert obj.scenario is not None


# def test_sane_number_of_solutions():
#     assert len(list(solutions.keys())) >= 60
