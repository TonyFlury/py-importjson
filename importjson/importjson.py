#!/usr/bin/env python
# coding=utf-8
"""
# importjson : Implementation of importjson

Summary :
    Module to allow importation of a json file with a class generator
Use Case :
    As a Developer I want to be able to import json files and create a class
    hierarchy so that my development is easier

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
import copy
from . import version

from .internal import Module
import traceback as tr
import six


__configuration__ = {"JSONSuffixes": [".json"]}
__obsolete__ = {"AllDictionariesAsClasses":
                "No longer required - the different forms of json "
                "are automatically recognised"}

def configure(key, value):
    """Helper function to set configuration values for the module"""
    if key in __obsolete__:
        raise ValueError(
            "Obsolete Configuration : {} : {}".format(key, __obsolete__[key]))

    if key not in __configuration__:
        raise ValueError(
            "Unknown Configuration Item : {}".format(key))
    else:
        __configuration__[key] = value


def get_configure(key, default=None):
    """Helper function to retrieve configuration values for the module"""
    if key not in __configuration__:
        raise ValueError("Unknown Configuration Item {}".format(key))

    return __configuration__.get(key, default)


class JSONLoader(object):
    """Finder object to identify json files, and process them"""

    _found_modules = {}

    @staticmethod
    def _getjsonpaths(fullname, path):
        """Generator for all possible json file names for this module

           Implemented as a generator to allow for multiple suffixes in future.
        """
        # Bug fix #1 - sys.path not being searched
        path = path if path else sys.path

        # Extract the module name component from the dotted module name
        mod_name = fullname.split(".")[-1]

        for p in path:
            for suff in get_configure("JSONSuffixes", default=[".json"]):
                yield os.path.join(p, mod_name) + suff

    def find_module(self, fullname, path=None):
        """Identify if the module is potentially a json file
           :param fullname : the dotted module name of module being imported
           :param path : The path of the parent module
           :return None : If the module isn't a json file, or a JSONLoader
                         instance if it is
        """
        # Is this module a json file (i.e is there a json file which exists
        # of the same name and with a json suffix)
        for json_path in self._getjsonpaths(fullname, path):
            if os.path.exists(json_path):
                JSONLoader._found_modules[fullname] = json_path
                return self
        else:
            # Allow a different finder to try to deal with this file
            return None

    def is_package(self, mod_name):
        """Returns False in all cases, unless the module is unknown"""
        if mod_name not in self.__class__._found_modules:
            raise ImportError("Unable to import : Cannot find module")

        return False

    def get_code(self, mod_name):
        """Returns the executable code for a given module once loaded."""
        if mod_name not in JSONLoader._found_modules:
            raise ImportError("Unable to import : Cannot find module")

        return compile(self.get_source(mod_name),
                       JSONLoader._found_modules[mod_name], "exec",
                       dont_inherit=True)

    def get_source(self, mod_name=""):
        """Generate the source code for the module"""
        if mod_name not in JSONLoader._found_modules:
            raise ImportError("Unable to import : Cannot find module")

        try:
            with open(JSONLoader._found_modules[mod_name]) as fp:
                json_dict = json.load(fp, encoding="ascii",
                                      object_pairs_hook=OrderedDict)

        except IOError as e:
            raise ImportError("Unable to import : Cannot open {} : {}".format(
                JSONLoader._found_modules[mod_name], e))
        except ValueError as e:
            raise ImportError(
                "Unable to import : Invalid json file {} : {}".format(
                    JSONLoader._found_modules[mod_name], e))

        if not isinstance(json_dict, dict):
            raise ImportError(
                "Unable to import : "
                "Top Level of Json file must be a dictionary")

        # Special module level attribute - the loaded json
        sys.modules[
            mod_name].__json__ = json_dict

        module = Module(module_naame=mod_name,
                        json_dict=json_dict,
                        loader=self)

        mod_code = module.generate()

        return mod_code


    def load_module(self, fullname):
        """Load the module - using the json file already found"""

        # Not sure this could ever be true - why would this loader be invoked
        # to reload a module which it hasn't loaded
        if fullname not in JSONLoader._found_modules:
            raise ImportError("Unable to import : Cannot find module")

        # Check whether module is already installed - and reload
        if fullname in sys.modules:
            mod = sys.modules[fullname]
            mod.__name__ = fullname
        else:
            mod = imp.new_module(fullname)

        mod.__file__ = JSONLoader._found_modules[fullname]
        mod.__loader__ = self
        mod.__package__ = ''
        sys.modules[fullname] = mod

        # noinspection PyUnusedLocal
        try:
            mod_code = self.get_source(mod.__name__)

            # noinspection PyCompatibility
            exec(mod_code, mod.__dict__)  # Compile the code into the modules

        except BaseException:
            del sys.modules[fullname]
            raise ImportError("Error Importing {}"
                              ": {}".format(fullname, tr.format_exc()))

        return mod

sys.meta_path.append(JSONLoader())
