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
    Point(x=10, y=-10, colour=[1,0,0])
    >>> str(p)
    Point(x=10, y=-10, colour=[1,0,0])

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


.. _valid python format string: https://docs.python.org/3.6/library/string.html?highlight=format_string#format-string-syntax