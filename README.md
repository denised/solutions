
This is a fork of https://github.com/ProjectDrawdown/solutions.  See that README for an intro to the project.

The original code for PD solutions is a fairly literal translation from a massive set of Excel workbooks and macros.
The translation focused on making the resulting code familiar to researchers who had worked with the Excel, and also on
making sure the results were exactly the same as the Excel results, even in some cases reproducing buggy behavior.

This fork will be a rewrite taking a different design perspective.  The goals will be:

* Focus on making the code understandable to a broad audience.  A person with reasonable programming skills should be able to understand how Project Drawdown produced the data that they use in their books and reports.
* Orient the design around Python (object-oriented, inheritance) rather than Excel.
* Clean up algorithm design and implementation where it is clear how to do that.
* Try to plan for further extension of the code.

I will _not_ guarantee either backwards compatibility with the existing code, or with the Excel results.
I also do not expect to implement all existing features, either; I will prioritize a solid foundation over completeness.

There are some more specific design goals as well, based on known pain points with the current implementation (these won't make sense
unless you are very familiar with the original code):

* Rename things according to their semantics rather than their Excel names (no more HelperTables!)
* Make it possible to load all required scenario data from anywhere (not bound to the code repository or even the file system)
* Unify Neil's Ocean solutions code with the prior existing (Denton/my) code.
* Simplify the way(s) in which adoption is specified, separating the tools for generating adoption curves from the model's use of them.
* Separate out the "reference scenario" as an explicit thing that is modeled. 


## Contributing, maybe?

As the contact person for the official project, I receive inquiries from time to time from people who would like to help.
Unfortunately it isn't clear how to take advantage of those generous offers, because the goals for that code going forward are not clear,
and the learning time to be able to do any work in the codebase is substantial (like _really_ substantial).
In this fork, I think I have to do most of the work to begin with, but may be able to accept help once a bunch of the groundwork is laid.

Who I would most like to hear from are those that would like to _use_ the code: **use cases** and **requests**, even ones significantly different 
from the original project, would be extremely interesting.
