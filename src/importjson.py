#!/usr/bin/env python
#
# importjson : Implementation for importjson
# 
#   Module to allow importation of a json file with a class generator
#

import sys
import os
import imp
import json
from collections import OrderedDict
import datetime
import time
import copy

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '11 Oct 2015'

"""
# importjson : Implementation of importjson

Summary : 
    Module to allow importation of a json file with a class generator
Use Case : 
    As a Developer I want to be able to import json files and create a class hierarchy so that my development is easier

Testable Statements :
    Can I import a json file
    Is a module created
    Can the module be correctly reloaded
    Are module level attributes supported
    Is the construction of classes supported
    Are class level attributes supported
    Are instance attributes supported
    Are instance initialisation methods created
    Are instance attribute property methods created
"""

class JSONFinder(object):
    _valid_suffix_ = [".json"]

    @staticmethod
    def _getjsonpaths(fullname, path):
        # Translates a dotted fullname into a file path
        parts = fullname.split(".")
        path = path[0] if path is not None else os.getcwd()
        for suff in JSONFinder._valid_suffix_:
            yield os.path.join(path, parts[-1]) + suff

    def __str__(self):
        return "<JSONFinder instance >"

    def find_module(self, fullname, path=None):

        # Is this module a json file (i.e is there a json file which exists of the same name)
        for json_path in self._getjsonpaths(fullname, path):
            if os.path.exists(json_path):
                return JSONLoader(fullname, json_path)
        else:
            # Allow a different finder to try to deal with this file
            return None


