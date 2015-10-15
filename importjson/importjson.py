#!/usr/bin/env python
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

import sys
import os
import imp
import json
from collections import OrderedDict
import datetime
import time
import copy

import version

__version__ = version.__version__
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '11 Oct 2015'


class JSONFinder(object):
    """Finder object to identify json files, and pass them to a loader object"""
    _valid_suffix_ = [".json"]

    _found_modules = {}

    @staticmethod
    def _getjsonpaths(fullname, path):
        """Generator for all possible json file names for this module

           Implemented as a generator to allow for multiple suffixes in future.
        """
        # path is a list - not a string.
        path = path[-1] if path else os.getcwd()

        # Extract the module name component only from the fully qualified module name
        mod_name = fullname.split(".")[-1]

        for suff in JSONFinder._valid_suffix_:
            yield os.path.join(path, mod_name) + suff

    def __str__(self):
        return "<JSONFinder instance >"

    def find_module(self, fullname, path=None):
        """Identify if the module is potentially a json file
           :param fullname : the dotted module name of module being imported
           :param path : The path of the parent module
           :return None if the module isn't a json file, or a JSONLoader instance if it is
        """
        # Is this module a json file (i.e is there a json file which exists of the same name)
        for json_path in self._getjsonpaths(fullname, path):
            if os.path.exists(json_path):
                JSONFinder._found_modules[fullname] = json_path
                return self
        else:
            # Allow a different finder to try to deal with this file
            return None

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def _class_attributes(self, data_dict, mod_name, cls_name):
        """ Generate relevant code for any class attributes"""
        if not isinstance(data_dict, dict):
            raise ImportError("Invalid json : __class_attributes__ must be a dictionary for {} class".format(cls_name))

        ca = ""
        for name, value in data_dict.iteritems():
            ca += "    {} = {}\n".format(name, value)
        return ca

    # noinspection PyMethodMayBeStatic
    def _methods(self, data_dict, mod_name, cls_name):
        """Create all the instance methods (__init__ and properties)"""
        mc = ""
        ignore = ["__doc__", "__class_attributes__"]
        """Generate code for class definition"""

        if not isinstance(data_dict, dict):
            raise ImportError("Unable to Import : Expecting dictionary for instance attributes for {} class".format(
                cls_name))

        al = [
            "{}={}".format(var, repr(value) if not isinstance(value, (list, dict)) else "None")
            for var, value in data_dict.iteritems() if var not in ignore]

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
        \"\"\"set/get {name} attribute - allows for <{modname}.{clsname}>.{name} = <value>\"\"\"
        return self._{name}

    @{name}.setter
    def {name}(self, value):
        self._{name} = value
"""
        mc += "".join(ptemplate.format(modname=mod_name, clsname=cls_name, name=var)
                      for var in data_dict if var not in ignore)

        return mc

    def _create_class(self, cls_name, data_dict, mod_name):
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
        cls_def += self._class_attributes(working_copy["__class_attributes__"], mod_name, cls_name) \
            if "__class_attributes__" in working_copy else ""
        if "__class_attributes__" in working_copy:
            del working_copy["__class_attributes__"]

        # Exit function now if nothing left in this class
        if not working_copy:
            return cls_def

        # Generate __init__ method and properties
        cls_def += self._methods(working_copy, mod_name, cls_name)
        return cls_def

    def _create_classes(self, data_dict, mod_name):
        """Take the __classes dictionary, and create one class per instance"""
        cc = ""
        assert isinstance(data_dict, dict)
        for cls in data_dict:
            cc += self._create_class(cls, data_dict[cls], mod_name)
        return cc

    def is_package(self, mod_name):
        if mod_name not in self.__class__._found_modules:
            raise ImportError("Unable to import : Cannot find module")

        return False

    def get_code(self, mod_name):
        if mod_name not in JSONFinder._found_modules:
            raise ImportError("Unable to import : Cannot find module")

        return compile(self.get_source(mod_name), JSONFinder._found_modules[mod_name], "exec", dont_inherit=True)

    def get_source(self, mod_name):
        if mod_name not in JSONFinder._found_modules:
            raise ImportError("Unable to import : Cannot find module")

        try:
            with open(JSONFinder._found_modules[mod_name], "r") as fp:
                json_dict = json.load(fp, encoding="ascii", object_pairs_hook=OrderedDict)
        except IOError as e:
            raise ImportError("Unable to import : Cannot open {} : {}".format(JSONFinder._found_modules[mod_name], e))
        except ValueError as e:
            raise ImportError("Unable to import : Invalid json file {} : {}".format(
                JSONFinder._found_modules[mod_name], e))

        if not isinstance(json_dict, dict):
            raise ImportError("Unable to import : Top Level of Json file must be a dictionary")

        sys.modules[mod_name].__json__ = json_dict  # Special module level attribute - the loaded json

        mod_code = ""

        if "__doc__" in json_dict:
            mod_code += '"""{}"""'.format(json_dict["__doc__"].encode("utf-8"))
        else:
            mod_code += '"""Module {} - Created by {} \n' \
                        '   Original json data : {}\n' \
                        '   Generated {} {}"""\n'.format(mod_name,
                                                         self.__class__.__name__,
                                                         JSONFinder._found_modules[mod_name],
                                                         format(
                                                             datetime.datetime.now().strftime("%a %d %b %Y %H:%M:%S")),
                                                         time.strftime("%Z (UTC %z)")
                                                         )

        # Scan through the dictionary - taking specials into account
        for key in json_dict:
            if key == "__classes__":
                if isinstance(json_dict[key], dict):
                    mod_code += self._create_classes(json_dict[key], mod_name)
                else:
                    raise ImportError("Unable to Import : classes must be defined as json dictionaries {}".format(
                        JSONFinder._found_modules[mod_name]))
            else:
                # Ignore the __doc__ key - as it has already been consumed
                if key == "__doc__":
                    continue

                # Everything else is treated module level attribute
                mod_code += "{} = {}\n".format(key, repr(json_dict[key]))

        return mod_code

    # noinspection PyUnusedLocal
    def load_module(self, fullname):
        """Load the module - using the json file already found"""

        if fullname not in JSONFinder._found_modules:
            raise ImportError("Unable to import : Cannot find module")

        if fullname in sys.modules:
            mod = sys.modules[fullname]
            mod.__name__ = fullname
        else:
            mod = imp.new_module(fullname)

        mod.__file__ = JSONFinder._found_modules[fullname]
        mod.__loader__ = self
        mod.__package__ = None
        sys.modules[fullname] = mod

        # noinspection PyUnusedLocal
        try:
            mod_code = self.get_source(mod.__name__)

            exec mod_code in mod.__dict__  # Compile the code into the modules

        except BaseException as e:
            del sys.modules[fullname]
            import traceback
            raise ImportError("Error Importing {} : {}".format(fullname, traceback.format_exc()))

        return mod


sys.meta_path.append(JSONFinder())
