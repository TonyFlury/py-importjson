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
import changelog

__version__ = version.__version__
__changes__ = changelog.__change_log__

__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '11 Oct 2015'

__configuration__ = {"JSONSuffixes": [".json"]}
__obsolete__ = {"AllDictionariesAsClasses":
                    "No longer required - the different forms of json are automatically recognised"}


def configure(key, value):
    if key in __obsolete__:
        raise ValueError("Obsolete Configuration : {} : {}".format(key, __obsolete__[key]))

    if key not in __configuration__:
        raise ValueError("Unknown Configuration Item : {}".format(key))
    else:
        __configuration__[key] = value


def get_configure(key, default=None):
    if key not in __configuration__:
        raise ValueError("Unknown Configuration Item {}".format(key))

    return __configuration__.get(key, default)


class JSONLoader(object):
    """Finder object to identify json files, and pass them to a loader object"""
    #    _valid_suffix_ = [".json"]

    _found_modules = {}

    @staticmethod
    def _getjsonpaths(fullname, path):
        """Generator for all possible json file names for this module

           Implemented as a generator to allow for multiple suffixes in future.
        """
        # Bugfix #1 - sys.path not being searched
        path = path if path else sys.path

        # Extract the module name component only from the fully qualified module name
        mod_name = fullname.split(".")[-1]

        for p in path:
            for suff in get_configure("JSONSuffixes", default=[".json"]):
                yield os.path.join(p, mod_name) + suff

    def find_module(self, fullname, path=None):
        """Identify if the module is potentially a json file
           :param fullname : the dotted module name of module being imported
           :param path : The path of the parent module
           :return None if the module isn't a json file, or a JSONLoader instance if it is
        """
        # Is this module a json file (i.e is there a json file which exists of the same name)
        for json_path in self._getjsonpaths(fullname, path):
            if os.path.exists(json_path):
                JSONLoader._found_modules[fullname] = json_path
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
    def _methods(self, cls_dict, mod_name, cls_name, cls_list):
        """Create all the instance methods (__init__ and properties)"""
        mc = ""
        ignore = ["__doc__", "__class_attributes__", "__constraints__"]

        # Essentially unreachable - this argument can never be anything other than a dictionary
        # See how it is invoked from _create_class
        if not isinstance(cls_dict, dict):
            raise ImportError("Unable to Import : Expecting dictionary for instance attributes for {} class".format(
                cls_name))

        # Build the __init__ argument list - make sure we don't have mutable arguments
        al = [
            "{}={}".format(var, repr(value) if not isinstance(value, (list, dict)) else "None")
            for var, value in cls_dict.iteritems() if var not in ignore]

        if not al:
            # mc += "    pass"
            return mc

        mc += "\n    def __init__(self, {arg_list}, *args, **kwargs):\n".format(arg_list=",".join(al))
        mc += "        self._constraints = {value}\n".format(
            value=self.dictrepr(cls_dict.get("__constraints__", "{}")))
        mc += "".join("        self._{attr_name} = self._constrain_{attr_name}({attr_value})\n".format(
            attr_name=key,
            attr_value=key if not isinstance(value, (list, dict)) else
            "{attr_value} if {attr_name} is None else {attr_name}".format(
                attr_value=repr(value), attr_name=key)
        )
                      for key, value in cls_dict.iteritems() if key not in ignore)

        mc += "        super({}, self).__init__(*args, **kwargs)\n".format(cls_name)

        mc += """
    def _get_constraints(self, attr_name):
        if not isinstance(self._constraints, dict):
            return None

        if attr_name not in self._constraints:
            return None

        if isinstance(self._constraints[attr_name], dict):
            return self._constraints[attr_name]
        else:
            return None

    def __constrain(self, attr_name, value):
        \"\"\"Checks the constraints for the given attribute\"\"\"

        cons = self._get_constraints(attr_name)
        if not cons:
            return value

        if cons.get("not_none", False) and value is None:
            raise ValueError("Range Error : '{{attr_name}}' cannot be None".format(
                        attr_name=attr_name ))

        if value is None:
            return value

        if "type" in cons:
            if not isinstance(value, {{"bool":(bool,int), "str":(str,basestring),
                                      "list":list,"int":int,
                                      "float":(float,int), "dict":dict,
                                      {class_list} }}[cons["type"]]):
                raise TypeError(" Type Error : Attribute '{{attr_name}}' must be of type {{type}} : {{type_name}} given".format(
                            attr_name=attr_name,
                            type = cons["type"],
                            type_name = type(value).__name__ ))

        # Don't apply min and max to dictionaries or lists
        if isinstance(value,(dict,list)):
            return value

        if "min" in cons and "max" in cons:
            if cons["min"] <= value <= cons["max"]:
                return value
            else:
                raise ValueError("Range Error : '{{attr_name}}' must be between {{min}} and {{max}}".format(
                            attr_name=attr_name,
                            min=cons["min"],
                            max=cons["max"] ))

        if "min" in cons :
            if cons["min"] <= value:
                return value
            else:
                raise ValueError("Range Error : '{{attr_name}}' must be >= {{min}}".format(
                            attr_name=attr_name,
                            min=cons["min"] ))

        if "max" in cons :
            if value <= cons["max"] :
                return value
            else:
                raise ValueError("Range Error : '{{attr_name}}' must be <= {{max}}".format(
                        attr_name=attr_name,
                        max=cons["max"] ))

        return value
    """.format(class_list=",".join(["'{0}':{0}".format(cls) for cls in cls_list])
               )

        ptemplate = """
    def _constrain_{attr_name}(self, value):
        return self.__constrain('{attr_name}', value)

    @property
    def {attr_name}(self):
        \"\"\"set/get {attr_name} attribute - allows for <{mod_name}.{cls_name}>.{attr_name} = <value>\"\"\"
        return self._{attr_name}

    @{attr_name}.setter
    def {attr_name}(self, value):
        cons = self._get_constraints(attr_name='{attr_name}' )
        if cons and cons.get("read_only",False):
            raise ValueError("Range Error : '{attr_name}' is read_only")

        try:
            nv = self._constrain_{attr_name}(value )
        except:
            raise
        else:
            self._{attr_name} = nv
"""
        mc += "".join(ptemplate.format(mod_name=mod_name, cls_name=cls_name, attr_name=var)
                      for var in cls_dict if var not in ignore)

        return mc

    def _create_class(self, cls_name, cls_dict, mod_name, cls_list):
        """ Create a class definition for the given class"""
        if not isinstance(cls_dict, dict):
            raise ImportError("Expecting dictionary for a class")

        working_copy = copy.deepcopy(cls_dict)

        cls_head = ""

        # Class definition
        cls_head += "\n\nclass {} ({}):\n".format(cls_name, working_copy.get("__parent__", "object"))
        if "__parent__" in working_copy:
            del working_copy["__parent__"]

        # Documentation string - special case item
        cls_head += '    """{}"""\n'.format(working_copy["__doc__"]) if "__doc__" in working_copy else ""
        if "__doc__" in working_copy:
            del working_copy["__doc__"]

        # Generate a pass if there is nothing left to generate
        if not working_copy:
            cls_head += "    pass\n"
            return cls_head

        cls_body = ""
        # Class attributes - special case item
        cls_body += self._class_attributes(working_copy["__class_attributes__"], mod_name, cls_name) \
            if "__class_attributes__" in working_copy else ""
        if "__class_attributes__" in working_copy:
            del working_copy["__class_attributes__"]

        # Exit function now if nothing left in this class
        if not working_copy:
            return cls_head + cls_body

        # Generate __init__ method and properties
        cls_body += self._methods(cls_dict=working_copy, mod_name=mod_name, cls_name=cls_name, cls_list=cls_list)

        cls_body += "        pass" if not cls_body else ""

        return cls_head + cls_body

    def _create_classes(self, classes_dict, mod_name, cls_list):
        """Take the __classes dictionary, and create one class per instance"""
        cc = ""
        assert isinstance(classes_dict, dict)
        for cls in classes_dict:
            cc += self._create_class(cls_name=cls, cls_dict=classes_dict[cls], mod_name=mod_name, cls_list=cls_list)
        return cc

    def is_package(self, mod_name):
        if mod_name not in self.__class__._found_modules:
            raise ImportError("Unable to import : Cannot find module")

        return False

    def get_code(self, mod_name):
        if mod_name not in JSONLoader._found_modules:
            raise ImportError("Unable to import : Cannot find module")

        return compile(self.get_source(mod_name), JSONLoader._found_modules[mod_name], "exec", dont_inherit=True)

    def get_source(self, mod_name):
        if mod_name not in JSONLoader._found_modules:
            raise ImportError("Unable to import : Cannot find module")

        try:
            with open(JSONLoader._found_modules[mod_name], "r") as fp:
                json_dict = json.load(fp, encoding="ascii", object_pairs_hook=OrderedDict)

        except IOError as e:
            raise ImportError("Unable to import : Cannot open {} : {}".format(JSONLoader._found_modules[mod_name], e))
        except ValueError as e:
            raise ImportError("Unable to import : Invalid json file {} : {}".format(
                JSONLoader._found_modules[mod_name], e))

        if not isinstance(json_dict, dict):
            raise ImportError("Unable to import : Top Level of Json file must be a dictionary")

        sys.modules[mod_name].__json__ = json_dict  # Special module level attribute - the loaded json

        mod_code = ""

        if "__doc__" in json_dict:
            mod_code += '"""{}"""\n\n'.format(json_dict["__doc__"].encode("utf-8"))
        else:
            mod_code += '"""Module {} - Created by {} v{} \n' \
                        '   Original json data : {}\n' \
                        '   Generated {} {}"""\n'.format(mod_name,
                                                         self.__class__.__name__,
                                                         __version__,
                                                         JSONLoader._found_modules[mod_name],
                                                         format(
                                                             datetime.datetime.now().strftime("%a %d %b %Y %H:%M:%S")),
                                                         time.strftime("%Z (UTC %z)")
                                                         )

        # Do we have Explicit or implicit classes
        implicit = "__classes__" not in json_dict

        if implicit:
            cls_list = [key for key in json_dict if isinstance(json_dict[key], dict)]
        else:
            cls_list = [key for key in json_dict["__classes__"] if isinstance(json_dict["__classes__"][key], dict)]

        # Scan through the dictionary - taking specials into account
        for key in json_dict:

            # Ignore the __doc__ key - as it has already been consumed
            if key == "__doc__":
                continue

            if not implicit:
                if key == "__classes__":
                    if isinstance(json_dict[key], dict):
                        mod_code += self._create_classes(classes_dict=json_dict[key], mod_name=mod_name,
                                                         cls_list=cls_list)
                    else:
                        raise ImportError("Unable to Import : classes must be defined as json dictionaries {}".format(
                            JSONLoader._found_modules[mod_name]))
                else:
                    # Everything else is treated as a module level attribute
                    mod_code += "{} = {}\n".format(key, self.dictrepr(json_dict[key]))
            else:
                if isinstance(json_dict[key], dict):
                    mod_code += self._create_class(cls_name=key, cls_dict=json_dict[key], mod_name=mod_name,
                                                   cls_list=cls_list)
                else:
                    # Everything else is treated as a module level attribute
                    mod_code += "{} = {}\n".format(key, self.dictrepr(json_dict[key]))

        return mod_code

    def dictrepr(self, value):
        if isinstance(value, (basestring, int, float)):
            return repr(value)
        if isinstance(value, dict):
            return "{" + ",".join(
                "{}:{}".format(self.dictrepr(k), self.dictrepr(v)) for k, v in value.iteritems()) + "}"
        if isinstance(value, list):
            return "[" + ",".join(self.dictrepr(v) for v in value) + "]"

    def load_module(self, fullname):
        """Load the module - using the json file already found"""

        # Not sure this could ever be true - why would this loader be invoked to reload a module which it hasn't loaded
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


sys.meta_path.append(JSONLoader())
