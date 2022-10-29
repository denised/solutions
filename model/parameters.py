
"""Parameters are key to defining Scenarios: a Scenario can be thought of as a Solution plus a set of Parameter values.
Different Solutions use different kinds of parameters.  The most commonly used parameter sets are defined in this package, but it is possible
for any individual Solution to define its own parameter set by inheriting from one of these classes.

Some things to know about Parameters / Parameter Sets:

Every Solution comes with a "reference parameter set" which defines the parameter values for the 'reference' or 'normal' case.  Scenarios then
only provide values that _differ_ from the reference parameters.  Typically adoption will be different, but other parameters may also be
different.  The effective parameter values for a scenario are determined by combining these two value sets.

# TODO soln vs conv params.

Each parameter value may have metadata associated with it.  In some cases the metadata is produced automatically
by certain calculations (particularly used when transcribing values extracted from the original Excel models), while in other cases
metadata may be hand-written by a scenario designer.

Parameter Sets are serialized to/from Yaml, which is the form developers will most often encounter them as.

Parameter Sets may be modified up until they are `locked`.  Locking happens when a parameter set is used to create a Scenario,
in order to guarantee that calculations will be consistent.  A new modifyable parameter set can be created by copying an existing one.

Hierarchy of classes:

    ParameterSet
     +--> ScenarioParams
           +--> RSSScenarioParams
           +--> LandScenarioParams 
           +--> OceanScenarioParams

"""
from typing import Optional
from dataclasses import field
import pandas as pd
from model.util.parameter_set import ParameterSet, ps_dataclass


@ps_dataclass
class ScenarioParams(ParameterSet):
    """The set of parameters common to all Solutions/Scenarios."""
    
    # Basic information

    scenario_name: str = None
    """Name of this scenario"""

    description: str = None
    """Freeform text describing this scenario"""

    creation_date: str = None
    """Creation date of this scenario, in %Y-%m-%d %H:%M:%S format."""
   
    report_start_year: int = 2020
    """The first year of results to report."""
    # excelref: SolarPVUtil "Advanced Controls"!H4
    # Note: many parts of the code have year 2014 hardwired because the initial Excel models
    # were developed then.  However any results generated for dates < report_start_year is not
    # necessarily accurate.

    # Cost Parameters

    soln_first_cost: float = 0.0
    """SOLUTION First Cost per Implementation Unit

    The cost of acquisition and the cost of installation (sometimes one and the same) or the
    cost of initiating a program/practice (for solutions where there is no direct artifact to
    acquire and install) per Implementation unit of the SOLUTION.

    E.g. What is the cost to acquire and install rooftop solar PV?"""
    # excelref: SolarPVUtil "Advanced Controls"!B128

    conv_first_cost: float = 0.0
    """CONVENTIONAL First Cost per Implementation Unit for replaced practices/technologies

    The cost of acquisition and the cost of installation (sometimes one and the same) or the cost
    of initiating a program/practice (for solutions where there is no direct artifact to acquire
    and install) per Unit of Implementation of the CONVENTIONAL mix of practices (those practices
    that do not include the technology in question.

    E.g. What is the cost to purchase an internal combustion engine vehicle?"""
    # excelref: SolarPVUtil "Advanced Controls"!B95


    # TODO: move these  comments to the costs code when it exists.
    # Learning curves (sometimes called experience curves) are used to analyze a well-known
    # and easily observed phenomena: humans become increasingly efficient with experience. The
    # first time a product is manufactured or a service provided, costs are high, work is
    # inefficient, quality is marginal, and time is wasted.   As experience is acquired, costs
    # decline, efficiency and quality improve, and waste is reduced.
    #
    # In many situations, this pattern of improvement follows a predictable pattern: for every
    # doubling of (or some multiple of) production of units, the 'cost' of production (measured in
    # dollars, hours, or in terms of other inputs) declines to some fraction of previous costs.
    # The efficiency rate is the percentage that first cost decreases with every doubling of units.

    soln_first_cost_efficiency_rate: float = 0.0
    """SOLUTION First Cost Learning Rate
    
    The percentage by which the first cost declines with every doubling of SOLUTION
    implementation units produced."""
    # excelref: SolarPVUtil "Advanced Controls"!C128


    conv_first_cost_efficiency_rate: float = 0.0
    """CONVENTIONAL First Cost Learning Rate

    The percentage by which the first cost declines with every doubling of CONVENTIONAL
    implementation units produced. In many/most cases this will be 0% if the conventional
    market is mature."""
    # excelref: SolarPVUtil "Advanced Controls"!C95


    soln_first_cost_below_conv: bool = True
    """Allow Solution First Cost to be less than Conventional?
    
    The Solution First Cost may decline below that of the Conventional due to the learning
    rate chosen. This may be acceptable in some cases for instance when the projections in the
    literature indicate so. In other cases, it may not be likely for the Solution to become
    cheaper than the Conventional."""
     # excelref: SolarPVUtil "Advanced Controls"!C132


    # Adoption

    projected_adoption : pd.DataFrame = field(default=None, metadata={'pdtype':'regional'})
    """The projected adoption curve (in Functional Units) assumed for this Scenario."""

    current_adoption: float = None
    """The currently observed worldwide adoption (in Functional Units) as of the start year of the solution.
    (Note: this value is not currently used in calculation, but may be used by the user for analysis, or to
    generate adoption curves.)"""
    # excelref: as "Current Adoption", airplanes "Advanced Controls"!C61

