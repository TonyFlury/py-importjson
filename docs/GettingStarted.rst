
Getting Started
===============

.. index::
   pair: json; format

Json Format
-----------
By default ``importjson`` creates the module according to some simple rules (see :doc:`Specification` for exact details on the required format for the json) :

- The json file must define a dictionary - i.e. the first and last characters must be a ``{`` and ``}`` respectively
- name values in the top-level dictionary are converted to module data attributes
- sub-dictionaries in the top-level dictionary are converted to classes - the name of the dictionary becomes the name of the class
- name value pairs in the class dictionaries are converted to instance data attributes with a few expections :

  - a name of ``__doc__`` can be used to define the documentation string for the class
  - a name of ``__parent__`` can be used to define that the class is subclassed from another class within the json file.
  - a name of ``__class_attributes__`` can be used to define class data attributes (rather than instance attributes). name/value pairs in the ``__class_attributes__`` dictionary are converted to class data attributes with the appropriate name and starting value.
  - a name of ``__constraints__`` can be used to define type, range and other constraints for the instance data attributes (See :doc:`Constraints` for details on how to specify constraints)
  - a name of ''__repr__'' can be used to define a customised repr format, and the name of ''__str__'' can be used to define a default str format - see :ref:`repr & str format` for more details.
- within a class dictionary - any name/value pairs where the value is a dictionary is defined as instance data variable with a default value of a dictionary.

You can define multiple classes per json file.

.. index::
   pair: search; path

Search Path
-----------
The ``importjson`` library will look for json files across all directories and files specified in ``sys.path``, ie. the same search path as normal
python modules. With the ``importjson`` library in use it will take any attempted import first and try to find a relevant JSON file to import, and
only if it is unable to find a JSON file of the appropriate name to import in any ``sys.path`` entry will it then hand over to the default python import to search for .py or .pyc files. This means that for instance if you have ``classes.json`` and ``classes.py`` in the same directory or package and your code either implicitly or explicitly imports ``classes``, then classes.json file will be found first and will be imported and the classes.py file will be effectively hidden, and cannot be imported. This will cause unexpected behaviour unless you are careful about your file naming.

.. index::
   pair: json; example

Example Json
------------

Using the following json file as an example to illustrate the key features of the importjson library:

Place the json file called ``classes.json`` exists in your applications current directory

.. code-block:: json

    {
        "__version__":"0.1",
        "__author__":"Tony",
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

.. index::
    pair: json; import

Importing the JSON file
^^^^^^^^^^^^^^^^^^^^^^^

Importing this json file is easy :

.. code-block:: python

    >>> import importjson # Importjson library - must be imported before any json files
    >>> import classes          # Will import classes.json

If a classes.json is found the above import will try to read the JSON and convert it following the rules described above. It it fails (due to permisssions, or malformed JSON for instance), and ``ImportError`` exception will be raised.
Assuming though that the above import works, with the JSON example above, then a python module is created, and can be used as any normal module:

.. index::
   triple: module; data; attributes

Module Data Attributes
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    >>> # Module attributes
    >>> classes.__author__, classes.__version__
    u'Tony', u'0.1'

As per the json implementation in the python standard library, all strings are treated as unicode.

By default the module has a auto generated documentation string

.. code-block:: python

    >>> print classes.__doc__
    Module classes - Created by JSONLoader
       Original json data : /home/tony/Development/python/importjson/src/classes.json
       Generated Mon 12 Oct 2015 22:30:54 BST (UTC +0100)

.. code-block:: python

    >>> dir(classes)
    ['__builtins__', '__doc__', '__file__', '__json__', '__loader__', '__name__', '__package__', '__version__', '__author__','point']

As can be seen from the ``dir`` listing above there are a number of special module variables :

 - ``__builtins__`` : as per all modules this is the standard python builtins modules
 - ``__doc__`` : as demonstrated above this is the module documentation string (either the auto generated or defined in the json file).
 - ``__file__`` : this is the full path to the json file - in a normal module this would be the path of the ``.py`` or ``.pyc`` file
 - ``__json__`` : the original json file imported as a dictionary. It is included for interest only, it should not ever be necessary to use the data in this dictionary (as it has all been converted to the specific module data attributes, classes and other content).
 - ``__loader__`` : This is the custom loader object (which the importjson library implements).
 - ``__name__`` : As with all other modules - this is the fully qualified module name.
 - ``__package__`` : This is False, as the json file cannot ever define a package

In the above output the ``__version__`` and ``__author__`` variables are not special variables - as they are defined by the json file.

.. index::
   single: classes

Classes
^^^^^^^

The ``point`` dictionary in the example json file will have been converted to the ``classes.point`` class.

The classes which are created have all the properties you might expect - for instance as defined by the ``__doc__`` and the ``__class__attributes__`` dictionary in  the json file we can define class data attributes (see :doc:`Specification` for details)


.. code-block:: python

    >>> classes.point._val1
    1
    >>> classes.point._val2
    2
    >>> classes.point.__doc__
    'Example class built from json'

.. index::
   pair: classes; instances

Creating Instances
^^^^^^^^^^^^^^^^^^
There is nothing special about these classes, instances of these classes can be created in just the same way as other classes.

Instances which are created from these classes have the expected Instance data attributes with default values derived from the relevant entries in the json. Instance Data Attributes can be retrieved by name (as expected).

.. code-block:: python

    >>> inst = classes.point()
    >>> inst.x, inst.y, inst.colour
    0, 0, [0, 0, 0]

.. index::
   pair: Instance Initialiser;  positional argument
   pair: Instance Initialiser;  keyword argument

Instance Initialiser
^^^^^^^^^^^^^^^^^^^^

The class initialiser accepts both keyword and position arguments; if positional arguments are used the arguemnts appear in the order that they are defined within the JSON file.

.. code-block:: python

    >>> insta = classes.point(0, 1)
    >>> insta.x, insta.y, insta.colour
    0, 1, [0, 0, 0]

Arguments to the initializer can be keyword arguments too - using the same names in the json file.

.. code-block:: python

    >>> instb = classes.point(colour=[1,1,1])
    >>> instb.x, instb.y, instb.colour
    0, 0, [1, 1, 1]

Instance Data attributes are implemented as data descriptors, and so attributes are accessed using the normal dot syntax :

.. code-block:: python

    >>> insta.x = 23
    >>> insta.x, insta.y, insta.colour
    23, 0, [0,0,0]


.. seealso::

  - Detailed Specification of the JSON format : :doc:`Specification`
  - Disovering what python classes and attributes have been imorted :doc:`Introspection`
  - Type and range checking of Instance Data Attributes : :doc:`Constraints`
  - Customised repr and str formatting : :ref:`repr & str format`
  - Known Issues and Gotchas : :ref:`Shortcomings`
