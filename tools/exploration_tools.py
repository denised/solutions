
    # Data structure is title => (testf, getf, regional) and 
    #    testf:  lambda to test if we should have this thingy
    #    getf: lambda to get this thingy
    #    regional:  boolean: does this thingy have a 'region' dimension?
    # the lambdas take a *scenario* as an argument, not a solution

    stuff_we_know_about = {
        "Reference TAM per region": (
            lambda s: hasattr(s, 'ua'),
            lambda s: s.ua.ref_tam_per_region, 
            True),
        None: (lambda s: False, lambda s: False, False)   # end of list marker
    }

    def available_data(self):
        """Not all solution types support all types of computed results.  This method will
        return a list of some data that this solution does have"""


    def lookup(self, property, scenario=None):
        """Lookup the value of a property for scenario, for this solution.
         scenario may be an index, a scenario name, or 'None', in which case the value is
        for all scenarios is concatenated together."""
        pass