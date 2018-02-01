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
import datetime
import time
import copy
from .version import __version__, __author__, __copyright__, __email__, __release__
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

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def _class_attributes(self, data_dict, mod_name, cls_name):
        """ Generate relevant code for any class attributes"""

        if not isinstance(data_dict, dict):
            raise ImportError(
                "Invalid json : __class_attributes__ must be "
                "a dictionary for {} class".format(cls_name))

        ca = ""
        for name, value in data_dict.items():
            ca += "    {} = {}\n".format(name, value)
        return ca

    # noinspection PyMethodMayBeStatic
    def _get_constraints(self, class_cons, attr_name):
        """Extract the constraints for a given attribute"""

        if class_cons is None:
            return dict()

        if not isinstance(class_cons, dict):
            return dict()

        if attr_name not in class_cons:
            return dict()

        if isinstance(class_cons[attr_name], dict):
            return class_cons[attr_name]
        else:
            return dict()


    def _get_default_repr(self, attributes):
        """Create the default repr for this class"""
        repr_fmt = '{class_name}('
        repr_fmt += ', '.join(['{name}={{{name}!r}}'.format(name=attr_name) for attr_name in attributes])
        repr_fmt += ')'
        return repr_fmt

    def _generate_str_format_method(self, mod_name, cls_name, attributes, format_str, method_name='repr'):
        """Generate the code for the __repr__ method"""
        src= """
    def __{method_name}__(self):
        \"\"\"{doc}\"\"\"
        return \'{format_str}\'.format(class_name=\'{cls_name}\', module_name=\'{mod_name}\', {attrs})
        """.format( method_name=method_name,
                    doc = 'Generate repr for instance' if method_name=='__repr__' else 'Generate str for instance',
                    format_str=format_str, mod_name=mod_name, cls_name=cls_name, attrs=', '.join(['{name}=self.{name}'.format(name=name) for name in attributes]))
        return src

    # noinspection PyMethodMayBeStatic
    def _generate_property_setter_getter(self, mod_name,
                                         cls_name,
                                         attr_name,
                                         cls_list,
                                         constraints):
        """Generate code for the property methods with constraints code"""

        if constraints is None:
            constraints = dict()

        # Generate getter method - easy peasy
        src = """
    @property
    def {attr_name}(self):
        \"\"\"get {attr_name} attribute
              allows for <{mod_name}.{cls_name}>.{attr_name} syntax\"\"\"
        return self._{attr_name}

        """.format(attr_name=attr_name, mod_name=mod_name, cls_name=cls_name)

        # Method definition of setter method
        src += """
    @{attr_name}.setter
    def {attr_name}( self, value ):
        \"\"\"set {attr_name} attribute
              allows for <{mod_name}.{cls_name}>.{attr_name} = <value> syntax
              Constraints are applied as appropriate
        \"\"\"
        """.format(attr_name=attr_name, mod_name=mod_name, cls_name=cls_name)

        if constraints.get('read_only', False):
            src += """
        # Generate Read Only exception
        raise ValueError("{cls_name}.{attr_name} is read only")
            """.format(cls_name=cls_name, attr_name=attr_name)
        else:
            src += """
        self._{attr_name} = self._constrain_{attr_name}(value)
                """.format(attr_name=attr_name, cls_name=cls_name)

        # Method definition of _constrain method
        src += """
    def _constrain_{attr_name}( self, value ):
        \"\"\"Apply Constraints to the value for the attribute\"\"\"
        """.format(attr_name=attr_name, cls_name=cls_name)

        src += """
        if hasattr(super({cls_name},self), "_constrain_{attr_name}"):
            value = super({cls_name},self)._constrain_{attr_name}(value)
        """.format(cls_name=cls_name,
                   attr_name=attr_name,
                   )

        # Check if the attribute is constrained to be not none
        if constraints.get("not_none", False):
            src += """
        # Check for none as it not allowed
        if value is None:
            raise ValueError("Range Error : '{attr_name}' cannot be None")
        """.format(attr_name=attr_name)
        else:
            src += """
        # Since value is None and None is allowed - can ignore all other checks
        if value is None:
            return None
            """.format(attr_name=attr_name)

        if "type" in constraints:
            if constraints["type"] in cls_list:
                allowed_type = constraints["type"]
            else:
                # Create the appropriate argument for type check
                allowed_type = {"bool": "(bool,int)",
                                "str": "six.string_types",
                                "list": "list",
                                "int": "int",
                                "float": "(float,int)",
                                "dict": "dict"}[constraints["type"]]
            # Create the code for the type check
            src += """
        if not isinstance(value, {allowed_type} ):
            raise TypeError(" Type Error : Attribute '{attr_name}' "
                            "must be of type {allowed_type} : {{type_name}} "
                            "given".format(
                                    type_name = type(value).__name__ ))
                """.format(attr_name=attr_name,
                           allowed_type=allowed_type)

        src += """
        # Don't apply min and max to dictionaries or lists
        if isinstance(value,(dict,list)):
            return value
        """.format(attr_name=attr_name)

        if ('min' in constraints) and ('max' in constraints):
            src += """

        # Implement min/max constraint
        if {min_val} <= value <= {max_val}:
            return value
        else:
            raise ValueError("Range Error : '{attr_name}' must be "
                             "between {min_val} and {max_val}" )
            """.format(attr_name=attr_name,
                       min_val=constraints['min'],
                       max_val=constraints['max'])

            src += """
            return value
                """

            return src

        if "min" in constraints:
            src += """
        # Implement minimum value constraint
        if {min_val} <= value:
            return value
        else:
            raise ValueError("Range Error : '{attr_name}' "
                             "must be >= {min_val}")
                """.format(attr_name=attr_name,
                           min_val=constraints["min"])

        if "max" in constraints:
            src += """
        # Implement maximum value constraint
        if {max_val} >= value:
            return value
        else:
            raise ValueError("Range Error : '{attr_name}' "
                             "must be <= {max_val}")
                """.format(attr_name=attr_name,
                           max_val=constraints["max"])

        src += """
        return value
            """

        return src

    # noinspection PyMethodMayBeStatic
    def _methods(self, cls_dict, mod_name, cls_name, cls_list):
        """Create all the instance methods (__init__ __repr__, and properties)"""
        mc = ""
        ignore = ["__doc__", "__class_attributes__", "__constraints__",'__repr__','__str__']

        # Essentially unreachable - this argument will only be a dictionary
        # See how it is invoked from _create_class
        if not isinstance(cls_dict, dict):
            raise ImportError(
                "Unable to Import : Expecting dictionary for "
                "instance attributes for {} class".format(
                    cls_name))

        attributes = OrderedDict([(name,value) for name, value in cls_dict.items() if name not in ignore])

        # Build the __init__ argument list - and detect mutable arguments
        al = [
            "{}={}".format(var, repr(def_value) if not isinstance(def_value, (
                list, dict)) else "None")
            for var, def_value in attributes.items()]

        if not al:
            # mc += "    pass"
            return mc

        # Start generating source for __init__ method
        mc += ("\n" +
               " " * 4 +
               "def __init__(self, {arg_list}, *args, "
               "**kwargs):\n".format(arg_list=",".join(al))
               )

        # Issue 8 : Super is called first to initialise parent class
        mc += """
        super({cls_name}, self).__init__(*args, **kwargs)
        """.format(cls_name=cls_name)

        # Set the initial value of the attribute with constrains applied
        for attr_name, def_value in attributes.items():

            # Identify the appropriate value if default value is mutable
            if isinstance(def_value, (list, dict)):
                mc += """
        {attr_name} = {attr_value} if {attr_name} is None else {attr_name}
                """.format(
                    attr_value=repr(def_value), attr_name=attr_name)

            mc += """
        self._{attr_name} = self._constrain_{attr_name}( {attr_name} )
            """.format(attr_name=attr_name)

        for attribute_name in attributes:

            cons = self._get_constraints(
                class_cons=cls_dict.get("__constraints__", None),
                attr_name=attribute_name)
            mc += self._generate_property_setter_getter(mod_name=mod_name,
                                                        cls_name=cls_name,
                                                        attr_name=attribute_name,
                                                        cls_list=cls_list,
                                                        constraints=cons)

        repr_str = cls_dict.get('__repr__', self._get_default_repr(attributes=attributes))

        str_str = cls_dict.get('__str__', None)


        mc += self._generate_str_format_method(mod_name=mod_name, cls_name=cls_name, attributes=attributes, format_str=repr_str)

        if str_str:
            mc += self._generate_str_format_method(mod_name=mod_name, cls_name=cls_name, attributes=attributes, format_str=str_str, method_name='str')

        return mc


    def _create_class(self, cls_name, cls_dict, mod_name, cls_list):
        """ Create a class definition for the given class"""
        if not isinstance(cls_dict, dict):
            raise ImportError("Expecting dictionary for a class")

        working_copy = copy.deepcopy(cls_dict)

        cls_head = ""

        # Class definition
        cls_head += "\n\nclass {} ({}):\n".format(cls_name, working_copy.get(
            "__parent__", "object"))
        if "__parent__" in working_copy:
            del working_copy["__parent__"]

        # Documentation string - special case item
        cls_head += '    """{}"""\n'.format(
            working_copy["__doc__"]) if "__doc__" in working_copy else ""
        if "__doc__" in working_copy:
            del working_copy["__doc__"]

        # Generate a pass if there is nothing left to generate
        if not working_copy:
            cls_head += "    pass\n"
            return cls_head

        cls_body = ""
        # Class attributes - special case item
        cls_body += self._class_attributes(
            working_copy["__class_attributes__"], mod_name, cls_name) \
            if "__class_attributes__" in working_copy else ""
        if "__class_attributes__" in working_copy:
            del working_copy["__class_attributes__"]

        # Exit function now if nothing left in this class
        if not working_copy:
            return cls_head + cls_body

        # Generate __init__ method and properties
        cls_body += self._methods(cls_dict=working_copy, mod_name=mod_name,
                                  cls_name=cls_name, cls_list=cls_list)

        cls_body += "        pass" if not cls_body else ""

        return cls_head + cls_body

    def _create_classes(self, classes_dict, mod_name, cls_list):
        """Take the __classes dictionary, and create one class per instance"""
        cc = ""
        assert isinstance(classes_dict, dict)
        for cls in classes_dict:
            cc += self._create_class(cls_name=cls, cls_dict=classes_dict[cls],
                                     mod_name=mod_name, cls_list=cls_list)
        return cc

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

        mod_code = ""

        if "__doc__" in json_dict:
            mod_code += """
\"\"\"{}\"\"\"
""".format(json_dict["__doc__"])
        else:
            mod_code += """
\"\"\"Module {name} - Created by {loader} v{vers} \n'
   Original json data : {json_file}\n'
   Generated {date} {timez}
\"\"\"
            """.format(name=mod_name,
                       loader=self.__class__.__name__,
                       vers= __version__,
                       json_file=JSONLoader._found_modules[mod_name],
                       date=format(datetime.datetime.now().strftime(
                                    "%a %d %b %Y %H:%M:%S")),
                       timez=time.strftime("%Z (UTC %z)"))

        mod_code += """
import six

        """

        # Do we have Explicit or implicit classes
        implicit = "__classes__" not in json_dict

        if implicit:
            cls_list = [key for key in json_dict if
                        isinstance(json_dict[key], dict)]
        else:
            cls_list = [key for key in json_dict["__classes__"] if
                        isinstance(json_dict["__classes__"][key], dict)]

        # Scan through the dictionary - taking specials into account
        for key in json_dict:

            # Ignore the __doc__ key - as it has already been consumed
            if key == "__doc__":
                continue

            if not implicit:
                if key == "__classes__":
                    if isinstance(json_dict[key], dict):
                        mod_code += self._create_classes(
                            classes_dict=json_dict[key], mod_name=mod_name,
                            cls_list=cls_list)
                    else:
                        raise ImportError("Unable to Import : "
                                          "classes must be defined "
                                          "as json dictionaries {}".format(
                                          JSONLoader.
                                                _found_modules[mod_name]))
                else:
                    # Everything else is treated as a module level attribute
                    mod_code += """
{} = {}
""".format(key, self.recursive_repr(json_dict[key]))
            else:
                if isinstance(json_dict[key], dict):
                    mod_code += self._create_class(cls_name=key,
                                                   cls_dict=json_dict[key],
                                                   mod_name=mod_name,
                                                   cls_list=cls_list)
                else:
                    # Everything else is treated as a module level attribute
                    mod_code += """
{} = {}
""".format(key, self.recursive_repr(json_dict[key]))

        return mod_code

    def recursive_repr(self, value):
        """Generate a recursive repr for nested and complex data items"""

        if not (isinstance(value, dict) or isinstance(value, list)):
            return repr(value)

        if isinstance(value, dict):
            return "{" + ",".join(
                "{}:{}".format(self.recursive_repr(k), self.recursive_repr(v))
                for k, v in value.items()) + "}"

        if isinstance(value, list):
            return "[" + ",".join(self.recursive_repr(v) for v in value) + "]"

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
