.. image:: https://travis-ci.org/TonyFlury/py-importjson
    :target: http://travis-ci.org/TonyFlury/py-importjson

=======================================================
importjson : Import json data into a python application
=======================================================

It is sometimes useful to be able to use json data to initialise classes and other data structures, giving your application a portable and human readable configuration capability. To do this you will probably write some level of functionality around the json standard library, and use the resulting data loaded from the json file, to populate classes and instances implemented in your application. This separates your data and functionality, which can often present challenges later down the line as you need to keep the data and functionality in step. It would be better in many cases to be able to combine the data and functionality in a single place, and with the importjson library you can do that.

The library allows you to import a json file direct into your python application, and automatically build a real python module,
complete with classes, class attributes, and instance data attributes (implemented with set and get descriptors).

Your code can use these classes, attributes and methods just as if you have written the code yourself.

The importjson library also allows you to set constraints on your instance attributes, checking for the data type and simple range checks on the values your attempt to set when you create instances of the classes. You can also determine whether attributes are read only, or whether they will be allowed to be set to None (or not).

See the full documentation for examples of how to use the library and how to format the json file.

- `Full Documentation <http://py-importjson.readthedocs.org/en/latest/>`_
- `On PyPi (Python Package Index) <https://pypi.python.org/pypi/importjson>`_
- `Source code on GitHub <https://github.com/TonyFlury/py-importjson>`_

+--------------------------------------------------------------------------------+
|                            *Bugs*                                              |
+================================================================================+
| Every care is taken to try to ensure that this code comes to you bug free.     |
| If you do find an error - please report the problem on :                       |
| `GitHub <https://github.com/TonyFlury/py-importjson/issues/new>`_              |
| or                                                                             |
| by email to : `Tony Flury <mailto:anthony.flury?Subject=ImportJson%20Error>`_  |
+--------------------------------------------------------------------------------+
