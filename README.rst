=======================================================
importjson : Import json data into a python application
=======================================================

It is sometimes useful to be able to use json data to initialise classes and other data structures, giving your application a portable and human readable configuration capability. To do this you will probably write some level of functionality around the json standard library, and use the resulting data loaded from the json file, to populate classes and instances implemented in your application. This separates your data and functionality, which can often present challenges later down the line as you need to keep the data and functionality in step.

It would be better in many cases to be able to combine the data and functionality in a single place, and with the importjson library you can do that. The library allows you to import a json file direct into your python application.
The library uses the json data to construct a set of classes, complete with class attributes, and instance data attributes (implemented with set and get descriptors). These classes are presented as a fully formed python module - just as if you had written the code yourself.

Example
-------
The json file called classes.json exists in your applications current directory

.. code-block:: json

    {
        "__version__":"0.1",
        "__author__":"Tony",
        "__classes__" : {
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

Even with the json standard library only, it might take 10 lines or so to bring that json data into your application,
and to populate instances of your classes.

With the `importjson` library you can import this json directly into your application, and create the classes with 2
lines as demonstrated here in the console

.. code-block:: python

    >>> import importjson # Importjson library - must be imported before any json files
    >>> import classes          # Will import classes.json

The contents of the ''classes.json'' file have now been translated into module attributes and classes, which can be used just as any other module or class. All the values defined in the json file have been translated into module attributes, classes, class attributes, or data attributes as appropriate (see Details section below for the expected json structure):

.. code-block:: python

    >>> # Module attributes
    >>> classes.__author__, classes.__version__
    u'Tony', u'0.1'

As per the json implementation in the python standard library, all strings are treated as unicode.

**Warning** Because of the way that python implements imports - having classes.json and classes.py in the same directory or package the classes.json will be imported and the classes.py file will be effectively hidden, and cannot be imported.

By default the module has a auto generated documentation string

.. code-block:: python

    >>> print classes.__doc__
    Module classes - Created by JSONLoader
       Original json data : /home/tony/Development/python/importjson/src/classes.json
       Generated Mon 12 Oct 2015 22:30:54 BST (UTC +0100)

The ``__classes__`` dictionary in the json file has been converted to one or more classes (in this example the 'point' class) - see the Details section part 3 & 4 for particulars

.. code-block:: python

    >>> dir(classes)
    ['__builtins__', '__doc__', '__file__', '__json__', '__loader__', '__name__', '__package__', '__version__', '__author__','point']

The classes which are created have all the properties you might expect - for instance as defined by the ``__doc__`` and the ``__class__attributes__`` dictionary in  the json file we can define class data attributes - see Details section 5

**Note** : Special module variables :
    From the ``dir`` listing above you will see a number of special module variables :
    - ``__builtins__`` : as per all modules this is the standard python builtins modules
    - ``__doc__`` : as demonstrated above this is the module documentation string (either the auto generated or defined in the json file.
    - ``__file__`` : this is the full path to the json file
    - ``__json__`` : the original json file imported as a dictionary. It is included for interest only, it should not ever be necessary to use the data in this dictionary (as it has all been converted to the specific module data attributes, classes and other content.
    - ``__loader__`` : This is the custom loader object (which the importjson library implements).
    - ``__name__`` : As with all other modules - this is the fully qualified module name.
    - ``__package__`` : This is False, as the json file cannot ever define a package

The ``__version__`` and ``__author__`` variables are not special variables - as they are defined by the json file.

.. code-block:: python

    >>> classes.point._val1
    1
    >>> classes.point._val2
    2
    >>> classes.point.__doc__
    'Example class built from json'

Instances which are created from these classes have the expected Instance data attributes with default values derived from the relevant entries in the json. Instance Data Attributes can be retrieved by name (as expected).

.. code-block:: python

    >>> inst = classes.point()
    >>> inst.x, inst.y, inst.colour
    0, 0, [0, 0, 0]

The class is generated with a initializer (``__init__`` method) which accepts arguments so the default can be overridden. These arguments are in the same order as the json file.

.. code-block:: python

    >>> insta = classes.point(0, 1)
    >>> insta.x, insta.y, insta.colour
    0, 1, [0, 0, 0]

Arguments to the initializer can be keyword arguments too - using the same names in the json file.

.. code-block:: python

    >>> instb = classes.point(colour=[1,1,1])
    >>> instb.x, instb.y, instb.colour
    0, 0, [1, 1, 1]

Instance Data attributes can be changed using the normal dot syntax :

.. code-block:: python

    >>> insta.x = 23
    >>> insta.x, insta.y, insta.colour
    23, 0, [0,0,0]

Details
=======

The json file must be in a specific format :

1 JSON file Top Level
---------------------
The Top level of the json file **must** be a directory.

2 Top Level content
-------------------
**All** key, value pairs in the top level are created as module level attributes (see example of ``__version__`` above) with the following notes and exceptions:
 - An optional key of ``__doc__`` is found then the value is used as the module documentation string instead of an automatically generated string (example as above ``classes.__doc__`` example). While it is normal that the value is a string if a different object is provided the documentation string will be set to the string representation of that object
 - An optional key of ``__classes__`` has the value of a dictionary - this dictionary is interpreted as the definition of the classes in this module - see section 3.

3 Content of ``__classes__`` dictionary
---------------------------------------
Within the ``__classes__`` dictionary in the json file, each key,value is a separate class to be created. the key is the class name, and the value must be a dictionary (called the class defining dictionary) - see section 4

4 Content of a class defining dictionary
----------------------------------------
Within the class defining dictionary, each key,value pair is used as instance attributes; the value in the json file is used as the default value for that attribute, and is set as such in the initializer method for the class. This is true for all key,value pairs with the following notes and exceptions:
 - An optional key of ``__doc__`` will set the documentation string for the class - unlike at module level there is no automatically generated documentation string for the class. While it is normal that the value is a string if a different object is provided the documentation string will be set to the string representation of that object
 - An optional key of ``__class_attributes__`` will have the value which is a dictionary : This dictionary defines the names and values of the class data attributes (as opposed to the instance data attributes) - see section 5
 - An optional key if ``__parent__`` will have a string value which is used as the name of a superclass for this class

5 Content of the ``__class_attributes__`` dictionary
----------------------------------------------------
Within the ``__class_attributes__`` dictionary each key, value pair defines the name and value of a class data attribute. There are no exceptions to this rule at this time.

Notes and Comments
==================
1. Instance data attributes are actually created with the name prefixed by a ``_``, thus marking the attribute as private. A read/write descriptor is then created with the name as given in the json file.
2. If the json defines Instance data attribute with a default value which is a mutable type (list or dictionary), the initializer ensures that changes to the instance are not propagated to other instances. See [Common Python Gotchas](http://docs.python-guide.org/en/latest/writing/gotchas/) for a description of this issue. There are no plans to allow this protection to be turned off.
3. All strings are imported as Unicode - as can be seen from the ``__version__`` example above.
4. The module works by creating a python code block which is then compiled into the module and made available to the application. That code block is available for information : <module>.__loader__.get_source(<module_name) - this is NOT the json file. The json file is available through the ``__file__`` module attribute, and the imported dictionary can be seen by inspecting ``__json__`` module attribute. Under normal circumstance it should not be necessary to use either the json dictionary or the generated code.

Shortcomings
============
1. It is not possible to use json to define tuples, sets or other complex python data types. json only supports strings, lists, numbers and dictionaries. This is not a limitation of the importjson library, and cannot be fixed easily.
2. All instance data attributes are read/write, read_only is not possible in this implementation - see Futures
3. It is not possible to set a documentation string for any of the instance data attributes - see Futures
4. The current implementation does not pass data down the inheritance tree - BUG

Future
======
Possible future enhancements :
 - Read only instance data attributes
 - Criteria (min, max, allowed values) for attributes.
 - Auto generation of factory methods, using a specific attribute as the key
 - Auto generation of human friendly ``__str__`` and ``__repr__`` functions
 - Documentation strings for the Instance Data Attributes