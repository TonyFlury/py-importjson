# coding=utf-8
""" Change Log for importjson package """

__change_log__ = """
-------------
                                Change Log
 Version 0.1.2 (2 Feb 2018) - In progress
        Issue 21 : Expose meta-data
        
 Version 0.1.1 (1 Feb 2018) - Released
        Issue 11: Useful default repr and Customiseable repr and str

 Version 0.1.0 (22 Aug 2016) - Released
        Issue 18: Resolved Inheritance of constraints

 Version 0.0.1a9 (22 Aug 2016)
        Issue 8 : Initial values on subclass overwritten by parent class

 Version 0.0.1a8 (20 Aug 2016)
        Made compatible to Py3.5 as well.

 Version 0.0.1a7 (24 Nov 2015)
        Issue 6 : Implemented ability to constrain type of Instance Attribute
                  to be one of the classes in the module.
        Issue 4 : Implemented "read_only"
        Issue 5 : Implemented "not_none"

        Corrected Readme so that table render correctly on github & pyPI
            (github pages still an issue).
        Added more unit tests : now at 99% coverage
                                (1 line unreached - 159 total)

 Version 0.0.1a6 (13th Oct 2015)
        Corrected some errors in the Readme - no functional change

 Version 0.0.1a5 (13th Oct 2015)
        Automatically differentiate between the two forms of json file.
        Make AllDictionariesAreClasses config item obsolete.

 Version 0.0.1a4 (19th Oct 2015)
        Update README with more details of constraints.
        Fixed bugs in the import of some classes.
        Refactored generated constrains code to allow easy subclass
                                        (to add extra constrains for instance).
        Refactored some tests to remove repetition of tests case while
        still getting the same coverage.
        Added Examples directory.

 Version 0.0.1a3 (18th Oct 2015)
       Implemented configuration method & Dictionary
       Implement AllDictionaryAsClasses config items
       Implement __constraints__ section for numerics
       Implement type checking within __constraints section

 Version 0.0.1a2 (16th Oct 2015)
       Bug fix #1 - Need to search sys.path when looking for a top level module
       Bug fix #2 - Arguments are passed down to parent class correctly

 Version 0.0.1a1 (15th Oct 2015)
       Initial version.
"""
