#!/usr/bin/env python
# coding=utf-8
"""
# importjson : Implementation of _internal.py

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""
from collections import OrderedDict as OrderedDict
import datetime
import time
import six

from . import version

__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '02 Feb 2018'

class ClassAttribute():
    def __init__(self, name, default, parent):
        self._name = name
        self._default = default
        self._parent = parent

    def generate( self, src):
        src += """
    {} = {}\n""".format(self._name, self._default)
        return src

    @property
    def name(self):
        return self._name

    @property
    def default(self):
        return self._default

class InstanceAttribute():
    def __init__(self, name, default, parent, constraints):
        self._name = name
        self._default = default
        self._parent = parent
        self._constraints = constraints
    @property
    def name(self):
        return self._name

    @property
    def default(self):
        return self._default

    def generate(self, src):
        return self._generate_property_setter_getter(src)

    def _generate_property_setter_getter(self, src):
        """Generate code for the property methods with constraints code"""
        src = self._generate_property_getter( src)
        src = self._generate_property_setter( src)
        src = self._generate_property_constraint_method( src)
        return src

    def _generate_property_getter(self, src):
        # Generate getter method - easy peasy
        src += """
    @property
    def {attr_name}(self):
        \"\"\"get {attr_name} attribute
               allows for <{mod_name}.{cls_name}>.{attr_name} syntax\"\"\"
        return self._{attr_name}

         """.format(attr_name=self._name, mod_name=self._parent.module.name,
                    cls_name=self._parent.name)
        return src

    def _generate_property_setter(self, src):
        """Generate code for the property setter with constraints code"""
        src += """
    @{attr_name}.setter
    def {attr_name}( self, value ):
        \"\"\"set {attr_name} attribute
                allows for <{mod_name}.{cls_name}>.{attr_name} = <value> syntax
                Constraints are applied as appropriate
        \"\"\"
          """.format(attr_name=self._name, mod_name=self._parent.module.name,
                     cls_name=self._parent.name)

        if self._constraints.get('read_only', False):
            src += """
        # Generate Read Only exception
        raise ValueError("{cls_name}.{attr_name} is read only")
                  """.format(cls_name=self._parent.name, attr_name=self._name)
        else:
            src += """
        self._{attr_name} = self._constrain_{attr_name}(value)
                  """.format(attr_name=self._name, cls_name=self._parent.name)
        return src

    def _generate_property_constraint_method(self, src):
        # Method definition of _constrain method
        src += """
    def _constrain_{attr_name}( self, value ):
        \"\"\"Apply Constraints to the value for the attribute\"\"\"
         """.format(attr_name=self._name, cls_name=self._parent.name)

        src = self._super_class_constraints_check(src)

        src = self._not_none_constraints_check(src)
        src = self._type_constraints_check(src)
        src = self._min_max_constraint_check(src)

        src += """
        return value
                 """
        return src

    def _type_constraints_check(self, src):
        """Generate code segment to check for type constraints"""

        if not self._constraints:
            return src

        if "type" in self._constraints:
            if self._constraints["type"] in self._parent.module.class_name_list:
                allowed_type = self._constraints["type"]
            else:
                # Create the appropriate argument for type check
                allowed_type = {"bool": "(bool,int)",
                                "str": "six.string_types",
                                "list": "list",
                                "int": "int",
                                "float": "(float,int)",
                                "dict": "dict"}[self._constraints["type"]]
            # Create the code for the type check
            src += """
        if not isinstance(value, {allowed_type} ):
            raise TypeError(" Type Error : Attribute '{attr_name}' "
                                "must be of type {allowed_type} : {{type_name}} "
                                "given".format(
                                        type_name = type(value).__name__ ))
                    """.format(attr_name=self._name,
                               allowed_type=allowed_type)
        return src

    def _super_class_constraints_check(self, src):
        """Generate code segment to check any constraints on the super class - and apply them first"""

        src += """
        if hasattr(super({cls_name},self), "_constrain_{attr_name}"):
            value = super({cls_name},self)._constrain_{attr_name}(value)
           """.format(cls_name=self._parent.name,
                      attr_name=self._name
                      )
        return src

    def _not_none_constraints_check(self, src, ):
        """Generate code segment to check for Not None constraints"""
        # Check if the attribute is constrained to be not none

        if not self._constraints:
            return src

        if self._constraints.get("not_none", False):
            src += """
        # Check for none as it not allowed
        if value is None:
            raise ValueError("Range Error : '{attr_name}' cannot be None")
            """.format(attr_name=self._name)
        else:
            src += """
        # Since value is None and None is allowed - can ignore all other checks
        if value is None:
            return None
                """.format(attr_name=self._name)
        return src

    def _min_max_constraint_check(self, src):
        """Generate code segment to check for min/max constraints"""

        if not self._constraints:
            return src

        src += """
        # Don't apply min and max to dictionaries or lists
        if isinstance(value,(dict,list)):
            return value
             """.format(attr_name=self._name)

        if ('min' in self._constraints) and ('max' in self._constraints):
            src += """
        # Implement min/max constraint
        if {min_val} <= value <= {max_val}:
            return value
        else:
            raise ValueError("Range Error : '{attr_name}' must be "
                                  "between {min_val} and {max_val}" )
                 """.format(attr_name=self._name,
                            min_val=self._constraints['min'],
                            max_val=self._constraints['max'])
            # Early return as we do both in one hit
            return src

        if "min" in self._constraints:
            src += """
        # Implement minimum value constraint
        if {min_val} <= value:
            return value
        else:
            raise ValueError("Range Error : '{attr_name}' "
                                  "must be >= {min_val}")
                     """.format(attr_name=self._name,
                                min_val=self._constraints["min"])

        if "max" in self._constraints:
            src += """
        # Implement maximum value constraint
        if {max_val} >= value:
            return value
        else:
            raise ValueError("Range Error : '{attr_name}' "
                                  "must be <= {max_val}")
                     """.format(attr_name=self._name,
                                max_val=self._constraints["max"])
        return src


class ClassInfo():
    def __init__(self, name, json_segment,parent):
        self._name = name
        self._json_segment = json_segment
        self._parent = parent
        self._base = ''
        self._attributes = []
        self._class_attributes = []

    @property
    def name(self):
        return self._name
    @property
    def base(self):
        return self._base

    @property
    def module(self):
        return self._parent

    def generate(self, src, loader):
        return src + self._create_class()

    def _create_class(self):
        """ Create a class definition for the given class"""
        if not isinstance(self._json_segment, dict):
            raise ImportError("Expecting dictionary for a class")

        cls_head = ""

        # Class definition
        cls_head += '\n\nclass {} ({}):\n'.format(self._name, self._json_segment.get(
            '__parent__', 'object'))

        self._base = self._json_segment.get('__parent__','object')

        # Documentation string - special case item
        cls_head += '    """{}"""\n'.format(
            self._json_segment["__doc__"]) if "__doc__" in self._json_segment else ""

        cls_body = ""
        # Class attributes - special case item
        cls_body = self._generate_class_attributes( cls_body,  self._json_segment["__class_attributes__"]) if "__class_attributes__" in self._json_segment else ""

        # Generate __init__ method and properties
        cls_body = self._generate_methods(cls_body)

        cls_body = self._generate_get_class_attributes_function(cls_body)
        cls_body = self._generate_get_instance_attributes_function(cls_body)

        return cls_head + cls_body

    def _generate_methods(self, src):
        """Create all the instance methods (__init__ __repr__, and properties)"""

        # Essentially unreachable - this argument will only be a dictionary
        # See how it is invoked from _create_class
        if not isinstance(self._json_segment, dict):
            raise ImportError(
                "Unable to Import : Expecting dictionary for "
                "instance attributes for {} class".format(
                    self._name))

        # Names that might be encountered which aren't attribute names.
        ignore = ['__doc__', '__parent__', '__class_attributes__', '__constraints__', '__repr__', '__str__']

        # Check if there are any attributes
        if not any(True for key in self._json_segment if key not in ignore):
            return src

        # Get the attributes in the order they were defined in a separate dictionary
        attributes = OrderedDict([(name,value) for name, value in self._json_segment.items() if name not in ignore])

        # Build the __init__ argument list - and detect mutable arguments
        al = [ "{}={}".format(var,
                        repr(def_value) if not isinstance(def_value, (list, dict)) else "None")
                        for var, def_value in attributes.items()]

        if not al:
            return src

        # Start generating source for __init__ method
        src += ("\n" +
               " " * 4 +
               "def __init__(self, {arg_list}, *args, "
               "**kwargs):\n".format(arg_list=",".join(al))
               )

        # Issue 8 : Super is called first to initialise parent class
        if self.base != 'object':
            src += """
        super({cls_name}, self).__init__(*args, **kwargs)
        """.format(cls_name=self._name)

        # Set the initial value of the attribute with constrains applied
        for attr_name, def_value in attributes.items():
            cons = self._get_constraints( attr_name=attr_name)

            ia_info = InstanceAttribute(name=attr_name, default= def_value, parent=self, constraints=cons)
            self._attributes.append(ia_info)

            # Identify the appropriate value if default value is mutable
            if isinstance(def_value, (list, dict)):
                src += """
        {attr_name} = {attr_value} if {attr_name} is None else {attr_name}
                """.format(
                    attr_value=repr(def_value), attr_name=attr_name)

            src += """
        self._{attr_name} = self._constrain_{attr_name}( {attr_name} )
            """.format(attr_name=attr_name)

        for entry in self._attributes:
            src = entry.generate(src)

        # Generate dunder repr and dunder str methods
        repr_str = self._json_segment.get('__repr__', self._get_default_repr(attributes=attributes))
        str_str = self._json_segment.get('__str__', None)

        # Always create a dunder repr method
        src = self._generate_str_format_method(src, format_str=repr_str)

        # Only create a dunder str method if it has been overriden
        if str_str:
            src = self._generate_str_format_method(src, format_str=str_str, method_name='str')

        return src

    def _get_constraints(self, attr_name):
        """Extract the constraints for a given attribute"""

        class_cons = self._json_segment.get("__constraints__", None)

        # No constraints on class at all
        if class_cons is None:
            return dict()

        # Something called constraints but it isn't a dictionary
        if not isinstance(class_cons, dict):
            return dict()

        # No constraints for this attribute
        if attr_name not in class_cons:
            return dict()

        # Constraints for this attribute isn't a dictionary
        if isinstance(class_cons[attr_name], dict):
            return class_cons[attr_name]
        else:
            return dict()

    def _get_default_repr(self, attributes):
        """Create the default repr for this class"""
        repr_fmt = '{class_name}('
        repr_fmt += ', '.join(
            ['{name}={{{name}!r}}'.format(name=attr_name) for attr_name in
             attributes])
        repr_fmt += ')'
        return repr_fmt

    def _generate_str_format_method(self, src, format_str, method_name='repr'):
        """Generate the code for the __repr__ method"""
        src += """
    def __{method_name}__(self):
         \"\"\"{doc}\"\"\"
         return \'{format_str}\'.format(class_name=\'{cls_name}\', module_name=\'{mod_name}\', {attrs})
         """.format(method_name=method_name,
                    doc='Generate repr for instance' if method_name == '__repr__' else 'Generate str for instance',
                    format_str=format_str, mod_name=self._parent.name,
                    cls_name=self._name, attrs=', '.join(
                ['{name}=self.{name}'.format(name=attr.name) for attr in
                 self._attributes]))
        return src

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def _generate_class_attributes(self, src, cls_attrs):
        """ Generate relevant code for any class attributes"""

        if not isinstance(cls_attrs, dict):
            raise ImportError(
                "Invalid json : __class_attributes__ must be "
                "a dictionary for {} class".format(self._name))

        for name, value in cls_attrs.items():
            cai = ClassAttribute(name=name, default=value, parent=self)
            src = cai.generate(src)
            self._class_attributes.append(cai)
        return src

    def _generate_get_instance_attributes_function(self, src):
        """Generate the code for the get_attributes function"""
        attrs = ', '.join(
                ["InstanceAttributeInfo(name=\'{name}\', default={default})".format(name=attr.name,
                                                                                  default=attr.default)
                 for attr in self._attributes]
        )
        src += """
    @classmethod
    def get_instance_attributes(cls_):
        \"\"\"Generator yielding information on module level attributes\"\"\"
        attrs = [{attrs}]
        for attr in attrs:
            yield attr
            """.format(attrs=attrs)
        return src

    def _generate_get_class_attributes_function(self, src):
        """Generate the code for the get_attributes function"""
        attrs = ', '.join(
            [
                "ClassAttributeInfo(name=\'{name}\', default={default})".format(
                     name=attr.name,
                     default=attr.default)
                for attr in self._class_attributes]
        )
        src += """
    @classmethod
    def get_class_attributes(cls_):
        \"\"\"Generator yielding information on module level attributes\"\"\"
        attrs = [{attrs}]
        for attr in attrs:
            yield attr
        """.format(attrs=attrs)
        return src


class ModuleAttribute():
    def __init__(self, json_segment, attr_name, parent):
        self._segment = json_segment
        self._attr_name = attr_name
        self._parent = parent

    @property
    def name(self):
        return self._attr_name

    @property
    def default(self):
        return self._segment

    def generate(self, src_code):
        return src_code + """
{} = {}
        """.format(self._attr_name, recursive_repr(self._segment))


class Module():
    def __init__(self, module_naame, json_dict, loader):
        self._module_name = module_naame
        self._json_dict = json_dict
        self._loader = loader
        self._imports = ['import six','from collections import namedtuple as namedtuple']
        self._attributes = []
        self._classes = []
        self._class_name_list = []

    @property
    def name(self):
        return self._module_name

    @property
    def class_name_list(self):
        return self._class_name_list

    def generate(self):
        """Generate the code required for the module"""
        mod_code = self._generate_module_doc_string()
        mod_code = self._generate_imports(mod_code) # Will have to move this later

        mod_code = self._generate_module_NamedTuples(mod_code)

        # Do we have Explicit or implicit classes
        implicit = "__classes__" not in self._json_dict

        if implicit:
            self._class_name_list = [key for key in self._json_dict if
                        isinstance(self._json_dict[key], dict)]
        else:
            self._class_name_list = [key for key in self._json_dict["__classes__"] if
                        isinstance(self._json_dict["__classes__"][key], dict)]

        # Scan through the dictionary - taking specials into account
        for key in self._json_dict:

            # Ignore the __doc__ key - as it has already been consumed
            if key == "__doc__":
                continue

            if not implicit:
                if key == "__classes__":
                    for cls_name, cls_dict in self._json_dict[key].items():
                        if isinstance(cls_dict,dict):
                                ci = ClassInfo(name=cls_name,
                                               json_segment=cls_dict,
                                               parent=self)
                                self._classes.append(ci)
                                mod_code = ci.generate(mod_code,
                                                       loader=self._loader)
                        else:
                            raise ImportError("Unable to Import : "
                                              "classes must be defined "
                                              "as json dictionaries {}".format(
                                    self._loader.__class__.
                                        _found_modules[self._module_name]))
                else:
                    ma = ModuleAttribute(self._json_dict[key], key, parent=self)
                    self._attributes.append( ma )
                    mod_code = ma.generate(mod_code)
            else:
                if isinstance(self._json_dict[key], dict):
                    ci = ClassInfo(name=key, json_segment=self._json_dict[key],
                                   parent=self)
                    self._classes.append(ci)
                    mod_code = ci.generate(mod_code, loader=self._loader)
                else:
                    # Everything else is treated as a module level attribute
                    ma = ModuleAttribute(self._json_dict[key], key, parent=self)
                    self._attributes.append( ma )
                    mod_code = ma.generate(mod_code)

        mod_code = self._generate_module_get_attributes_function(mod_code)
        mod_code = self._generate_module_get_classes_function(mod_code)

        return mod_code

    def _generate_module_doc_string(self):
        """Generate the docstring for the module"""
        if "__doc__" in self._json_dict:
            mod_code = """
