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
import templatelite
import os.path

TemplateDirectory = os.path.join(os.path.dirname(__file__), 'templates')

def render_template(template_name, **context):
    """Helper function to render a specific template"""
    return templatelite.Renderer(template_file=os.path.join(TemplateDirectory, template_name),remove_indentation=False, errors=True).from_context(context) + '\n'

@templatelite.registerModifier('join')
def join( attribute, sep, member=''):
    if member:
        return sep.join(getattr(elem, member) for elem in attribute)
    else:
        return sep.join(elem for elem in attribute)



from . import version

__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '02 Feb 2018'

class ClassAttribute(object):
    """A data holder for class attributes"""
    def __init__(self, name, default, parent):
        self._name = name
        self._default = default
        self._parent = parent

    @property
    def name(self):
        return self._name

    @property
    def default(self):
        return recursive_repr(self._default)

    def __repr__(self):
        return 'Classttribute({})'.format(self._name)

class InstanceAttribute(object):
    """A data holder for instance attributes and constraints"""
    def __init__(self, name, default, parent, constraints):
        self._name = name
        self._default = default
        self._parent = parent
        self._constraints = constraints
    @property
    def name(self):
        """The name of the attribute"""
        return self._name

    @property
    def default(self):
        """The actual default as given in the json file"""
        return self._default

    def mutable_default(self):
        """Whether the default type is mutable (i.e. a list or dict"""
        return isinstance(self._default, (list, dict))

    @property
    def parameterised_default(self):
        """The parameter string for this attribute
            Takes into account if the formal default is mutable
        """
        return '{} = {!r}'.format( self.name, self.default if not self.mutable_default() else None)

    @property
    def default_repr_format(self):
        """Argument string for default repr"""
        return "{name}={{{name}!r}}".format(name=self.name)

    def __str__(self):
        return '{} = {}'.format(self._name, self._default)

    def __repr__(self):
        return 'InstanceAttribute({})'.format(self._name)

    def constraints(self):
        """The constraints dictionary for this attribute"""
        return self._constraints

    def allowed_type(self):
        """The types that are allowed for this attribute"""
        if self._constraints["type"] in self._parent.module.class_name_list:
            return self._constraints["type"]

        return {"bool": "(bool,int)",
                        "str": "six.string_types",
                        "list": "list",
                        "int": "int",
                        "float": "(float,int)",
                        "dict": "dict"}[self._constraints["type"]]


class ClassInfo():
    """The data holder for the Classes"""
    def __init__(self, name, json_segment,parent):

        if not isinstance(json_segment, dict):
            raise ImportError("Expecting dictionary for a class")

        self._name = name
        self._json_segment = json_segment
        self._parent = parent
        self._base = self._json_segment.get('__parent__', 'object')
        self._attributes = []
        self._class_attributes = []
        self._identify_instance_attributes()
        self._identify_class_attributes()

    @property
    def name(self):
        """The unqualified class name"""
        return self._name

    @property
    def base(self):
        """The base type for this class"""
        return self._base if self._base else 'object'

    @property
    def module(self):
        """"Association back to the moduleInfo object"""
        return self._parent

    @property
    def doc_string(self):
        """The docstring for this class"""
        return self._json_segment.get("__doc__", '')

    def has_instance_attributes(self):
        """Boolean if class has instance attributes"""
        return self._attributes and True

    def instance_attributes(self):
        """Sequence of instance attributes"""
        for attr in self._attributes:
            yield attr

    def class_attributes(self):
        """Sequence of class attributes"""
        for attr in self._class_attributes:
            yield attr

    def dunder_repr_overriden(self):
        """Whether this class has a specific __repr__ specifed"""
        return '__repr__' in self._json_segment

    def dunder_repr_format(self):
        """The specified __repr__ format"""
        return self._json_segment['__repr__']

    def dunder_str_overriden(self):
        """Whether this class has a specific __str__ specifed"""
        return '__str__' in self._json_segment

    def dunder_str_format(self):
        """The specified __str__ format"""
        return self._json_segment['__str__']

    def _identify_instance_attributes(self):
        """Build the Instance attributes from the json data"""

        # Essentially unreachable - this argument will only be a dictionary
        # See how it is invoked from _create_class
        if not isinstance(self._json_segment, dict):
            raise ImportError(
                "Unable to Import : Expecting dictionary for "
                "instance attributes for {} class".format(
                    self._name))

        # Names that might be encountered which aren't attribute names.
        ignore = ['__doc__', '__parent__', '__class_attributes__', '__constraints__', '__repr__', '__str__']

        if not any(True for key in self._json_segment if key not in ignore):
            return

        # Extract the attribute and default values
        attributes = ((name,value) for name, value in self._json_segment.items() if name not in ignore)

        # Set the initial value of the attribute with constrains applied
        self._attributes = [
            InstanceAttribute( name=attr_name,
                               default=def_value, parent=self,
                               constraints=self._get_constraints( attr_name=attr_name))
          for attr_name, def_value in attributes ]

    def _identify_class_attributes(self):
        """Identify the class attributes"""

        cls_attrs = self._json_segment.get("__class_attributes__", {})

        if not isinstance(cls_attrs, dict):
            raise ImportError(
                "Invalid json : __class_attributes__ must be "
                "a dictionary for {} class".format(self._name))

        self._class_attributes = [
                    ClassAttribute(name=name, default=value, parent=self)
                    for name, value in cls_attrs.items() ]

    def _get_constraints(self, attr_name):
        """Extract the constraints for a given attribute

           Returns am empty dictionary if no constraints are defined.
        """
        class_cons = self._json_segment.get("__constraints__", None)

        # No constraints on class at all, or constraint is illdefined
        if ((class_cons is None) or
                (not isinstance(class_cons, dict)) or
                (attr_name not in class_cons) or
                (not isinstance(class_cons[attr_name], dict))):
            return dict()

        return class_cons[attr_name]


