"""The common implementation of all Parameter Sets"""
from typing import List, Dict
from model.util.values import value_eq, compact_string
from collections import OrderedDict
import pandas as pd
import dataclasses
import warnings
import yaml

# Commentary on design goals:
# The main goal for ParameterSet is to make it as simple-seeming and easy to use as
# possible for these major use cases:
# 1) serialization to and from a readable/editable form of Yaml.
# 2) inspection and modification of individual parameter or meta values by an interactive user.
# 3) inline documentation of what each parameter *is*, such that the documentation is available
#    in tools like VSCode or Jupyter
#
# There are two obvious ways to implement a collection of values like this: as a dict, or as
# attributes on a class object.  The dict approach makes it easy to implement things like
# serialization and enumeration of parameters, but very difficult to then document the
# individual entries.  Conversely, it is easy to document attributes on a class, but more
# complex to implement generic functionality like serialization and freezing across all
# parameters.  So here we've used dataclasses primarily because they give us a collection of
# fields (cf. parameter_names) that we can use to implement generic behavior, while also
# enabling the documentation benefits of a class attribute approach.
#
# Note also that it is allowed for the concrete ParameterSet classes to augment the functionality here,
# e.g. to do more value checking or more complex initialization.
#


class ParameterSet:
    """Provides values for a set of parameters that are used for Solution and Scenario calculations.
    ParameterSet is a base class that defines functionality of ParameterSets, but does not specify any particular
    set of parameters.
    
    The value of a parameter can be retrieved with: `ps.parameter_name`  or `ps['parameter_name']`.
    If unlocked, it can be set with `ps.parameter_name = <newvalue>` or `ps['parameter_name'] = <new_value>`.

    The list of all parameter names is given by `ps.parameter_names()`.
    
    Metadata about a parameter value can be retrieved with `ps.meta('parameter_name')`."""

    _locked = False
    _meta : Dict[str,str] = None
    _set : set = None
    # '_set' is used to indicate which values are actually _set_, vs. inheriting from the default for from
    # another ParameterSet.  It is used to implement merging and compact serialization

    def __init__(self, param_data=None):
        """If `param_data` is present, it is used to fill the values of the parameters and their
        metadata.  Either a Yaml string or a raw yaml structure are accepted. If the data contains
        unrecognized parameters, warnings will result."""
        
        self._meta = {}
        self._set = set()

        if param_data:
            if isinstance(param_data, str):
                param_data = yaml.safe_load(param_data)
            
            fielddata = self._field_data()            
            for k,v in param_data.items():
                if k in fielddata:
                    # Unpack the value:
                    # If metadata is present, the value will be represented by a nested dict containing both
                    # (Note if the actual value was a dict that contained keys 'meta' and 'value' we'd have a problem...)

                    if isinstance(v, dict) and ('meta' in v) and ('value' in v):
                        self._meta[k] = v['meta']
                        v = v['value']

                    # Per-parameter initialization; subclasses can customize/extend
                    v = self._initialize_value(k,v,fielddata[k].metadata)

                    self[k] = v
                    self._set.add(k)
                    
                else:
                    warnings.warn(f"{self.__class__.__name__} ignoring unknown parameter '{k}'")

    def _initialize_value(self, param_name, raw_value, metadata):
        """Hook for additional initialization of a parameter."""

        # If the value is supposed to be a dataframe, reconstitute it.
        if metadata.get('pdtype') and raw_value is not None:
            return pd.DataFrame.from_dict(raw_value)
        else:
            return raw_value


    def _to_yaml_form(self, compact=True):
        """Convert into a structure that is what we would serialize to yaml."""
        #   group metadata with values
        #   rewrite dataframes
        #   omit unnecessary entries if compact.
        the_data = {}
        for p in self.parameter_names():
            v = self[p]
            if compact and p not in self._set:
                continue
            if isinstance(v, pd.DataFrame):
                v = v.to_dict()
            m = self.meta(p)
            if m is not None:
                v = {'value': v, 'meta': m}
            the_data[p] = v
        return the_data

    def to_yaml(self, compact=True) -> str:
        """Return a yaml string serializing self.
        
        If `compact` is True (the default), only parameters that have metadata or have
        been explicitly set are included in the result.
        If `compact` is False, all parameters are emitted."""
        the_data = self._to_yaml_form(compact)
        return yaml.safe_dump(the_data, sort_keys=False)
            

    @classmethod
    def parameter_names(cls) -> List[str]:
        return [f.name for f in dataclasses.fields(cls)]
    
    @classmethod
    def _field_data(cls) -> Dict[str, dataclasses.Field]:
        """All the Field information, indexed by field name"""
        # This is a cheat: we are accessing the internals of the dataclasses implementation here, but it saves us
        # from having to copy or cache this info ourselves.  
        # Also, getattr instead of cls.__dataclass_fields__ because this class (Parameter_Set) isn't a dataclass itself,
        # and thus doesn't have the __dataclass_fields__ attribute
        return getattr(cls,'__dataclass_fields__',{})
    
    def merged_with(self, other_ps: "ParameterSet"):
        """Return a new ParameterSet with all the parameters of this ps, updated/overridden by parameter values in `other_ps`.
        The class returned is the same class as `other_ps`.  If there are incompatible parameters, warnings will be issued."""
        newps = other_ps.__class__(self._to_yaml_form())  # copy self, but to other class
        pnames = other_ps.parameter_names()
        # Only copy over values that are explicitly set; ignore those that inherit default values automatically.
        for op in other_ps._set:
            if op in pnames:
                newps[op] = other_ps[op]
                # Copy over the metadata with the value.  Side note: this will result in there being explicit "None"
                # entries in the dictionary, so it is important we rely on the value in the dictionary, not the
                # existence of keys.
                newps.set_meta(op, other_ps.meta(op))
        return newps


    def delta_from(self, base_ps: "ParameterSet"):
        """Return a new ParameterSet that only explicitly sets parameters that are different from `base_ps`.
        The inverse of @merged_with."""
        newps = self.copy()
        fielddata = self._field_data()
        for p in self.parameter_names():
            base_value = base_ps[p]
            new_value = newps[p]
            # Don't 'set' new_value if it is the same as base_value
            if value_eq(base_value, new_value):
                newps._set.discard(p)
            # But *do* 'set' new_value if it is default (and base_value isn't)
            elif value_eq(new_value, fielddata[p].default):
                newps._set.add(p)
            # Otherwise the existing 'set' values should be good.
        return newps


    def copy(self):
        """Return a new ParameterSet that is a full copy of self"""
        return self.__class__(self._to_yaml_form())

    def lock(self):
        """Lock self, which disables any further changes to parameter values."""
        setattr(self, '_locked', True)
    
    def islocked(self):
        return self._locked
    
    # disable setting any attribute values when we are locked
    def __setattr__(self, name, value):
        if self.islocked():
            raise AttributeError("Cannot set parameter of locked Parameter Set")
        else:
            # do the regular version of __setattr__
            object.__setattr__(self, name, value)
            # mark it as set, but only if it is an actual parameter
            if name in self.parameter_names():
                self._set.add(name)
    
    # enable access via ps['parameter_name']
    def __getitem__(self, key):
        if key not in self.parameter_names():
            raise AttributeError(f"No such parameter '{key}'")
        else:
            return getattr(self, key)
    
    def __setitem__(self, key, value):
        if key not in self.parameter_names():
            raise AttributeError(f"No such parameter '{key}'")
        else:
            self.__setattr__(key,value)
    
    def __str__(self, n=5):
        # Show a few values that have been set, clipping long values.
        output =  f"{self.__class__.__name__}("
        i = 0
        for k in self.parameter_names():
            if k in self._set:
                valstr = compact_string(str(self[k]))
                if len(valstr) > 45:
                    valstr = valstr[:42] + '...'
                output = output + '\n  ' + k + ': ' + valstr
                i = i+1
                if i == n:
                    return output + '\n  ...)'
        # if the for exits normally...
        return output + ')'


    def meta(self, parameter_name : str):
        """Return any metadata associated with the specific parameter `parameter_name` (or None if there isn't any)"""
        if parameter_name not in self.parameter_names():
            raise AttributeError(f"No such parameter '{parameter_name}'")
        return self._meta.get(parameter_name)
    
    def all_meta(self):
        """Return the set of all parameter metadata."""
        return self._meta.copy()

    def set_meta(self, parameter_name, newvalue):
        """Change the metadata for a parameter"""
        if self.islocked():
            raise AttributeError(f"Cannot alter value of locked Parameter Set (set_meta {parameter_name})")
        elif parameter_name not in self.parameter_names():
            raise AttributeError(f"No such parameter '{parameter_name}'")
        else:
            self._meta[parameter_name] = newvalue
            # Setting the metadata also counts as a 'set' operation
            self._set.add(parameter_name)


def ps_dataclass(the_class):
    """Syntactic sugar to simplify the dataclass decorator for ParameterSets.
    ParameterSet classes _must_ use this decorator, as the base class depends on it."""
    # We really are using only a small part of what dataclasses support, and actively don't want the rest.
    # This just makes the declaration look less frightening.
    return dataclasses.dataclass(init=False,repr=False,eq=False)(the_class)


