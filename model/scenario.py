from model.costs import CostsMixin
from model.parameters import ScenarioParams, LandParams, RRSParams
import model.solution

# Implementation note: they module model.solution imports this module, so we can't reference its actual class
# definitions (model.solution.Solution, etc.) until runtime.  Quotes around the type name
# are the type hint technique to resolve this circulatrity.

class Scenario(CostsMixin):
    _solution: "model.solution.Solution"
    _params : ScenarioParams

    def __init__(self, params: ScenarioParams, solution: "model.solution.Solution"):
        self._params = params
        self._params.lock()

    def params(self) -> ScenarioParams:
        return self._params


class RRSScenario(Scenario):
    _params: RRSParams

    def params(self) -> RRSParams:
        return self._params