#     soln_energy_efficiency_factor: float = None # double check
#         # subtitle: ,
#         'tooltip': ("Energy Efficiency Factor SOLUTION
#   soln_energy_efficiency_factor: Units of energy reduced per year per   functional unit installed.

#   FOR CLEAN RENEWABLE ENERGY SOLUTIONS: enter 0 (e.g. implementing solar PV   fully replaces existing fossil fuel-based generation, but does not reduce   the amount of energy generated)

#   FOR ENERGY EFFICIENCY SOLUTIONS: enter positive number representing total   energy reduced, 0 < X < 1 (e.g. HVAC efficiencies reduce the average annual   energy consumption of buildings, by square meters of floor space; they still   use the electric grid, but significantly less)

#   FOR SOLUTIONS THAT CONSUME MORE ENERGY THAN THE CONVENTIONAL TECHNOLOGY/PRACTICE:   Use the next input, Total Annual Energy Used SOLUTION (e.g. electric vehicles   use energy from the electric grid, whereas conventional vehicles use only fuel)"
#             ),
#         # excelref: SolarPVUtil "Advanced Controls"!C159; Silvopasture "Advanced Controls"!C123


#     conv_annual_energy_used: float = None # double check
#         # subtitle: ,
#         """Average Electricty Used CONVENTIONAL
#   NOTE: for solutions that reduce electricity consumption per functional unit,   enter the
#   average electricity used per functional unit of the conventional   technologies/practices."""
#         # excelref: SolarPVUtil "Advanced Controls"!B159; Silvopasture "Advanced Controls"!B123


#     soln_annual_energy_used: float = None # double check
#         # subtitle: ,
#         """ALTERNATIVE APPROACH Annual Energy Used SOLUTION
#   This refers to the units of average energy used per year per functional unit   installed.

#   This is an optional variable to be used in cases where a) the literature   reports the energy
#   use of the solution rather than energy efficiency; or   b) the solution uses more electricity
#   than the conventional   technologies/practices.

#   E.g. electric vehicles use energy from the electric grid, whereas   conventional vehicles use
#   only fuel"""
#         # excelref: SolarPVUtil "Advanced Controls"!D159


#     conv_fuel_consumed_per_funit: float = None # double check
#         # subtitle: ,
#         """Fuel Consumed per CONVENTIONAL Functional Unit
#   This refers to the unit (default is Liters) of FUEL used per year per   cumulative unit
#   installed. The equation may need to be edited if your   energy savings depend on the marginal
#   unit installed rather than the   cumulative units."""
#         # excelref: SolarPVUtil "Advanced Controls"!F159; Silvopasture "Advanced Controls"!F123


#     soln_fuel_efficiency_factor: float = None # double check
#         # subtitle: ,
#         """Fuel Efficiency Factor - SOLUTION
#   This refers to the % fuel reduced by the SOLUTION relative to the   CONVENTIONAL mix of
#   technologies/practices. The Percent reduction is   assumed to apply to the Conventional Fuel
#   Unit, if different to the   Solution Fuel Unit.