\"\"\"{}\"\"\"
""".format(self._json_dict["__doc__"])
        else:
            mod_code = """
\"\"\"Module {name} - Created by {loader} v{vers} \n'
   Original json data : {json_file}\n'
   Generated {date} {timez}
\"\"\"
            """.format(name=self._module_name,
                       loader=self._loader.__class__.__name__,
                       vers= version.__version__,
                       json_file=self._loader._found_modules[self._module_name],
                       date=format(datetime.datetime.now().strftime(
                           "%a %d %b %Y %H:%M:%S")),
                       timez=time.strftime("%Z (UTC %z)"))
        return mod_code

    def add_to_import(self, module_name):
        "Add something to the import list"
        self._imports.append(module_name)

    def _generate_module_NamedTuples(self, src):
        return src + """
ModuleAttributeInfo = namedtuple('ModuleAttributeInfo',['name','default'])
ClassInfo = namedtuple('ClassInfo',['name','cls_', 'parent_class'])
ClassAttributeInfo = namedtuple('ClassAttributeInfo',['name','default'])
InstanceAttributeInfo = namedtuple('ClassAttributeInfo',['name','default'])
"""

    def _generate_imports(self, src):
        """Generate all the relevant imports for this module"""
        for import_command in self._imports:
            src += """
{import_command}""".format(import_command=import_command)
        return src

    def _generate_module_get_attributes_function(self, src):
        """Generate the code for the get_attributes function"""
        attrs = ', '.join(
                ["ModuleAttributeInfo(name=\'{name}\', default={default})".format(name=attr.name,
                                                                                  default=attr.default)
                 for attr in self._attributes]
        )
        src += """
def get_attributes():
    \"\"\"Generator yielding information on module level attributes\"\"\"
    attrs = [{attrs}]
    for attr in attrs:
        yield attr
        """.format(attrs=attrs)
        return src

    def _generate_module_get_classes_function(self, src):
        """Generate the code for the get_attributes function"""
        classes = ', '.join(
                ['ClassInfo(name=\'{name}\', cls_={name}, parent_class=\'{parent_class}\')'.format(name=cls.name,
                                                            parent_class=cls.base)
                 for cls in self._classes] )

        src += """
def get_classes():
    \"\"\"Generator yielding information on defined classes attributes\"\"\"
    classes = [{classes}]
    for cls in classes:
        yield cls
        """.format(classes=classes)
        return src

def recursive_repr(value):
    """Generate a recursive repr for nested and complex data items"""

    if not (isinstance(value, dict) or isinstance(value, list)):
        return repr(value)

    if isinstance(value, dict):
        return "{" + ",".join(
            "{}:{}".format(recursive_repr(k), recursive_repr(v))
            for k, v in value.items()) + "}"

    if isinstance(value, list):
        return "[" + ",".join(recursive_repr(v) for v in value) + "]"