Extra Information
=================

This section contains some information that might be useful, or which might trip you up, and also some musings about the future.

.. _notes-and-Comments:

Notes and Comments
------------------

1. Instance data attributes are actually created with the name prefixed by a **``_``**, thus marking the attribute as private. A read/write descriptor is then created with the name as given in the json file.
2. If the json defines Instance data attribute with a default value which is a mutable type (list or dictionary), the initializer ensures that changes to the instance are not propagated to other instances. See `Common Python Gotchas <http://docs.python-guide.org/en/latest/writing/gotchas/>`_ for a description of this issue. There are no plans to allow this protection to be turned off.
3. All strings are imported as Unicode - as can be seen from the **``__version__``** example above.
4. The module works by creating a python code block which is then compiled into the module and made available to the application. That code block is available for information : **``<module>.__loader__.get_source(<module_name)``** - while the json file is available through the **``__file__``** module attribute, and the imported dictionary can be seen by inspecting **``__json__``** module attribute. Under normal circumstance it should not be necessary to use either the json dictionary or the generated code.

.. _Shortcomings:

Shortcomings
------------

1. It is not possible to use json to define tuples, sets or other complex python data types. json only supports strings, lists, numbers and dictionaries. This is not a limitation of the importjson library, and cannot be fixed easily.
2. It is not possible to set a documentation string for any of the instance data attributes - see Futures
3. Keys in the **``__constraints__``** section of each class are lower case only.

.. _future:

Future
------

Possible future enhancements :

 - Auto generation of factory methods, using a specific attribute as the key
 - Auto generation of human friendly **``__str__``** and **``__repr__``** functions
 - Documentation strings for the Instance Data Attributes
 - Keys in **``__constrains__``** section should be case insensitive
 - validity of **``__constrains_``** items should be performed at import time.


Explicit Classes
----------------

*Note* : From v0.0.1a5 onwards the example JSON used at the top of this README could be changed to be as follows :

.. code-block:: json

    {
        "__version__":"0.1",
        "__author__":"Tony",
        "__classes__":{
            "point": {
                "__doc__": "Example class built from json",
                "__class_attributes__": {
                                  "_val1": 1,
                                  "_val2": 2
                                },
                "x": 0,
                "y": 0,
                "colour": [0,0,0]
            }
        }
    }

Note the existence of the "__classes__" dictionary. This form is termed as the **explicit** form. The advantage of this form is that it is possible to define Module Data Attributes which are dictionaries, something which impossible in the other form of json.