#   FOR REPLACEMENT SOLUTIONS: enter 1 (e.g. electric vehicles fully replace fuel   consumption
#   with electricity use -- but be sure to add a negative value for   Annual Energy Reduced from
#   Electric Grid Mix!)

#   FOR FUEL EFFICIENCY SOLUTIONS: enter positive number representing total fuel   reduced, 0 < X
#   < 1  (e.g. hybrid-electric vehicles partially replace fuel   consumption with electricity
#   use, it thus uses less fuel compared to conventional   vehicles)

#   FOR SOLUTIONS THAT CONSUME MORE FUEL THAN THE CONVENTIONAL TECHNOLOGY/PRACTICE:   enter
#   negative number representing total additional fuel used, X < 0 (e.g. we   hope solutions do
#   not actually consume more fuel than the conventional practice,   check with the senior
#   research team if you run into this)"""
#         # excelref: SolarPVUtil "Advanced Controls"!G159; Silvopasture "Advanced Controls"!G123


#     conv_fuel_emissions_factor: float = None # double check
#         # subtitle: ,
#         'tooltip': 'direct fuel emissions per funit, conventional',
#         # excelref: SolarPVUtil "Advanced Controls"!I159


#     soln_fuel_emissions_factor: float = None # double check
#         # subtitle: ,
#         'tooltip': 'direct fuel emissions per funit, solution',
#         # excelref: SolarPVUtil "Advanced Controls"!I163; DistrictHeating "Advanced
#         # Controls"!I144


#     conv_emissions_per_funit: float = None # double check
#         # subtitle: ,
#         """Direct Emissions per CONVENTIONAL Functional Unit
#   This represents the direct CO2-eq emissions that result per functional unit   that are not
#   accounted for by use of the electric grid or fuel consumption."""
#         # excelref: SolarPVUtil "Advanced Controls"!C174


#     soln_emissions_per_funit: float = None # double check
#         # subtitle: ,
#         """Direct Emissions per SOLUTION Functional Unit
#   This represents the direct CO2-eq emissions that result per functional unit   that are not
#   accounted for by use of the electric grid or fuel consumption."""
#         # excelref: SolarPVUtil "Advanced Controls"!D174


#     # ch4_is_co2eq: True if CH4 emissions measurement is in terms of CO2 equivalent, False if
#     #   measurement is in units of CH4 mass.  derived from SolarPVUtil "Advanced Controls"!I184
#     ch4_is_co2eq: bool = None

#     # n2o_is_co2eq: True if N2O emissions measurement is in terms of CO2 equivalent, False if
#     #   measurement is in units of N2O mass.  derived from SolarPVUtil "Advanced Controls"!J184
#     n2o_is_co2eq: bool = None

#     # co2eq_conversion_source: One of the conversion_source names defined in
#     #   model/emissions_factors.py like "AR5 with feedback" or "AR4" SolarPVUtil "Advanced
#     #   Controls"!I185
#     co2eq_conversion_source: str = None

#     ch4_co2_per_funit: float = None # double check
#         # subtitle: ,
#         """CH4-CO2eq Tons Reduced
#   CO2-equivalent CH4 emitted per functional unit, in tons."""
#         # excelref: SolarPVUtil "Advanced Controls"!I174


#     n2o_co2_per_funit: float = None # double check
#         # subtitle: ,
#         """N2O-CO2eq Tons Reduced
#   CO2-equivalent N2O emitted per functional unit, in tons."""
#         # excelref: SolarPVUtil "Advanced Controls"!J174


#     soln_indirect_co2_per_iunit: float = None # double check
#         # subtitle: ,
#         """Indirect CO2 Emissions per SOLUTION Implementation Unit
#   CO2-equivalent indirect emissions per iunit, in tons."""
#         # excelref: SolarPVUtil "Advanced Controls"!G174


#     conv_indirect_co2_per_unit: float = None # double check
#         # subtitle: ,
#         """Indirect CO2 Emissions per CONVENTIONAL Implementation OR functional Unit
#   NOTE: this represents the indirect CO2 emissions that result per implementation   unit
#   installed. The production, distribution, and installation of   technologies/practices often
#   generate their own emissions that are not associated   with their function.

#   E.g. the production of ICE vehicles is an energy- and resource-intensive endeavor   that
#   generates indirect emissions that must be accounted for.
# """
#         # excelref: SolarPVUtil "Advanced Controls"!F174


