"""Module new_point - Created by JSONLoader v0.0.1a3 
   Original json data : new_point.json
   Generated Mon 19 Oct 2015 09:53:47 BST (UTC +0100)"""
__version__ = u'0.1'


class point (object):
    """Point class - 2D"""

    def __init__(self, x=0,y=0,colour=None, *args, **kwargs):
        self._constraints = {u'x':{u'type':u'int',u'min':-100,u'max':100},u'y':{u'type':u'int',u'min':-100,u'max':100}}
        self._x = self._constrain_x(x)
        self._y = self._constrain_y(y)
        self._colour = self._constrain_colour([0, 0, 0] if colour is None else colour)
        super(point, self).__init__(*args, **kwargs)

    def __constrain(self, attr_name, value):
        """Checks the constraints for this attribute"""
        if not isinstance(self._constraints, dict):
            return value

        if attr_name not in self._constraints:
            return value

        cons = self._constraints[attr_name]
        if not isinstance(cons, dict):
            return value

        if "type" in cons:
            if not isinstance(value, {"bool":(bool,int), "str":(str,basestring),
                                      "list":list,"int":int,
                                      "float":(float,int), "dict":dict}[cons["type"]]):
                raise TypeError(" Type Error : '{attr_name}' must be of {type} type : {val} given".format(
                        attr_name=attr_name,
                        type = cons["type"],
                        val = repr(value) ))

        # Don't apply min and max to dictionaries or lists
        if isinstance(value,(dict,list)):
            return value

        if "min" in cons and "max" in cons:
            if cons["min"] <= value <= cons["max"]:
                return value
            else:
                raise ValueError("Range Error : '{attr_name}' must be between {min} and {max}".format(
                        attr_name=attr_name,
                        min=cons["min"],
                        max=cons["max"] ))

        if "min" in cons :
            if cons["min"] <= value:
                return value
            else:
                raise ValueError("Range Error : '{attr_name}' must be >= {min}".format(
                        attr_name=attr_name,
                        min=cons["min"] ))

        if "max" in cons :
            if value <= cons["max"] :
                return value
            else:
                raise ValueError("Range Error : '{attr_name}' must be <= {max}".format(
                        attr_name=attr_name,
                        max=cons["max"] ))

        return value
    

    def _constrain_x(self, value):
        return self.__constrain('x', value)

    @property
    def x(self):
        """set/get x attribute - allows for <new_point.point>.x = <value>"""
        return self._x

    @x.setter
    def x(self, value):
        try:
            nv = self._constrain_x(value)
        except:
            raise
        else:
            self._x = nv


    def _constrain_y(self, value):
        return self.__constrain('y', value)

    @property
    def y(self):
        """set/get y attribute - allows for <new_point.point>.y = <value>"""
        return self._y

    @y.setter
    def y(self, value):
        try:
            nv = self._constrain_y(value)
        except:
            raise
        else:
            self._y = nv


    def _constrain_colour(self, value):
        return self.__constrain('colour', value)

    @property
    def colour(self):
        """set/get colour attribute - allows for <new_point.point>.colour = <value>"""
        return self._colour

    @colour.setter
    def colour(self, value):
        try:
            nv = self._constrain_colour(value)
        except:
            raise
        else:
            self._colour = nv
