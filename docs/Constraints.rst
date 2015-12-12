Constraints
===========

It is possible to define constraint criteria for the Instance Data Attributes, by using a ``__constraints__`` sub
dictionary within the class definition - as an example :

.. code-block:: json

    {
        "point": {
            "x": 0,
            "y": 0,
            "__constraints__": {
                "x":{
                    "type":"int",
                    "min":-100,
                    "max":100
                    }
                }
        }
    }

This would implement a definition of the ``x`` attribute on instances of the ``point`` class could only ever be set to
an integer (or boolean), and must between -100 and 100 inclusive. The allowed criteria are ``type``, ``min``, ``max``, ``read_only`` and ``not_none``.
The``type`` can be any one of ``list``, ``str``, ``int``, ``float``, ``dict`` or ``bool`` or the name of a class which is also defined in the JSOn file.

 - A ``type`` of ``float`` will allow both floats and integer values
 - A ``type`` of ``int`` will allow both integers and booleans values
 - A ``type`` of ``bool`` will only allow either True or False values
 - If the constraint of ``not_none`` is True, a ``ValueError`` will be raised if any attempt is made to assign a ``None`` value to the attribute which is not None. For lists and dictionaries an empty list or dict is not the same as a ``None`` value.
 - If the constraint of ``read_only`` is True, a ``ValueError`` will be raised if an attempt is made to assign the attribute (other than the assignment made during initialisation).
 - If an attempt is made to set an attribute to a value outside the range defined by ``min`` and ``max``, a ``ValueError`` exception will be raised.
 - If an attempt is made to set an attribute to a value which does not match the type criteria, then a ``TypeError`` exception will be raised.
 - All criteria are optional - but an empty or missing constraints section has no effect (and specifically ``not_none``, and ``read_only`` default to False when omitted)

.. warning::

 You must ensure that the constraints for each instance attribute are self consistent, and don't contradict the specified default value for that attribute. The constraints section is not validate at the time of import, but if the constraints are wrong, or non-consistent then there will be exceptions raised during instance initialisation or other attribute assignment.


Extending constraints
---------------------

The constraints system has been constructed to allow simple extensions. By subclassing the class, and creating a method on the subclass of ``_constrain_<attr_name>(value)`` you can add further tests to the constraints applied to the named attribute (e.g. to extend the constraints testing of the ``classes.point.x`` attribute, your code should sub class ``classes.point`` and implement a method ``_constrain_x(value)``).

.. py:method:: _constrain_<attr_name>(self, value)

   Implements constraints for the attribute <attr_name>.

   If you need to access the existing current value of the attribute you can simply use ``self.<attr_name>``.

       :param value: The attempted new value for this attribute - i.e. the value to be validated
       :return: The value if valid (there is nothing to stop the method from changing the value although that isn't recommended)
       :raises ValueError: raised if the value of the ``value`` argument is not valid for that attribute
       :raises TypeError: raised if the type of the ``value`` argument is not valid for that attribute


As shown in the example any extension should ideally call the ``<super class> _constrain`` method first, as it is that method which applies all of the constrains defined in the JSON file - including any type checks. By allowing the superclass method to execute first, you can be sure that the value returned is the expected type (assuming that the JSON file constrains the type).

Extending constraints example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As an example :

.. code-block:: json
  :caption: json_classes.json (in a top level directory)

  {
     "classa":{
        "x":0,
        "__constraints__":{
            "x":{
                "type":"int",
                "min":0,
                "max":1024
            }
        }
     }
  }

.. code-block:: python
    :caption: Extending the json_classes.classa to constrain x attribute to be even only

    >>> import importjson
    >>> import json_classes # As above
    >>>
    >>> class XMustBeEven(json_classes.classa):
    ...     def _constrain_x(self, value):
    ...             value = super(XMustBeEven,self)._constrain_x(value)
    ...
    ...             if value % 2 == 0:
    ...                 return value
    ...             else:
    ...                 raise ValueError("Value Error : x must be an even number")
    >>>
    >>> e = XMustBeEven()
    >>> e.x = 2 # will be fine - no exceptions expected
    >>> e.x = 3
    Value Error : x must be an even number

