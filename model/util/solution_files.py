"""Utilities to read data from solution files.
These are low-level routines that do basically no error checking, and do not process the results at all.
Just syntactic sugar to keep higher-level code cleaner."""

from pathlib import Path
import typing
import types
import yaml


# The structure of the solution directory

def solution_info_file(solution_path) -> Path:
    return solution_path / "solution_info.yml"

def solution_refparams_file(solution_path) -> Path:
    return solution_path / "reference_params.yml"


def solution_scenarios_dir(solution_path) -> Path:
    return solution_path / "scenarios"

def scenario_file(solution_path, scenario_id) -> Path:
    # We expect the identifier *not* to have the file suffix,
    # but we will tolerate it if it is provided.
    # We also tolerate it being a Path instead of a string.
    if not str(scenario_id).endswith(".yml"):
        scenario_id = str(scenario_id) + ".yml"
    return solution_scenarios_dir(solution_path) / scenario_id

def all_scenario_files(solution_path) -> typing.List[Path]:
    return solution_scenarios_dir(solution_path).glob('*.yml')



def solution_source_data_dir(solution_path) -> Path:
    return solution_path / "source_data"

def solution_tam_data_dir(solution_path) -> Path:
    return solution_source_data_dir(solution_path) / "tam"

def solution_adoption_data_dir(solution_path) -> Path:
    return solution_source_data_dir(solution_path) / "adoption"

def solution_pma_data_dir(solution_path) -> Path:
    return solution_source_data_dir(solution_path) / "pmas"


# Basic routines to load solution files
# Note these all return raw data, not the finished data structures!

def load_raw(p):
    d = p.read_text(encoding='utf-8')
    return yaml.safe_load(d)

def raw_solution_info(solution_path) -> dict:
    return load_raw(solution_info_file(solution_path))

def raw_reference_params(solution_path) -> dict:
    return load_raw(solution_refparams_file(solution_path))

def raw_scenario_params(solution_path, scenario_id) -> dict:
    return load_raw(scenario_file(solution_path, scenario_id))

# For the following, check that the directories exist, because they
# are not required to, and we don't want to throw an error.

def raw_tam_source_data(solution_path) -> list:
    tamdata = []
    d = solution_tam_data_dir(solution_path)
    if d.exists():
        for p in d.glob("*.yml"):
            tamdata.append(load_raw(p))
    return tamdata

def raw_adoption_source_data(solution_path) -> list:
    adoptiondata = []
    d = solution_adoption_data_dir(solution_path)
    if d.exists():
        for p in d.glob("*.yml"):
            adoptiondata.append(load_raw(p))
    return adoptiondata

def raw_pma_data(solution_path) -> list:
    pmadata = []
    d = solution_pma_data_dir(solution_path)
    if d.exists():
        for p in d.glob("*.yml"):
            pmadata.append(load_raw(p))
    return pmadata



def module_directory(m : types.ModuleType) -> Path:
    """Return the directory in which the module is defined.  (Only works for modules defined in the file system.)"""
    return Path(m.__path__._path[0])