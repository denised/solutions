"""Solutions are the technological and procedural practices that are proposed for reducing
climate risk.  Solutions come in three types:
* RRS Solutions either _Reduce_ the need for a high-footprint resource (e.g. electricity) or
  _Replace_ an existing good or service with one of lower ghg effect (e.g. bikes instead of
  cars).
* Land Solutions are land-usage techniques that may improve existing land-use efficiency (e.g.
  increasing crop yield), reduce the ghg effects of land use (e.g. reducing fertilizer use),
  and/or introduce or augment the land's ability to sequester carbon dioxide.
* Ocean Solutions are similar to land solutions, but applied to ocean areas.

Each Solution has its own class, defined in the `solutions` module.
"""
from pathlib import Path
from typing import List, Dict, Any, Union
import importlib
import types
from model.parameters import ScenarioParams
from model.scenario import Scenario
from model.util.solution_files import *


SOLUTIONS_DIR = Path(__file__).parents[1]/"solutions"
"""Path to directory that contains the standard solutions"""


def load_solution(solution_name) -> "Solution":
    """Create and return the solution `solution_name`, which should be a solution identifier like '`improvedrice`' that is in SOLUTIONS_DIR."""

    module_name = "solutions." + solution_name
    m = importlib.import_module(module_name)
    # Note: importing a module multiple times is harmless and efficient.
    # In the old code, there was an importlib.reload(m) here to handle the case where the user was modifying the solution and
    # would expect the updated code.  But this is not really an issue now, since the code content of a solution is usually very minor and
    # not likely to change.  In the case where that code *does* change, the developer should use load_solution_from_module directly, and handle
    # their own reloads.   And in that case, they will probably have encountered this comment :-)
    return load_solution_from_module(m)


def load_solution_from_module(m : types.ModuleType) -> "Solution":
    """Create a solution from a module.  Use this variation if you are using or developing custom solutions outside this code directory."""
    # Simple: just use the constants provided...
    return m.SOLUTION_TYPE(m.SCENARIO_TYPE, m.PARAMS_TYPE, module_directory(m))


def solution_info(solution_name) -> dict:
    """Return a dictionary of basic information about the named solution."""
    p = SOLUTIONS_DIR / solution_name
    return raw_solution_info(p)


def all_solutions() -> List[str]:
    """Return a list of all solutions included in SOLUTIONS_DIR"""
    # Find all the subdirectories that contain an info file
    # The extra check for the info file avoids this issue: if you switch branches in git from a branch
    # that has a solution to one that does not, you end up with an empty directory.
    # It also makes it easy to "disable" a solution by renaming the info file.
    return [ d.name for d in SOLUTIONS_DIR.glob('*') if solution_info_file(d).exists() ]


def solution_directory() -> Dict[str,str]:
    """Return a dictionary of solution identifiers and titles"""
    result = {}
    for soln in all_solutions():
        info = solution_info(soln)
        result[soln] = info.get('title')
    return result


def list_solutions_matching(phrase: str) -> Dict[str,str]:
    pass




class Solution:
    """Solution is the abstract base class shared by all Solutions.
    You do not create Solution objects directly; instead use functions such as `@load_solution`"""

    _soln_dir : Path = None
    _scenario_class : type = None
    _params_class : type = None

    identifier : str = None
    """Identifier (module name) for this Solution"""
    
    title : str = None
    """English-language title of this Solution"""

    info: str = None
    """Additional information about this Solution"""

    pds_scenarios : Dict[str, str] = None
    """A list of scenarios that are included with this Solution"""

    implementation_units : str = None
    """The Implementation Units for this Solution.  Implementation units are the things that
    are built or deployed, which provide the functionality of the solution.  Example:
    km of bike paths."""

    functional_units : str = None
    """The Functional Units for this Solution.  Functional units are the units of value that
    the solution provides.  Example: km person-transport."""
    
    reference_params : ScenarioParams = None
    """The reference parameter values that define the "normal case" for this Solution."""

    
    # These are loaded on demand only.
    _adoption_data : Any = None
    _pmas : Any = None
    _scenario_descriptions : Dict[str,str] = None

    
    def __init__(self, path: Path, scenario_class=Scenario, parameter_class=ScenarioParams):
        self._soln_dir = path
        self._scenario_class = scenario_class
        self._params_class = parameter_class
        self.identifier = path.stem
        
        info = raw_solution_info(path)      
        self.title = info['title']
        self.info = info.get('info');                           # optional field
        self.pds_scenarios = info.get('pds_scenarios', dict())  # optional field
        self.implementation_units = info['implementation_units']
        self.functional_units = info['functional_units']

        params = raw_reference_params(path)
        self.reference_params = parameter_class(params)
        
    def load_scenario(self, scenario_def : Union[ str , ScenarioParams ]) -> Scenario:
        """Create a Scenario object from the `scenario_def` parameter, which must
        either be the name or path of a scenario, or a suitable scenario parameter object."""
        # Create the Scenario Parameters object
        if not isinstance(scenario_def, ScenarioParams):
            path = self.resolve_scenario_name(scenario_def)
            scenario_def = self._params_class(load_raw(path))
        # Create the Scenario object.  Scenario init does the rest of the work.
        return self._scenario_class(self, scenario_def)
    
    def resolve_scenario_name(self, scenario_name: str) -> Path:
        """`scenario_name` might be one of these categories:
        1. "PDS1", "PDS2" or "PDS3": the scenario of that type for this Solution
        2. The name of a scenario file in the scenarios directory (with or without the file suffix)
        3. An absolute path (or Path) to an existing scenario file
        Convert any of these to a Path object, or throw an exception if none of those work."""

        if scenario_name in self.pds_scenarios:
            scenario_name = self.pds_scenarios[scenario_name]
        path = Path(scenario_name)
        if not path.is_absolute():
            path = scenario_file(self._soln_dir, scenario_name)
        if not path.exists():
            raise FileExistsError(f"Unable to find a scenario file for scenario {scenario_name} (path={path})")
        return path
    
    def list_scenarios(self) -> Dict[str,str]:
        """Return a list of scenario names mapped to their descriptions, for this solution"""
        pass

    @property
    def adoption_data(self):
        pass

    @property
    def pmas(self):
        pass


class RRSSolution(Solution):
    pass