#     # conv_indirect_co2_is_iunits: whether conv_indirect_co2_per_unit is iunits (True) or
#     #   funits (False).  SolarPVUtil "Advanced Controls"!F184
#     conv_indirect_co2_is_iunits: bool = None

#     soln_lifetime_capacity: float = None # double check
#         # subtitle: (use until replacement is required),
#         """Lifetime Capacity - SOLUTION

#   NOTE: This is the average expected number of functional units generated by the   SOLUTION
#   throughout their lifetime before replacement is required. If no replacement   time is
#   discovered or applicable the fellow will default to 100 years.

#   E.g. an electric vehicle will have an average number of passenger kilometers it   can travel
#   until it can no longer be used and a new vehicle is required. Another   example would be an
#   efficient HVAC system, which can only service a certain amount   of floor space over a period
#   of time before it will require replacement."""
#         # excelref: SolarPVUtil "Advanced Controls"!E128


#     soln_avg_annual_use: float = None # double check
#         # subtitle: (annual use),
#         """Average Annual Use - SOLUTION

#   NOTE:  Average Annual Use is the average annual use of the technology/practice,   in
#   functional units per implementation unit. This will likely differ significantly   based on
#   location, be sure to note which region the data is coming from. If data   varies
#   substantially by region, a weighted average may need to be used.

#   E.g. the average annual number of passenger kilometers (pkm) traveled per   electric
#   vehicle."""
#         # excelref: SolarPVUtil "Advanced Controls"!F128


#     conv_lifetime_capacity: float = None # double check
#         # subtitle: (use until replacement is required),
#         """Lifetime Capacity - CONVENTIONAL

#   NOTE: This is the average expected number of functional units   generated by the CONVENTIONAL
#   mix of technologies/practices   throughout their lifetime before replacement is required.
#   If no replacement time is discovered or applicable, please   use 100 years.

#   E.g. a vehicle will have an average number of passenger kilometers   it can travel until it
#   can no longer be used and a new vehicle is   required. Another example would be an HVAC
#   system, which can only   service a certain amount of floor space over a period of time before
#   it will require replacement."""
#         # excelref: SolarPVUtil "Advanced Controls"!E95


#     conv_avg_annual_use: float = None # double check
#         # subtitle: (annual use),
#         """Average Annual Use - CONVENTIONAL

#   NOTE:  Average Annual Use is the average annual use of the technology/practice,   in
#   functional units per implementation unit. This will likely differ significantly   based on
#   location, be sure to note which region the data is coming from. If data   varies
#   substantially by region, a weighted average may need to be used.

#   E.g. the average annual number of passenger kilometers (pkm) traveled per   conventional
#   vehicle.
# """
#         # excelref: SolarPVUtil "Advanced Controls"!F95


#     soln_var_oper_cost_per_funit: float = None # double check
#         # subtitle: (functional units),
#         """SOLUTION Variable Operating Cost (VOM)
#   NOTE: This is the annual operating cost per functional unit, derived from the   SOLUTION. In
#   most cases this will be expressed as a cost per 'some unit of   energy'.

#   E.g., $1 per Kwh or $1,000,000,000 per TWh. In terms of transportation, this   can be
#   considered the weighted average price of fuel per passenger kilometer."""
#         # excelref: SolarPVUtil "Advanced Controls"!H128


#     soln_fixed_oper_cost_per_iunit: typing.Any = None # double check
#             'SOLUTION Fixed Operating Cost (FOM)'],
#         # subtitle: (per ha per annum),
#         """SOLUTION Operating Cost per Functional Unit per Annum

#   NOTE: This is the Operating Cost per functional unit, derived from the   SOLUTION. In most
#   cases this will be expressed as a cost per 'hectare of   land'.

#   This annualized value should capture both the variable costs for maintaining   the SOLUTION
#   practice as well as the fixed costs. The value should reflect   the average over the
#   reasonable lifetime of the practice."""
#         # That tooltip is phrased for land solutions, one for RRS would be:
#         'tooltipFIXME': ("SOLUTION Operating Cost per Functional Unit per Annum

