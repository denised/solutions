import pytest
import pandas as pd
import dataclasses
import model.util.parameter_set as ps


@ps.ps_dataclass
class SamplePS(ps.ParameterSet):
    not_a_param : dataclasses.InitVar[str] = "nap" # InitVar can be used to have an attribute that is not a parameter.
    paramA : int = None
    paramB : pd.DataFrame = dataclasses.field(default=None, metadata={'pdtype':'regional'})
    paramC : float = 3.14
    """This param has inline docs"""


@ps.ps_dataclass
class ChildPS(SamplePS):
    paramC: int = 3  # change type and default value of existing parameter
    childParamA : str = None
    childParamB : int = 0

    def __init__(self, data):
        super().__init__(data)
        # Add some massaging/validation/whatever of the values
        self.childParamB = max(10, self.childParamB)


def test_simple_load():
    data = """
    paramA: 20
    paramB: { "World": {1990: 2, 1991: 3, 1993: 4} }
    """

    myps = SamplePS(data)
    assert myps.paramA == 20
    assert list(myps.paramB.columns) == ["World"]  # successfully loaded df
    assert myps['paramC'] == pytest.approx(3.14)   # array-style access works

    assert 'not_a_param' not in myps.parameter_names()   # not listed as a parameter
    assert myps.not_a_param == "nap"                     # ...but it is there
    with pytest.raises(AttributeError):
        x = myps['not_a_param']                          # array-style access doesn't work

    myps2 = ChildPS(data)
    assert myps2.parameter_names() == ['paramA','paramB','paramC','childParamA','childParamB']
    assert myps2.paramA == 20                       # inherited attribute
    assert myps2.paramC == 3                        # overridden attribute with new default
    assert myps2.childParamA is None                # child attribute with default value
    assert myps2.childParamB == 10                  # child attribute set by __init__


def test_metadata_load():
    data = """
    paramA: 20
    paramB:
      value: { "World": {1990: 2, 1991: 3, 1993: 4} }
      meta: "This is my metadata for the df"
    """

    myps = SamplePS(data)
    assert 'my metadata' in  myps.meta('paramB') 
    assert myps.meta('paramA') is None

    with pytest.raises(AttributeError):
        myps.meta('NoSuchParam')


def test_load_edge_cases():

    myps = SamplePS("")   # empty ps is legit; all params have default values
    assert myps.paramA is None

    myps = SamplePS("paramA: This is a string value")  # data types are not generally enforced
    assert isinstance(myps.paramA, str)

    with pytest.raises(ValueError):
        # Except for dataframes.  You get an error if it can't reconstruct the df value.
        SamplePS("paramB: 10")
    
    with pytest.warns(UserWarning):
        # It warns if you assign a parameter that doesn't exist.
        myps = SamplePS("noSuchParam: 1")
    
    # ...And the parameter does not end up in the object
    assert not hasattr(myps, 'noSuchParam')
    with pytest.raises(AttributeError):
        myps['noSuchParam']
    

def test_set_values():
    data = """
    paramA: 20
    paramB:
      value: { "World": {1990: 2, 1991: 3, 1993: 4} }
      meta: "This is my metadata for the df"
    """

    myps = ChildPS(data)

    myps.childParamA = "This is a new value"
    assert myps['childParamA'] == "This is a new value"

    myps['paramA'] = 15
    assert myps.paramA == 15

    myps.lock()

    with pytest.raises(AttributeError):
        myps['paramA'] = 0
    
    with pytest.raises(AttributeError):
        myps.childParamA = "can't set this now"
    
    with pytest.raises(AttributeError):
        myps.set_meta('childParamA', "I can't even set metadata")
    
    newps = myps.copy()
    assert newps.childParamA == "This is a new value"
    newps.childParamA = "I can set this again"
    newps.set_meta('childParamA', "I can set the metadata too")


def test_serialize_simple():
    data = """
    paramA: 20
    paramB:
      value: { "World": {1990: 2, 1991: 3, 1993: 4} }
      meta: "This is my metadata for the df"
    """

    # The expected result is this, but I don't want to hardcode
    # that into the test because there are a number of yaml variations
    # that would all be legal:
    # paramA: 20
    # paramB:
    #   meta: This is my metadata for the df
    #   value:
    #     World:
    #       1990: 2
    #       1991: 3
    #       1993: 4
    # childParamB: 10

    myps = ChildPS(data)
    out = myps.to_yaml()
    assert "my metadata" in out
    assert "childParamB" in out
    assert "childParamA" not in out
    assert "paramC" not in out
   