class JSONLoader(object):
    """Loader object, instantiated from the JSONFinder - loads the json file and creates the relevant module"""

    def __init__(self, fullname, json_path):
        """Loader object initialisation"""
        self._mod_name = fullname  # Module name
        self._jsonpath = json_path  # Path the found file
        self._mod = None
        self._dict = None

    def __str__(self):
        return "<JSONLoader instance {}>".format(self._jsonpath)

    # noinspection PyMethodMayBeStatic
    def _class_attributes(self, data_dict):
        """ Generate relevant code for any class attributes"""
        if not isinstance(data_dict, dict):
            raise ImportError("Invalid json : class_attributes must be a dictionary")

        ca = ""
        for name, value in data_dict.iteritems():
            ca += "    {} = {}\n".format(name, value)
        return ca

    def _methods(self, data_dict):
        """Create all the instance methods (__init__ and properties)"""
        mc = ""
        ignore = ["__doc__", "__class_attributes__"]
        """Generate code for class definition"""

        if not isinstance(data_dict, dict):
            raise ImportError("Expecting dictionary for instance attributes")

        al = [
            "{}={}".format(var, repr(value) if not isinstance(value, (list, dict)) else "None")
            for var, value in data_dict.iteritems() if var not in ignore ]

        if not al:
            mc += "    pass"
            return mc

        mc += "\n    def __init__(self, {}):\n".format(",".join(al))
        mc += "".join("        self._{} = {}\n".format(var,
                      var if not isinstance(default_value, (list, dict)) else
                      "{} if {} is None else {}".format(repr(default_value), var, var))
                      for var, default_value in data_dict.iteritems() if var not in ignore
                      )

        ptemplate = """
    @property
    def {name}(self):
        \"\"\"getter for {name} - allows for <{modname}>.{name} syntax\"\"\"
        return self._{name}

    @{name}.setter
    def {name}(self, value):
        \"\"\"setter for {name} - allows for <{modname}>.{name} = <value>\"\"\"
        self._{name} = value
"""
        mc += "".join(ptemplate.format(modname=self._mod_name, name=var) for var in data_dict if var not in ignore)

        return mc

    def _create_class(self, cls_name, data_dict):
        """ Create a class definition for the given class"""
        if not isinstance(data_dict, dict):
            raise ImportError("Expecting dictionary for a class")

        working_copy = copy.deepcopy(data_dict)
        cls_def = ""

        # Class definition
        cls_def += "\n\nclass {} ({}):\n".format(cls_name, working_copy.get("__parent__", "object"))
        if "__parent__" in working_copy:
            del working_copy["__parent__"]

        # Documentation string - special case item
        cls_def += '    """{}"""\n'.format(working_copy["__doc__"]) if "__doc__" in working_copy else ""
        if "docstring" in working_copy:
            del working_copy["__doc__"]

        # Generate a pass if there is nothing left to generate
        if not working_copy:
            cls_def += "    pass\n"
            return cls_def

        # Class attributes - special case item
        cls_def += self._class_attributes(working_copy["__class_attributes__"]) \
            if "__class_attributes__" in working_copy else ""
        if "__class_attributes__" in working_copy:
            del working_copy["__class_attributes__"]

        # Exit function now if nothing left in this class
        if not working_copy:
            return cls_def

        # Generate __init__ method and properties
        cls_def += self._methods(working_copy)
        return cls_def

    def _create_classes(self, data_dict):
        """Take the __classes dictionary, and create one class per instance"""
        cc = ""
        assert isinstance(data_dict, dict)
        for cls in data_dict:
            cc += self._create_class(cls, data_dict[cls])
        return cc

    def is_package(self, mod_name):
        if mod_name != self._mod_name:
            raise ImportError("Mismatching Loaders")

        return False

    def get_code(self, mod_name):
        if mod_name != self._mod_name:
            raise ImportError("Mismatching Loaders")

        return compile(self.get_source(mod_name), self._jsonpath, "exec", dont_inherit=True)

    def get_source(self, mod_name):
        if mod_name != self._mod_name:
            raise ImportError("Mismatching Loaders")

        mod_code = ""

        if "__doc__" in self._dict:
            mod_code += '"""{}"""'.format(self._dict["__doc__"].encode("utf-8"))
        else:
            mod_code += '"""Module {} - Created by {} \n' \
                    '   Original json data : {}\n' \
                    '   Generated {} {}"""\n'.format(mod_name,
                                                     self.__class__.__name__,
                                                     self._jsonpath,
                                                     format(datetime.datetime.now().strftime("%a %d %b %Y %H:%M:%S")),
                                                     time.strftime("%Z (UTC %z)")
                                                     )
        for key in self._dict:
            # Sub dictionaries are classes
            if key == "__classes__":
                if isinstance(self._dict[key], dict):
                    mod_code += self._create_classes(self._dict[key])
                else:
                    raise ImportError("Unable to Import : classes must be defined as json dictionaries")
            else:
                # Ignore the __doc__ key - as it has already been consumed
                if key == "__doc__":
                    continue

                # Everything else is treated module level attribute
                mod_code += "{} = {}\n".format(key, repr(self._dict[key]))

        return mod_code

    def load_module(self, fullname):

        if fullname in sys.modules:
            mod = sys.modules[fullname]
            mod.__name__ = fullname
        else:
            mod = imp.new_module(fullname)

        mod.__file__ = self._jsonpath
        mod.__loader__ = self
        mod.__package__ = None
        sys.modules[fullname] = mod

        try:
            self._mod = mod
            with open(self._jsonpath, "r") as fp:
                self._dict = json.load(fp, encoding="ascii", object_pairs_hook=OrderedDict)

            if not isinstance(self._dict, dict):
                raise ImportError("Unable to import : Top Level of Json file must be a dictionary")

            mod_code = self.get_source(self._mod_name)

            exec mod_code in mod.__dict__       # Compile the code into the modules
            mod.__json__ = self._dict           # Special module level attribute - the loaded json
#            mod.__source__ = mod_code

        except BaseException as e:
            del sys.modules[fullname]
            import traceback
            raise ImportError("Error Importing {} : {}".format(fullname, traceback.format_exc()))

        return mod

sys.meta_path.append(JSONFinder())