#   NOTE: This is the annual operating cost per implementation unit, derived from   the SOLUTION.  In most cases this will be expressed as a cost per 'some unit of   installation size' E.g., $10,000 per kw. In terms of transportation, this can be   considered the total insurance, and maintenance cost per car.

#   Purchase costs can be amortized here or included as a first cost, but not both."),
#         # excelref: SolarPVUtil "Advanced Controls"!I128; Silvopasture "Advanced Controls"!C92


#     # soln_fuel_cost_per_funit: Fuel/consumable cost per functional unit.  SolarPVUtil
#     #   "Advanced Controls"!K128
#     soln_fuel_cost_per_funit: float = None

#     conv_var_oper_cost_per_funit: float = None # double check
#         # subtitle: (functional units),
#         """CONVENTIONAL Variable Operating Cost (VOM)

#   NOTE: This is the annual operating cost per functional unit, derived from the   CONVENTIONAL
#   mix of technologies. In most cases this will be expressed as a   cost per 'some unit of
#   energy'.

#   E.g., $1 per Kwh or $1,000,000,000 per TWh. In terms of transportation, this   can be
#   considered the weighted average price of fuel per passenger kilometer."""
#         # excelref: SolarPVUtil "Advanced Controls"!H95


#     # conv_fixed_oper_cost_per_iunit: as soln_fixed_oper_cost_per_funit.  SolarPVUtil "Advanced
#     #   Controls"!I95 / Silvopasture "Advanced Controls"!C77
#     conv_fixed_oper_cost_per_iunit: typing.Any = None # double check
#             'CONVENTIONAL Fixed Operating Cost (FOM)'],
#         # subtitle: (per ha per annum),
#         """CONVENTIONAL Operating Cost per Functional Unit per Annum

#   NOTE: This is the Operating Cost per functional unit, derived   from the CONVENTIONAL mix of
#   technologies/practices.  In most   cases this will be expressed as a cost per 'hectare of
#   land'.

#   This annualized value should capture the variable costs for   maintaining the CONVENTIONAL
#   practice, as well as  fixed costs.   The value should reflect the average over the reasonable
#   lifetime   of the practice.

# """
#         # excelref: SolarPVUtil "Advanced Controls"!I95; Silvopasture "Advanced Controls"!C77


#     # conv_fuel_cost_per_funit: as soln_fuel_cost_per_funit.  SolarPVUtil "Advanced
#     #   Controls"!K95
#     conv_fuel_cost_per_funit: float = None

#     # npv_discount_rate: discount rate for Net Present Value calculations.  SolarPVUtil
#     #   "Advanced Controls"!B141
#     npv_discount_rate: float = None

#     # emissions_use_co2eq: whether to use CO2-equivalent for ppm calculations.  SolarPVUtil
#     #   "Advanced Controls"!B189 emissions_grid_source: "IPCC Only" or "Meta Analysis" of
#     # multiple studies.  SolarPVUtil "Advanced Controls"!C189 emissions_grid_range: "mean",
#     #   "low" or "high" for which estimate to use.  SolarPVUtil "Advanced Controls"!D189
#     emissions_use_co2eq: bool = None
#     emissions_grid_source: str = None
#     emissions_grid_range: str = None

    

#     # emissions_use_agg_co2eq: Use Aggregate CO2-eq instead of Individual GHG for direct
#     #  emissions ForestProtection "Advanced Controls"!C155 (Land models)
#     emissions_use_agg_co2eq: bool = None


#     # soln_expected_lifetime: solution expected lifetime in years "Advanced Controls"!F92 (Land
#     #   models) conv_expected_lifetime: conventional expected lifetime in years. Default value
#     # is 30.  "Advanced Controls"!F77 (Land models)
#     soln_expected_lifetime: float = None
#     conv_expected_lifetime: float = None





@ps_dataclass
class RRSParams(ScenarioParams):
    """Parameters common to RRS Solutions/Scenarios"""

    total_addressable_market : pd.DataFrame = field(default=None,metadata={'pdtype':'regional'})
    """The available demand for the value this Solution provides (its 'Functional
    Units'), projected out over years (and sometimes by regions).
     
    The Total Addressable Market (TAM) represents an upper limit of the number of Functional
    Units that can be produced by this solution in any given region/year."""




@ps_dataclass
class LandParams(ScenarioParams):
    """Parameters common to Land Solutions/Scenarios"""