class ModuleAttribute(object):
    """Data holder for the module attribute"""
    def __init__(self, json_segment, attr_name, parent):
        self._segment = json_segment
        self._attr_name = attr_name
        self._parent = parent

    @property
    def name(self):
        """The name of the attribute"""
        return self._attr_name

    @property
    def default(self):
        """The repr of the value"""
        return recursive_repr(self._segment)


class Module():
    """Data holder of the module itself"""
    def __init__(self, module_naame, json_dict, loader):
        self._module_attributes = []
        self._module_name = module_naame
        self._json_dict = json_dict
        self._loader = loader
        self._imports = ['import six','from collections import namedtuple as namedtuple']
        self._class_name_list = []
        self._classes = []
        self._module_attributes = []

    @property
    def name(self):
        """The name of the module"""
        return self._module_name

    @property
    def class_name_list(self):
        """The name of the classes"""
        return self._class_name_list

    def has_classes(self):
        """Boolean if this module has classes"""
        return self._classes and True

    def has_attributes(self):
        """Boolean if this module has attributes"""
        return self._module_attributes and True

    @property
    def classes(self):
        """The classInfo objects for this module"""
        for cls in self._classes:
            yield cls

    @property
    def attributes(self):
        """The module attributes"""
        for attr in self._module_attributes:
            yield attr

    def has_doc_string(self):
        """Whether this has a specific doc string"""
        return "__doc__" in self._json_dict

    @property
    def doc_string(self):
        """The specific doc string"""
        return self._json_dict.get('__doc__','')

    def generated_date(self):
        """The datetime now for the generation"""
        return format(datetime.datetime.now().strftime("%a %d %b %Y %H:%M:%S"))

    def timez(self):
        """Nicely structured time zone"""
        return time.strftime("%Z (UTC %z)")

    def loader(self):
        """The name of the loader class"""
        return self._loader.__class__.__name__

    def json_file(self):
        """The name of the json file"""
        return self._loader._found_modules[self._module_name]

    def loader_version(self):
        """"The version of the json loader"""
        return self._loader.__class__.__name__

    def imports(self):
        """The imports that are required"""
        for entry in self._imports:
            yield entry

    def generate(self):
        """Generate the code required for the module - called by get_source"""

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
                        else:
                            raise ImportError("Unable to Import : "
                                              "classes must be defined "
                                              "as json dictionaries {}".format(
                                    self._loader.__class__.
                                        _found_modules[self._module_name]))
                else:
                    ma = ModuleAttribute(self._json_dict[key], key, parent=self)
                    self._module_attributes.append(ma)
            else:
                if isinstance(self._json_dict[key], dict):
                    ci = ClassInfo(name=key, json_segment=self._json_dict[key],
                                   parent=self)
                    self._classes.append(ci)
 #                   ci.generate()
                else:
                    # Everything else is treated as a module level attribute
                    ma = ModuleAttribute(self._json_dict[key], key, parent=self)
                    self._module_attributes.append(ma)

        mod_code = render_template('module_general.tmpl', module=self)

        return mod_code

    def add_to_import(self, module_name):
        "Add something to the import list"
        self._imports.append(module_name)

def recursive_repr(value):
    """Generate a recursive repr for nested and complex data items"""

    if not (isinstance(value, (OrderedDict,dict)) or isinstance(value, list)):
        return repr(value)

    if isinstance(value, (OrderedDict,dict)):
        return "{" + ",".join(
            "{}:{}".format(recursive_repr(k), recursive_repr(v))
            for k, v in value.items()) + "}"

    if isinstance(value, list):
        return "[" + ",".join(recursive_repr(v) for v in value) + "]"