===================
importjson examples
===================

The examples directory contains a number of json files and the auto generated python code that the importjson library will create for that json file. The created python files are included to demonstrate the functionality : when using the importjson library it is not necessary to use any other generated code, the library creates the code automatically when the json file is imported.

**Note** It is entirely likely that the generated python code does not meet PEP 08 coding standards, but that does not impact the functionality of the generated code, and that code does not need to be human readable in vast majority of cases.

Using the examples
------------------

For examples named as ``original_<name>.json`` :

>>> import importjson
>>> import ``original_<name>``

For examples named as ``new_<name>.json`` :

>>> import importjson
>>> importjson.configure("AllDictionariesAsClasses", True)
>>> import ``new_<name>``