def test_merge():
    data1 = """
    paramA: 20
    paramB:
      value: { "World": {1990: 2, 1991: 3, 1993: 4} }
      meta: "This is my metadata for the df"
    """

    data2 = """
    paramA: 22
    childParamA: "another string"
    """

    ps1 = SamplePS(data1)
    ps2 = ChildPS(data2)

    # Merge two instances that are different classes.  Both set paramA, but otherwise they manage different parameters.

    psmerge = ps1.merged_with(ps2)
    assert isinstance(psmerge,ChildPS)
    assert psmerge.paramA == 22
    assert psmerge.paramC == 3    # this is initialized according to childPS default, b/c it was not explicitly set
    assert "my metadata" in psmerge.meta('paramB') 
    assert psmerge.childParamA == "another string"

    # let's try it the other way around:
    with pytest.warns(UserWarning):   # warnings b/c ps2 has parameters that SamplePS doesn't know about.
        psmerge = ps2.merged_with(ps1)
    assert not isinstance(psmerge, ChildPS)
    assert 'childParamA' not in psmerge.parameter_names()
    assert psmerge.paramA == 20
    assert psmerge.paramC == pytest.approx(3.14)  # this is now set by SamplePS default

    # Look at contrasting set values, one with metadata.

    ps1.paramC = -10
    ps1.set_meta('paramC',"let's make this exciting...")
    ps2.paramC = 40

    psmerge = ps1.merged_with(ps2)
    assert psmerge.paramC == 40
    assert psmerge.meta('paramC') is None

    with pytest.warns(UserWarning):
        psmerge = ps2.merged_with(ps1)
    assert psmerge.paramC == -10
    assert "exciting" in psmerge.meta('paramC')


def test_diff():
    data1 = """
    paramA: 20
    paramB: { "World": {1990: 2, 1991: 3, 1993: 4} }
    """

    # ---------------------------------------
    psdefault = SamplePS("")
    ps1 = SamplePS(data1)

    # the delta from the default ought to always be equal to self in compact form.
    psdelta = ps1.delta_from(psdefault)
    assert psdelta.to_yaml() == ps1.to_yaml()

    # ----------------------------------------
    data2 = """
    paramA: 40
    paramB: 
      value: { "World": {1990: 2, 1991: 3, 1993: 4} }
      meta: "I have metadata"
    """ 
    ps2 = SamplePS(data2)   
    psdelta = ps2.delta_from(ps1)

    # paramA is different, and we get that new value
    assert psdelta.paramA == ps2.paramA

    # The value of paramB is the same, but ps2 added metadata.
    # Since the value of paramB is the same, it will not be 'set' in the result
    # Since it is not set, it won't be in the serialized result, which means we 
    # lose the metadata in this case.
    assert psdelta.paramB.equals(ps1.paramB)
    assert 'paramB' not in psdelta._set
    assert 'metadata' not in psdelta.to_yaml()

    # --------------------------------------------
    data3 = """
    paramB: { "World": {1990: 2, 1991: 3, 1993: 4} }
    """
    ps3 = SamplePS(data3)
    psdelta = ps3.delta_from(ps1)

    # In this case, paramA is not set in ps3, but it is set in ps1.  So when you take the difference, you
    # get it explicitly set to the default value in the delta.  We can tell this by checking the internal _set
    # variable, and by observing that paramA is included in the to_yaml output of psdelta, even though it
    # wasn't in ps3.
    assert 'paramA' in psdelta._set
    serialized = psdelta.to_yaml()
    assert 'paramA' in serialized
    assert 'paramB' not in serialized

    # --------------------------------------------
    # And of course, changes inside the dataframe count too.
    # And when we are keeping a change, we keep its metadata.
    data4 = """
    paramB: 
      value: { "World": {1990: 2, 1991: 3, 1993: 4}, "EU": {1990: 1, 1991: 1, 1993: 2}}
      meta: "I thought I'd add a column"
    """
    ps4 = SamplePS(data4)
    psdelta = ps4.delta_from(ps1)
    serialized = psdelta.to_yaml()
    assert 'paramB' in serialized
    assert 'column' in serialized



