.. _repr & str format:

repr and str format
===================

within a class definition, you can define a customised repr and str format for this class.

the default formatting is such that the repr string of an instance is a string representation of the constructor call - as an example :

With a class defined with this json fragment :

.. code-block:: json

    {
        "point": {
            "x": 0,
            "y": 0,
            "colour": [0,0,0]
             }
    }

then we can see the following result :

.. code-block:: pycon

    >>> p = Point(x=10,y=-10,colour=[1,0,0])
    >>> repr(p)
    "Point(x=10, y=-10, colour=[1,0,0])"
    >>> str(p)
    "Point(x=10, y=-10, colour=[1,0,0])"

As seen by default the str response is the same as the repr response.

Customising repr
----------------

The repr format can be customised by defining the '__repr__' key within the json file; the value for this key must be a string. This string can contain placeholders for the class and instance attributes, as well as the class name :

As an example the repr for the above class is equivalent to definiing the '__repr__' format as follows :

.. code-block:: json

    {
        "point": {
            "x": 0,
            "y": 0,
            "colour": [0,0,0],
             "__repr__":"{class_name}(x={x}, y={y}, colour={colour})"
             }
    }

note the ``{class_name}`` placeholder within the format string for the class name (in this case 'point').

As well as the placeholders, the format string can contain all of the formatting in a `valid python format string`_

Customising str
---------------

By default the str of an instance is the same as the repr - this is default behaviour for all python classes and the importjson module does not change this.

A customised str format can be provided within the json definition by using a `__str__` key within the json (in a smiliar fashion to the `__repr__` format above.


.. code-block:: json

    {
        "person": {
            "first_name": "John",
            "last_name": "Smith",
            "birth_place": "London",
             "__str__":"{first_name} {last_name} born in {birth_place}"
             }
    }

defines a class so that :

.. code-block:: pycon

    >>> p = Person(first_name='Michael', last_name='Palin', birth_place='Sheffield')
    >>> repr(p)
    "Person(first_name='Michael', last_name='Palin', birth_place='Sheffield')"
    >>> str(p)
    "Michael Palin born in Sheffield"

As you can see the repr result is the default described above, while the str result is now customised.

Format String attrributes
-------------------------
Both the repr and str formats support field names in the format strings for all of the class and instance attributes by name, as well as the ``module_name`` and ``class_name`` field names for the name of the module and class respectively.

The use of those field names includes accessing the items within attributes which are lists and dictionaries, and attributes can even be used as field fill and alignment values for other fields - as an example :

.. code-block:: json

    {
        "formatter": {
            "words": ["Monty", "Python"],
            "fill": "",
            "align": "",
            "width":"",
             "__str__":"{words[0]:{fill}{align}{width}} {words[1]}"
             }
    }

.. code-block:: pycon

    >>> p = formatter()
    >>> str(p)
    "Monty Python"
    >>> p.width=10
    >>> str(p)
    "Monty      Python"
    >>> p.align='^'
    >>> p.fill='~"'
    >>> str(p)
    '~~Monty~~~ Python'



.. _valid python format string: https://docs.python.org/3.6/library/string.html?highlight=format_string#format-string-syntax