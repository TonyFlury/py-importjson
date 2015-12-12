Details
=======

.. _module-configuration:

1. Module Configuration
------------------------

The importjson module supports one configuration options, set using `importjson.configure(<config_item>,<value>)`. The config_items supported are :

- ``JSONSuffixes`` : A list of valid JSON file name suffixes which are used when searching for potential JSON files to import. The default is [".json"]. Setting this value incorrectly will prevent the library from finding or importing any JSON files - so take care.

A previous configuration item ``AllDictionariesAsClasses`` has been rendered obsolete due to changes in `0.0.1a5` and a exception is raised if this item is attempted to be used.

.. _json-structure:

2. JSON file structure
----------------------

The json file must be in a specific format :

The Top level of the json file **must** be a dictionary - ie it must start with ``{`` and end with ``}`` - see :ref:`json_top_level_content` for details.


.. _json_top_level_content:

3. Top Level content
--------------------

**All** name, value pairs in the top level are created as module level attributes (see example of ``__version__`` above) with the following notes and exceptions:

 - An optional name of ``__doc__`` is found then the value is used as the module documentation string instead of an automatically generated string. While it is normal that the value is a string if a different object is provided the documentation string will be set to the string representation of that object.
 - Within the top level dictionary, a name of ``__classes__`` is optional :
 - If an json object with the name of ``__classes__`` does **not** exist: all dictionaries under the Top Level areas are used to define the classes in this module - see  see :ref:`class-defining-dictionary`. Although this form of JSON is more 'natural', in this case it is not possible to define a Module Data Attribute with a dictionary value.
 - If an json object with the name of ``__classes__`` does exist: the content of this dictionary are used as the definitions of the classes in this module - see :ref:`classes-dictionary`. In this case any other dictionary under the Top Level JSON is treated as a Module Data Attributes whose initial value is a dictionary.

.. _classes-dictionary:

4. Content of ``__classes__`` dictionary
--------------------------------------------

When the ``__classes__`` dictionary exists in the json file, each key,value within that dictionary is a separate class to be created. The key is the class name, and the value must be a dictionary (called the class defining dictionary) - see section 4. An example of this form of JSON file is used above.

.. _class-defining-dictionary:

5. Content of a class defining dictionary
-----------------------------------------

Within the class defining dictionary, each key,value pair is used as instance attributes; the value in the json file is used as the default value for that attribute, and is set as such in the initializer method for the class. This is true for all key,value pairs with the following notes and exceptions:

 - An optional key of ``__doc__`` will set the documentation string for the class - unlike at module level there is no automatically generated documentation string for the class. While it is normal that the value is a string if a different object is provided the documentation string will be set to the string representation of that object
 - An optional key of ``__class_attributes__`` will have the value which is a dictionary : This dictionary defines the names and values of the class data attributes (as opposed to the instance data attributes) - see :ref:`class-attributes`
 - An optional key of ``__parent__`` will have a string value which is used as the name of a superclass for this class.
 - An optional key ``__constraints__`` which will have a dictionary value - and define constraint to be applied to the value of individual Instance Data Attributes - see :ref:`constraints`

.. _class-attributes:

6. Content of the ``__class_attributes__`` dictionary
---------------------------------------------------------

Within the ``__class_attributes__`` dictionary each key, value pair defines the name and value of a class data attribute. There are no exceptions to this rule.

.. _constraints:

7. Content of the ``__constraints__`` dictionary
----------------------------------------------------

Within the ``__constraints__`` dictionary each key is the the name Instance Data attribute, as defined within the class defining dictionary. It is not neccessary for every Instance Data Attribute to be represented by a key in the ``__constraints__`` dictionary.

Each key has the value of a dictionary, and this dictionary has zero or more keys within it (every key being optional) :

- `type` : Can be used to constrain the type of value allowed for the attribute

  - `list` : constrains the type to be a list (the values of the items are not restricted)
  - `str` : constrains the type to be a string or basestring
  - `int`  : constrains the type to be a integer or boolean
  - `float`  : constrains the type to be a float or integer
  - `dict`  : constrains the type to be a dictionary (keys and values are not restricted)
  - `bool` : constrains the type to be boolean (i.e. True or False Only)
  - Any other value must be the name of a class defined in the JSON file.
- `min` : Constrain the minimum value allowed for the attribute - applied to strings and numeric values only
- `max` : Constrain the maximum value allowed for the attribute - applied to strings and numeric values only
- `not_none` : determines if the value is allowed to be a None value
- `read_only` : determine if the value can be changed after the instance is created

If an attempt is made to set an attribute to a value outside the range defined by `min` and `max` the ``ValueError`` exception will be raised. This include setting the value within the Instance initializer.

If an attempt is made to set an attribute to a value which does not match the type criteria, then a ``TypeError`` exception will be raised. This includes setting the value within the Instance initializer.

If an attempt is made to set an attribute to None when `not_none` is set to True, a ``ValueError`` exception will be raised. This value defaults to false - i.e. None values are allowed.

- If an attempt is made to set an attribute when `read_only` is set to True, a ``ValueError`` exception will be raised. This does not include setting the attribute in the initialiser/constructor. This value defaults to False, i.e. attributes can be changed at any time.

All criteria are optional - an empty or missing constraints section for a given attribute has no effect.

.. warning::

  Since the constraints are applied every time the value is set, including the initializer, you must ensure that the default value given for the data attribute is valid based on any constraints defined for that attribute. If the default value is invalid, then the JSON will import successfully, but class instances will not be able to be created with it's default values.
  The values in the constraints section are not cross checked currently at the time of import, and any errors (such as incorrect numeric ranges or invalid types) will only be detectable when instances are created. It is relatively simple though to change the json file and reload the module.
