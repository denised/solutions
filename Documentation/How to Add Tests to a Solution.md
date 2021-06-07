# How to Add Tests to a Solution

Solutions should be tested by adding test file(s) to their `test` subdirectory.  Because solutions share a
lot of code in common, there is shared testing infrastructure that makes testing each solution much
easier.  This document will cover how to use that shared testing infrastructure.

## Goals of testing

The primary testing that is currently being done for solutions is to test that the output of a solution agrees,
for all sample scenarios, with the saved spreadsheet data for those scenarios.  The saved spreadsheet data
is found in the tests subdirectory in a file called `expected.zip`

## Basics of enabling testing against `Expected.zip`

Assuming your solution already has an `expected.zip` file, do the following to enable testing against it:

Copy from the template below into the file `test_<SOLUTION_NAME>.py` in the tests subdirectory of the solution:

```python
import pytest
import tests.test_solutions as testbase

class Test_<SOLUTION_NAME> (<BASECLASS>):
    solution_name = "<SOLUTION_NAME>"
```

Replace `<SOLUTION_NAME>` with the code name of the solution, e.g. 'afforestation' or 'solarpvutil'.

The base class will determine what suite of tests to run against this solution.  For many solutions,
this will be one of:

* `testbase.RSSSolutionTester` for RSS type solutions
* `testbase.LANDSolutionTester` for Land type solutions

(For other situations see the section on inheritance below).

That's it!

### Running tests just against one solution

It can be convenient during development to run tests just against a single solution.  You can do this by running
the following command from the main solutions directory:

```shell
python -m pytest solution/<SOLUTION_NAME>
```

## Customizing the Tests

The solution testing system is designed to make the common case quite easy, while still allow considerable
customization to support the unique needs of different solutions.  

### Limiting the tested scenarios

By default, tests are run against all scenarios of the solution.  To test only a subset of the scenarios, add the
following variable in the test class:

```python
class test_<SOLUTION_NAME> (<BASECLASS>):
    solution_name = "<SOLUTION_NAME>"
    scenarios_to_test = [<LIST SCENARIOS>]
```

The list can either be a list of scenario names or a list of scenario indices (zero based).  So, for example to test
the first two scenarios only, you could write:
```python
    scenarios_to_test = [0,1]
```

### Customizing test inheritance

The solution test suite is sectioned into chunks arranged around particular tabs of the spreadsheet.  If neither
`testbase.RSSSolutionTester` or `testbase.LANDSolutionTester` are right for your solution, you can pick and
choose from these chunks yourself, using multiple inheritence.  For example you might have something like:

```python
class test_<SOLUTION_NAME> (testbase.SolutionTAMTester, testbase.SolutionOperatingCostTester, ...):
```

TODO: This needs to be expanded as we actually write those classes....

### Overriding specific tests

A standard test may behave incorrectly for a specific solution for some reason.  For example, some of the equations
might be mathematically unstable resulting in failing comparisons between the code and the saved data in `expected.zip`.

When this occurs it is easy to create a local override to a particular test in your test file.  Start by copying
the code of the existing test into your class:

```python
class test_<SOLUTION_NAME> (<BASECLASS>):
    solution_name = "<SOLUTION_NAME>"
    scenarios_to_test = [<LIST SCENARIOS>]

    def test_tm_forecast_low_med_high( self, scenario, region, expected_tm ):
        actual = scenario.tm.forecast_low_med_high( region=region )
        eloc = self.tam_adjust( self.tm_forecast_low_med_high_locations[region] )
        expected = xlt.excel_range_from_df( expected_tm, eloc )
        self.diff_test( actual, expected )
```

Then alter whatever you need to about this test, for example:

```python
    def test_tm_forecast_low_med_high( self, scenario, region, expected_tm ):
        actual = scenario.tm.forecast_low_med_high( region=region )
        eloc = self.tam_adjust( self.tm_forecast_low_med_high_locations[region] )
        expected = xlt.excel_range_from_df( expected_tm, eloc )
        if region != 'World':
            # Years before 2030 are not set properly and should be excluded from the test
            # So mask them to zero
            actual.iloc[:15,:] = 0
            expected.iloc[:15,:] = 0
        self.diff_test( actual, expected )
```

### Adding your own tests

You can also, of course, add your own tests to the test suite.  Tests must begin with the name `test_`, and they
may be placed anywhere in the test file (in the class or outside of it).

The big advantage to putting a test in the test class is that you get access to "fixtures" which are magic parameters
that come pre-filled for you to use.  Fixtures that are available to you include:

* `scenario`:  An instantiated `Scenario` object for your solution.
* `region`: A region string (e.g. 'World', 'China', etc.) for tests that need to test each region essentially identically.
* `expected_*`:  A `DataFrame` containing the corresponding sheet from `expected.zip` for this scenario.  For example,
`expected_tm` contains the entire `TAM Info` sheet.

TODO: expand and refine as we actually create all these things.
The test will be executed for each value these fixtures take on (e.g. for each scenario and region).

Looking at the existing tests in `tests/test_solutions.py` will give you a good idea of how the fixtures are used, and
other tools that are available.

## Managing the `expected.zip` file

TODO: Fill this out.

