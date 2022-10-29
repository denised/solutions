from pathlib import Path
import model.solution as sol

THISDIR = Path(__file__).parent


def test_manual_import():
    """Test loading a solution from a code directory without using the 'load_*' facilities from model.solution"""
    import sample_soln1 as ats
    assert ats.PARAMS_TYPE is not None

    soln = ats.SOLUTION_TYPE(THISDIR/'sample_soln1',ats.SCENARIO_TYPE,ats.PARAMS_TYPE)
    
    assert isinstance(soln, sol.RRSSolution)
    assert soln.implementation_units == "widgets"
    assert soln.reference_params['soln_first_cost'] > 1234
