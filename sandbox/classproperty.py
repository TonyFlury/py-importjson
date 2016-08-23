#!/usr/bin/env python
"""
# importjson : Implementation of classproperty.py

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '14 Dec 2015'

import inspect

class ClassPropertyMetaClass(type):
    def __setattr__(self, key, value):
        if key in self.__dict__:
            obj = self.__dict__.get(key)
        if obj and type(obj) is ClassPropertyDescriptor:
            return obj.__set__(self, value)
        else:
            return super(ClassPropertyMetaClass, self).__setattr__(key, value)

class ClassPropertyDescriptor(object):

    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()

    def __set__(self, obj, value):
       if not self.fset:
           raise AttributeError("can't set attribute")
       if inspect.isclass(obj):
           type_ = obj
           obj = None
       else:
           type_ = type(obj)
       return self.fset.__get__(obj, type_)(value)

    def setter(self, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.fset = func
        return self

def classproperty(func):
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return ClassPropertyDescriptor(func)


class Bar(object):

    __metaclass__ = ClassPropertyMetaClass

    _x = 1
    y = 1

    @classproperty
    def x(self):
        print "fetching x"
        return Bar._x

    @x.setter
    def x(self,value):
        print "setting x before {} - after {}".format(Bar._x, value)
        Bar._x = value
        print "After setting x to value {}".format(Bar._x)

if __name__ == "__main__":
    print Bar.x, Bar.y
    Bar.x = 3
    Bar.y = 4
    assert Bar.x == 3
    assert Bar.x == 4
