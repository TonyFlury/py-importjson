#!/usr/bin/env python
"""
# importjson : Test Suite for test_importjson

Summary : 
    <summary of module/class being tested>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""
import unittest
from TempDirectoryContext import TempDirectoryContext as TestDirCont
from random import sample
from string import lowercase
import sys
import importlib
import importjson
import os
import inspect
from distutils.version import StrictVersion as StVers

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '16 Oct 2015'

_installation_failed = False
_imports_failed = False


def set_module_flag(name, val):
    sys.modules[__name__].setattr(name, val)


def get_module_flag(name):
    return sys.modules[__name__].getattr(name)


def cmp_version(x, y):
    return cmp(StVers(x), StVers(y))


class Installation(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_000_001_HookAppend(self):
        """Confirm that the Hook is correctly appended"""
        self.assertEqual(isinstance(sys.meta_path[-1], importjson.importjson.JSONLoader), True)

    def test_000_002_Version(self):
        """Confirm correct version - expecting 0.0.1a1 or better"""
        self.assertTrue(cmp_version(importjson.version.__version__, "0.0.1a1") > 0)

    @unittest.skipIf(cmp_version(importjson.version.__version__, "0.0.1a5") < 0,
                     "Only gives exception on v0.0.1a5 or higher")
    def test_000_010_configurationObsolete(self):
        """Test obsolete config item - will only be tested when v0.01a5"""
        with self.assertRaises(ValueError) as cm:
            importjson.configure("AllDictionariesAsClasses", True)
            print cm.exception

    def test_000_010_configurationValid(self):
        """Test obsolete config item"""
        importjson.configure("JSONSuffixes", [".JSON"])
        self.assertEqual(importjson.get_configure("JSONSuffixes"), [".JSON"])

        importjson.configure("JSONSuffixes", [".json"])

    def test_000_010_configurationInvalid(self):
        """Test unknown config item"""
        with self.assertRaises(ValueError):
            importjson.configure("InvalidConfig", True)

        with self.assertRaises(ValueError):
            importjson.get_configure("InvalidConfig")


class ModuleContentTest(unittest.TestCase):
    def setUp(self):
        self.tm, self.mod_name = None, None

    def tearDown(self):
        del sys.path[-1]
        if self.tm:
            del sys.modules[self.tm.__name__]

    _module_name = set()

    @staticmethod
    def _random_name():
        """Generate previously unused random name"""
        name = "".join("".join(sample(lowercase, 7)))
        while name in ModuleContentTest._module_name:
            name = "".join("".join(sample(lowercase, 7)))
        return name

    def createModule(self, json_str, perm_error=False):
        """Generate a json file in a random file in a random directory - and then import it

            :param json_str : The json to write to the file
            :param perm_error : A boolean - whether there is to be an perm_error in this module - i.e. wrong permissions
        """
        with TestDirCont() as tempd:
            sys.path.append(tempd)
            self.mod_name = ModuleContentTest._random_name()
            self.path = os.path.join(tempd, self.mod_name + ".json")
            with open(self.path, "w") as json_fp:
                json_fp.write(json_str)

            if perm_error:
                os.chmod(self.path, 0o200)

        self.tm = importlib.import_module(self.mod_name)


class ModuleData(ModuleContentTest):
    def setUp(self):
        super(ModuleData, self).setUp()

    def tearDown(self):
        super(ModuleData, self).tearDown()

    def test_010_000_BasicModuleName(self):
        """Import module and check module name"""

        self.createModule("""
{
    "test_value":0
}""")
        self.assertEqual(self.tm.__name__, self.mod_name)

    def test_010_001_BasicModulePath(self):
        """Import module and check module path"""

        self.createModule("""
{
    "test_value":0
}""")
        self.assertEqual(self.tm.__file__, self.path)

    def test_010_002_BasicModulePackage(self):
        """Import module and check module package flag"""

        self.createModule("""
{
    "test_value":0
}""")
        self.assertTrue(self.tm.__package__ is None)

    def test_010_003_BasicModuleSysmodule(self):
        """Import module and check module exists in sys.modules"""

        self.createModule("""
{
    "test_value":0
}""")
        self.assertEqual(self.tm, sys.modules[self.mod_name])

    def test_010_004_BasicModuleLoader(self):
        """Import module and check loader instance for the module"""

        self.createModule("""
{
    "test_value":0
}""")
        self.assertTrue(isinstance(self.tm.__loader__, importjson.JSONLoader))

    def test_010_005_BasicModuleGetSource(self):
        """Import module and check get_source call"""

        self.createModule("""
{
    "__doc__":"",
    "test_value":0

}""")
        self.assertEqual(self.tm.__loader__.get_source(self.mod_name),
                         '""""""\n\ntest_value = 0\n')

    def test_010_005_BasicModuleLoaderIsPackage(self):
        """Import module and check loader is_package method"""

        self.createModule("""
{
    "test_value":0
}""")
        self.assertTrue(self.tm.__package__ is None)
        self.assertFalse(self.tm.__loader__.is_package(self.mod_name))

    def test_010_006_BasicModuleGet_code(self):
        """Import module and check get_code call"""

        self.createModule("""
{
    "test_value":0
}""")
        c = self.tm.__loader__.get_code(self.mod_name)
        self.assertTrue(inspect.iscode(c))

    def test_010_052_ValidJsonReload(self):
        """Test module reload works correctly"""
        self.createModule("{}")
        m1, p1, n1 = self.tm, self.path, self.mod_name
        with open(self.path, "w") as fp:
            fp.write('{ "a":1 }')
        reload(m1)
        self.assertEqual(sys.modules[n1], m1)
        self.assertEqual(sys.modules[n1].__name__, n1)
        self.assertEqual(sys.modules[n1].__file__, p1)

    def test_010_053_ValidJsonDirectLoad(self):
        """Test load_module call works correctly"""
        self.createModule("{}")
        m1, p1, n1 = self.tm, self.path, self.mod_name
        with open(self.path, "w") as fp:
            fp.write('{ "a":1 }')
        newm = m1.__loader__.load_module(n1)  # Load directly - rather than calling reload
        self.assertEqual(sys.modules[n1], newm)
        self.assertEqual(newm.__name__, n1)
        self.assertEqual(newm.__file__, p1)


class ModuleDataErrors(ModuleContentTest):
    def setUp(self):
        super(ModuleDataErrors, self).setUp()

    def tearDown(self):
        super(ModuleDataErrors, self).tearDown()

    def test_015_000_is_packageUnknownModule(self):
        """Test that loader.is_package fails to find module not previously loaded"""
        self.createModule("{}")
        with self.assertRaises(ImportError):
            self.tm.__loader__.is_package(self._random_name())

    def test_015_001_get_codeUnknownModule(self):
        """Test that loader.get_code fails to find module not previously loaded"""
        self.createModule("{}")
        with self.assertRaises(ImportError):
            self.tm.__loader__.get_code(self._random_name())

    def test_015_002_get_sourceUnknownModule(self):
        """Test that loader.get_source fails to find module not previously loaded"""
        self.createModule("{}")
        with self.assertRaises(ImportError):
            self.tm.__loader__.get_source(self._random_name())

    def test_010_053_ValidJsonDirectLoad(self):
        """Test module load_module works correctly"""
        self.createModule("{}")
        with self.assertRaises(ImportError):
            self.tm.__loader__.load_module(self._random_name())  # Load directly - rather than calling reload

    def test_015_050_InvalidJSonEmpty(self):
        """Test that empty file is not able to be imported"""
        with self.assertRaises(ImportError):
            self.createModule("")

    def test_015_051_InvalidJSonList(self):
        """Test that a list is not able to be imported"""
        with self.assertRaises(ImportError):
            self.createModule("[]")

    def test_015_052_InvalidJSonIncomplete(self):
        """Test that an invalid json is not able to be imported"""
        with self.assertRaises(ImportError):
            self.createModule("[}")

    def test_015_052_InvalidJSonNotOpenable(self):
        """Test that a file without read permission cannot be imported"""
        with self.assertRaises(ImportError):
            self.createModule("{}", perm_error=True)


class ModuleAttributes(ModuleContentTest):
    def setUp(self):
        super(ModuleAttributes, self).setUp()

    def tearDown(self):
        super(ModuleAttributes, self).tearDown()

    def test_016_010_SimpleJsonInt(self):
        """Import module with single Int value"""
        self.createModule("""
{
    "test_value":0
}""")

        self.assertIs(sys.modules[self.mod_name], self.tm)
        self.assertEqual(self.tm.test_value, 0)

    def test_016_011_SimpleJsonFloat(self):
        """Import module with single Float value"""

        self.createModule("""
{
    "test_value":0.1
}""")

        self.assertIs(sys.modules[self.mod_name], self.tm)
        self.assertAlmostEquals(self.tm.test_value, 0.1, 5)

    def test_016_012_SimpleJsonString(self):
        """Import module with single String value"""

        self.createModule("""
{
    "test_value":"Hello"
}""")

        self.assertIs(sys.modules[self.mod_name], self.tm)
        self.assertEqual(self.tm.test_value, "Hello")

    def test_016_013_SimpleJsonDict(self):
        """Import module with single Dict Module Data Attribute """

        # must have __classes__ to ensure correct interpretation
        self.createModule("""
{
    "test_value":{"key1":0, "key2":1},
    "__classes__":{}
}""")

        self.assertIs(sys.modules[self.mod_name], self.tm)
        self.assertDictEqual(self.tm.test_value, {"key1": 0, "key2": 1})

    def test_016_014_SimpleJsonWithList(self):
        """Import module with single Dict Module Data Attribute - with a sub list"""

        # Test included to check correct interpretation of all type and elements within the dict

        # must have __classes__ to ensure correct interpretation
        self.createModule("""
{
    "test_value":{"key1":0, "key2":[]},
    "__classes__":{}
}""")
        self.assertIs(sys.modules[self.mod_name], self.tm)
        self.assertDictEqual(self.tm.test_value, {"key1": 0, "key2": []})

    def test_016_020_TwoModuleAttributes(self):
        """Import module with two attributes"""
        self.createModule("""
{
    "test_value1":1,
    "test_value2":2
}""")

        self.assertIs(sys.modules[self.mod_name], self.tm)
        self.assertEqual(self.tm.test_value1, 1)
        self.assertEqual(self.tm.test_value2, 2)

    def docstring_content(self):
        """Class name changed after 0.0.1a2"""
        if cmp_version(importjson.importjson.__version__, "0.0.1a2") > 0:
            return "Module {} - Created by JSONLoader".format(self.mod_name)
        else:
            return "Module {} - Created by JSONFinder".format(self.mod_name)

    def test_016_030_DefaultDocumentationString(self):
        """Test the Default Documentation String"""
        self.createModule("""
{
    "test_value":0
}""")

        self.assertIs(sys.modules[self.mod_name], self.tm)
        self.assertTrue(isinstance(self.tm.__doc__, basestring))

        # Class name changes on version 0.0.1a2
        self.assertTrue(self.tm.__doc__.startswith(self.docstring_content()))

        self.assertTrue("Original json data : {}".format(self.tm.__file__) in self.tm.__doc__)

    def test_016_031_OverrideDocumentationString(self):
        """Test the Overrider of the Documentation String"""
        self.createModule("""
{
    "__doc__":"Override documentation string",
    "test_value":0
}""")
        self.assertIs(sys.modules[self.mod_name], self.tm)
        self.assertTrue(isinstance(self.tm.__doc__, basestring))
        self.assertEqual(self.tm.__doc__, "Override documentation string")


class ClassTests(ModuleContentTest):
    pass


class SingleAttrClass(ClassTests):
    def setUp(self):
        pass

    def standard_case(self):
        """Override for the appropriate specific json format"""
        pass

    def tearDown(self):
        # Not sure why this is needed - but in some cases tm doesn't exist.
        if not hasattr(self, "tm"):
            return

        del sys.path[-1]
        if self.tm:
            del sys.modules[self.tm.__name__]
        self.tm, self.mod_name = None, None

    def test_020_000_SimpleClass(self):
        """Import simple single class"""
        self.standard_case()

        self.assertTrue("classa" in dir(self.tm))
        self.assertTrue(inspect.isclass(self.tm.classa))
        self.assertTrue(inspect.isdatadescriptor(self.tm.classa.attr))
        self.assertTrue(inspect.ismethod(self.tm.classa.__init__))

    def test_020_001_SimpleClassInstantiatedDefaults(self):
        """Import simple single class - check the instance has the right defaults"""
        self.standard_case()

        self.assertTrue(inspect.isclass(self.tm.classa))
        inst = self.tm.classa()
        self.assertTrue(inst.__class__ is self.tm.classa)
        self.assertEqual(inst.attr, 1)

    def test_020_002_SimpleClassInstantiatedKWord(self):
        """Import simple single attr class - keyword instantiation"""
        self.standard_case()

        self.assertTrue(inspect.isclass(self.tm.classa))
        inst = self.tm.classa(attr=23)
        self.assertTrue(inst.__class__ is self.tm.classa)
        self.assertEqual(inst.attr, 23)

        inst = self.tm.classa(attr="Hello")
        self.assertTrue(inst.__class__ is self.tm.classa)
        self.assertEqual(inst.attr, "Hello")

    def test_020_003_SimpleClassInstantiatedNoKeyword(self):
        """Import simple single class - None key word instantiation"""
        self.standard_case()

        self.assertTrue(inspect.isclass(self.tm.classa))
        inst = self.tm.classa(23)
        self.assertTrue(inst.__class__ is self.tm.classa)
        self.assertEqual(inst.attr, 23)

        inst = self.tm.classa("Hello")
        self.assertTrue(inst.__class__ is self.tm.classa)
        self.assertEqual(inst.attr, "Hello")


class SingAttrClassExplicit(SingleAttrClass):
    def setUp(self):
        pass

    def standard_case(self):
        self.createModule("""
{
    "__classes__":{
        "classa":{
                "attr":1
                }
    }
}""")
        self.assertIs(sys.modules[self.mod_name], self.tm)

    def error_class_def(self, alt_type):
        self.createModule("""
{
    "__classes__":{
        "classa":%s
    }
}""" % alt_type())
        self.assertIs(sys.modules[self.mod_name], self.tm)

    def error_classes_json(self, alt_type):
        self.createModule("""
{
    "__classes__":%s
}""" % alt_type())
        self.assertIs(sys.modules[self.mod_name], self.tm)

    def test_020_010_ClassJsonIsList(self):
        """Extra case for explicit format only - check that a class definition which is a list is rejected"""
        with self.assertRaises(ImportError):
            self.error_class_def(alt_type=list)

    def test_020_011_ClassJsonIsStr(self):
        """Extra case for explicit format only - check that a class definition which is a str is rejected"""
        with self.assertRaises(ImportError):
            self.error_class_def(alt_type=str)

    def test_020_012_ClassJsonIsInt(self):
        """Extra case for explicit format only - check that a class definition which is a int is rejected"""
        with self.assertRaises(ImportError):
            self.error_class_def(alt_type=int)

    def test_020_013_ClassJsonIsFloat(self):
        """Extra case for explicit format only - check that a class definition which is a float is rejected"""
        with self.assertRaises(ImportError):
            self.error_class_def(alt_type=float)

    def test_020_030_ClassesJsonIsList(self):
        """Extra case for explicit format only - check that a classes definition which is a list is rejected"""
        with self.assertRaises(ImportError):
            self.error_classes_json(alt_type=list)

    def test_020_021_ClassesJsonIsStr(self):
        """Extra case for explicit format only - check that a classes definition which is a str is rejected"""
        with self.assertRaises(ImportError):
            self.error_classes_json(alt_type=str)

    def test_020_022_ClassesJsonIsInt(self):
        """Extra case for explicit format only - check that a classes definition which is a int is rejected"""
        with self.assertRaises(ImportError):
            self.error_classes_json(alt_type=int)

    def test_020_023_ClassesJsonIsFloat(self):
        """Extra case for explicit format only - check that a classes definition which is a float is rejected"""
        with self.assertRaises(ImportError):
            self.error_classes_json(alt_type=float)


class SingleAttrClassImplicit(SingleAttrClass):
    def setUp(self):
        pass

    def standard_case(self):
        self.createModule("""
{
    "classa":{
            "attr":1
            }
}""")
        self.assertIs(sys.modules[self.mod_name], self.tm)


class MultipleAttrClass(ClassTests):
    def setUp(self):
        self.createModule("""
{
    "__classes__":{
        "classa":{
                "attr1":1,
                "attr2":2
                }
    }
}""")
        self.assertIs(sys.modules[self.mod_name], self.tm)


    def tearDown(self):
        del sys.path[-1]
        del sys.modules[self.tm.__name__]

    def test_030_000_ClassTwoAttributes(self):
        """Import simple multiple attr class - check the instance has the right defaults"""
        self.assertTrue(inspect.isclass(self.tm.classa))
        inst = self.tm.classa()
        self.assertTrue(inst.__class__ is self.tm.classa)
        self.assertEqual(inst.attr1, 1)
        self.assertEqual(inst.attr2, 2)

    def test_030_001_SimpleClassInstantiatedKWord(self):
        """Import simple multiple attr class - keyword instantiation"""

        self.assertTrue(inspect.isclass(self.tm.classa))
        inst = self.tm.classa(attr1=23, attr2=30)
        self.assertTrue(inst.__class__ is self.tm.classa)
        self.assertEqual(inst.attr1, 23)
        self.assertEqual(inst.attr2, 30)

        inst = self.tm.classa(attr1="Hello", attr2="Goodbye")
        self.assertTrue(inst.__class__ is self.tm.classa)
        self.assertEqual(inst.attr1, "Hello")
        self.assertEqual(inst.attr2, "Goodbye")

    def test_030_002_SimpleClassInstantiatedNoKeyWord(self):
        """Import simple multiple attr class - none keyword instantiation"""

        self.assertTrue(inspect.isclass(self.tm.classa))
        inst = self.tm.classa(23, 30)
        self.assertTrue(inst.__class__ is self.tm.classa)
        self.assertEqual(inst.attr1, 23)
        self.assertEqual(inst.attr2, 30)

        inst = self.tm.classa("Hello", "Goodbye")
        self.assertTrue(inst.__class__ is self.tm.classa)
        self.assertEqual(inst.attr1, "Hello")
        self.assertEqual(inst.attr2, "Goodbye")


class MultipleAttrClassExplicit(MultipleAttrClass):
    def setUp(self):
        self.createModule("""
{
    "__classes__":{
        "classa":{
                "attr1":1,
                "attr2":2
                }
    }
}""")


class MultipleAttrClassImplicit(MultipleAttrClass):
    def setUp(self):
        self.createModule("""
{
    "classa":{
            "attr1":1,
            "attr2":2
            }
}""")


class ClassAttributes(ClassTests):
    def class_attr_not_dict(self, alt_type):
        """Method to be overriden - create module where the class attributes is of type not dictionary"""
        pass

    def setUp(self):
        self.tm, self.mod_name = None, None

    def tearDown(self):
        del sys.path[-1]
        if self.tm:
            del sys.modules[self.tm.__name__]

    def test_040_000_ClassAttributes(self):
        """Import class - with class attributes"""
        self.normalclass()
        self.assertTrue(inspect.isclass(self.tm.classa))
        self.assertEqual(self.tm.classa.cls_attr1, -1)
        self.assertAlmostEqual(self.tm.classa.cls_attr2, 0.1)

    def test_040_001_ClassAttributesDocOnly(self):
        """ Test class definition with __doc__ string only"""
        self.class_doc_only(doc_string="Hello Doc string")
        self.assertTrue(inspect.isclass(self.tm.classa))
        self.assertEqual(self.tm.classa.__doc__, "Hello Doc string")

    def test_040_011_ClassAttributesListNotDict(self):
        """ Test that if class Attribute section is a list- then Import fails"""
        with self.assertRaises(ImportError):
            self.class_attr_not_dict(alt_type=list)

    def test_040_012_ClassAttributesIntNotDict(self):
        """ Test that if class Attribute section is a int - then Import fails"""
        with self.assertRaises(ImportError):
            self.class_attr_not_dict(alt_type=int)

    def test_040_013_ClassAttributeFloatNotDict(self):
        """ Test that if class Attribute section is a float - then Import fails"""
        with self.assertRaises(ImportError):
            self.class_attr_not_dict(alt_type=float)

    def test_040_014_ClassAttributesStrNotDict(self):
        """ Test that if class Attribute section is a str - then Import fails"""
        with self.assertRaises(ImportError):
            self.class_attr_not_dict(alt_type=str)


class ClassAttributesExplicit(ClassAttributes):
    def normalclass(self):
        self.createModule("""
{
    "__classes__":{
        "classa":{
            "__doc__":"Class A",
            "__class_attributes__":{
                "cls_attr1":-1,
                "cls_attr2":0.1
                },
                "attr1":1,
                "attr2":2
                }
    }
}""")

    def class_attr_not_dict(self, alt_type):
        self.createModule("""
{
    "__classes__":{
        "classa":{
            "__doc__":"Class A",
            "__class_attributes__":%s,
                "attr1":1,
                "attr2":2
                }
    }
}""" % alt_type())

    def class_doc_only(self, doc_string=""):
        self.createModule("""
{
    "__classes__":{
        "classa":{
            "__doc__":"%s"
        }
    }
}""" % doc_string)

    def test_040_020_ClassNoDataInstanceAttributes(self):
        """ Test that if class has no attributes - and has no other contents (not class attributes)"""
        self.createModule("""
{
        "__classes__":{
            "classa":{
                    }
        }
}""")
        self.assertTrue(inspect.isclass(self.tm.classa))

    def test_040_021_ClassNoDataInstanceAttributes1(self):
        """ Test that if class has no attributes - but has other contents (not class attributes)"""
        self.createModule("""
{
        "__classes__":{
            "classa":{
                "__constraints__":{}
                    }
        }
}""")
        self.assertTrue(inspect.isclass(self.tm.classa))

    def test_040_022_ClassAttributesOnly(self):
        """ Test that if class has no attributes - but has other contents (not class attributes)"""
        self.createModule("""
{
        "__classes__":{
            "classa":{
                "__class_attributes__":{
                    "attr1":1,
                    "attr2":2
                }
            }
        }
}""")
        self.assertTrue(inspect.isclass(self.tm.classa))
        self.assertEqual(self.tm.classa.attr1, 1)
        self.assertEqual(self.tm.classa.attr2, 2)


class ClassAttributesImplicit(ClassAttributes):
    def normalclass(self):
        self.createModule("""
{
    "classa":{
        "__doc__":"Class A",
        "__class_attributes__":{
            "cls_attr1":-1,
            "cls_attr2":0.1
            },
            "attr1":1,
            "attr2":2
            }
}""")

    def class_attr_not_dict(self, alt_type):
        self.createModule("""
{
        "classa":{
            "__doc__":"Class A",
            "__class_attributes__":%s,
                "attr1":1,
                "attr2":2
                }
}""" % alt_type())

    def class_doc_only(self, doc_string=""):
        self.createModule("""
{
    "classa":{
        "__doc__":"%s"
    }
}""" % doc_string)

    def test_040_020_ClassNoDataInstanceAttributes(self):
        """ Test that if class has no attributes - but has other contents (not class attributes)"""
        self.createModule("""
{
        "classa":{
                }
}""")
        self.assertTrue(inspect.isclass(self.tm.classa))

    def test_040_021_ClassNoDataInstanceAttributes1(self):
        """ Test that if class has no attributes - but has other contents (not class attributes)"""
        self.createModule("""
{
        "classa":{
            "__constraints__":{}
                }
}""")
        self.assertTrue(inspect.isclass(self.tm.classa))

    def test_040_022_ClassAttributesOnly(self):
        """ Test that if class has class attributes and nothing else"""
        self.createModule("""
{
        "classa":{
            "__class_attributes__":{
                "attr1":1,
                "attr2":2
            }
        }
}""")
        self.assertTrue(inspect.isclass(self.tm.classa))
        self.assertEqual(self.tm.classa.attr1, 1)
        self.assertEqual(self.tm.classa.attr2, 2)


class ClassInheritance(ClassTests):
    def setUp(self):
        self.tm, self.mod_name = None, None

    def tearDown(self):
        del sys.path[-1]
        del sys.modules[self.tm.__name__]

    def test_050_000_ClassInheritance(self):
        """Import two classes - with inheritance between them"""
        self.assertTrue(inspect.isclass(self.tm.classa))
        self.assertTrue(inspect.isclass(self.tm.classb))
        self.assertTrue(issubclass(self.tm.classb, self.tm.classa))
        insta = self.tm.classa()
        instb = self.tm.classb()
        self.assertEqual((insta.a1, insta.a2), (1, 2))
        self.assertEqual((instb.a1, instb.a2), (1, 2))
        self.assertEqual((instb.b1, instb.b2), (3, 4))


class ClassInheritanceExplicit(ClassInheritance):
    def setUp(self):
        self.createModule("""
{
    "__classes__":{
        "classa":{
            "__doc__":"Class A",
                "a1":1,
                "a2":2
                },
        "classb":{
            "__doc__":"Class B",
            "__parent__":"classa",
                "b1":3,
                "b2":4
                }
    }
}""")


class ClassInheritanceImplicit(ClassInheritance):
    def setUp(self):
        self.createModule("""
{
    "classa":{
        "__doc__":"Class A",
            "a1":1,
            "a2":2
            },
    "classb":{
        "__doc__":"Class B",
        "__parent__":"classa",
            "b1":3,
            "b2":4
            }
}""")


class ClassAttrConstraint(ClassTests):
    def setUp(self):
        self.tm, self.mod_name = None, None

    def tearDown(self):
        del sys.path[-1]
        if self.tm:
            del sys.modules[self.tm.__name__]
        self.tm, self.mod_name = None, None

    # noinspection PyUnusedLocal
    def test_100_000_min_constraint(self):
        """Integer attribute with min constraint"""
        self.createModule("""
{
    "classa":{
            "a1":1,
        "__constraints__":{
            "a1":{
                "min":0
                }
            }
        }
}""")

        self.assertTrue("classa" in dir(self.tm))
        insta = self.tm.classa()
        insta.a1 = 10

        with self.assertRaises(ValueError):
            insta.a1 = -1

        with self.assertRaises(ValueError):
            insta = self.tm.classa(a1=-1)

    # noinspection PyUnusedLocal
    def test_100_010_max_constraint(self):
        """Integer attribute with max constraint"""
        self.createModule("""
{
    "classa":{
            "a1":1,
        "__constraints__":{
            "a1":{
                "max":10
                }
            }
        }
}""")

        self.assertTrue("classa" in dir(self.tm))
        insta = self.tm.classa()
        insta.a1 = 9

        with self.assertRaises(ValueError):
            insta.a1 = 11

        with self.assertRaises(ValueError):
            insta = self.tm.classa(a1=20)

    # noinspection PyUnusedLocal,PyUnusedLocal
    def test_100_010_min_max_constraint(self):
        """Integer attribute with min/max constraint"""
        self.createModule("""
{
    "classa":{
            "a1":1,
        "__constraints__":{
            "a1":{
                "min":0,
                "max":10
                }
            }
        }
}""")

        self.assertTrue("classa" in dir(self.tm))
        insta = self.tm.classa()

        with self.assertRaises(ValueError):
            insta.a1 = -1

        with self.assertRaises(ValueError):
            insta.a1 = 11

        with self.assertRaises(ValueError):
            insta = self.tm.classa(a1=20)

        with self.assertRaises(ValueError):
            insta = self.tm.classa(a1=-2)

    def test_100_020_type_int_constraint(self):
        """Integer attribute with type constraint"""
        self.createModule("""
{
    "classa":{
            "a1":1,
        "__constraints__":{
            "a1":{
                "type":"int"
                }
            }
        }
}""")

        self.assertTrue("classa" in dir(self.tm))
        insta = self.tm.classa()
        self.assertEqual(insta.a1, 1)

        with self.assertRaises(TypeError):
            insta.a1 = "Hello"
        self.assertEqual(insta.a1, 1)

        with self.assertRaises(TypeError):
            insta.a1 = 11.1
        self.assertEqual(insta.a1, 1)

        with self.assertRaises(TypeError):
            insta.a1 = {}
        self.assertEqual(insta.a1, 1)

        with self.assertRaises(TypeError):
            insta.a1 = []
        self.assertEqual(insta.a1, 1)

        insta.a1 = False

    def test_100_021_type_str_constraint(self):
        """String attribute with type constraint"""
        self.createModule("""
{
    "classa":{
            "a1":"a",
        "__constraints__":{
            "a1":{
                "type":"str"
                }
            }
        }
}""")

        self.assertTrue("classa" in dir(self.tm))
        insta = self.tm.classa()
        self.assertEqual(insta.a1, "a")

        with self.assertRaises(TypeError):
            insta.a1 = 11
        self.assertEqual(insta.a1, "a")

        with self.assertRaises(TypeError):
            insta.a1 = 11.1
        self.assertEqual(insta.a1, "a")

        with self.assertRaises(TypeError):
            insta.a1 = {}
        self.assertEqual(insta.a1, "a")

        with self.assertRaises(TypeError):
            insta.a1 = []
        self.assertEqual(insta.a1, "a")

        with self.assertRaises(TypeError):
            insta.a1 = False
        self.assertEqual(insta.a1, "a")

    def test_100_022_type_float_constraint(self):
        """String attribute with type constraint"""
        self.createModule("""
{
    "classa":{
            "a1":1.2,
        "__constraints__":{
            "a1":{
                "type":"float"
                }
            }
        }
}""")

        self.assertTrue("classa" in dir(self.tm))
        insta = self.tm.classa()
        self.assertAlmostEquals(insta.a1, 1.2)

        with self.assertRaises(TypeError):
            insta.a1 = "a"
        self.assertAlmostEquals(insta.a1, 1.2)

        with self.assertRaises(TypeError):
            insta.a1 = {}
        self.assertAlmostEquals(insta.a1, 1.2)

        with self.assertRaises(TypeError):
            insta.a1 = []
        self.assertAlmostEquals(insta.a1, 1.2)

        insta.a1 = False
        self.assertEqual(insta.a1, 0)

        insta.a1 = 1
        self.assertEqual(insta.a1, 1)

    def test_100_030_not_none_true_constraint(self):
        """String attribute with type constraint"""
        self.createModule("""
{
    "classa":{
            "a1":0,
        "__constraints__":{
            "a1":{
                "not_none":true
                }
            }
        }
}""")

        self.assertTrue("classa" in dir(self.tm))
        insta = self.tm.classa()
        insta.a1 = 1

        with self.assertRaises(ValueError):
            insta.a1 = None

    def test_100_031_not_none_false_constraint(self):
        """String attribute with type constraint"""
        self.createModule("""
{
    "classa":{
            "a1":0,
        "__constraints__":{
            "a1":{
                "not_none":false
                }
            }
        }
}""")

        self.assertTrue("classa" in dir(self.tm))
        insta = self.tm.classa()
        insta.a1 = None

    def test_100_040_read_only_true_constraint(self):
        """String attribute with type constraint"""
        self.createModule("""
{
    "classa":{
            "a1":0,
        "__constraints__":{
            "a1":{
                "read_only":true
                }
            }
        }
}""")

        self.assertTrue("classa" in dir(self.tm))
        insta = self.tm.classa()

        with self.assertRaises(ValueError):
            insta.a1 = 1

    def test_100_030_read_only_false_constraint(self):
        """String attribute with type constraint"""
        self.createModule("""
{
    "classa":{
            "a1":0,
        "__constraints__":{
            "a1":{
                "read_only":false
                }
            }
        }
}""")

        self.assertTrue("classa" in dir(self.tm))
        insta = self.tm.classa()
        insta.a1 = 1


# noinspection PyUnusedLocal
def load_install_tests(loader, tests=None, pattern=None):
    test_classes = [
        Installation,
    ]

    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite


# noinspection PyUnusedLocal
def load_remaining_tests(loader, tests=None, pattern=None):
    test_classes = [
        ModuleData,
        ModuleDataErrors,
        ModuleAttributes,
        SingAttrClassExplicit,
        SingleAttrClassImplicit,
        MultipleAttrClassExplicit,
        MultipleAttrClassImplicit,
        ClassAttributesImplicit,
        ClassAttributesExplicit,
        ClassInheritanceExplicit,
        ClassInheritanceImplicit,
        ClassAttrConstraint
    ]

    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite


if __name__ == '__main__':
    ldr = unittest.TestLoader()

    Installtest_suite = load_install_tests(ldr)
    test_suite = load_remaining_tests(ldr)

    print "Installation of sys.meta_path hook"
    result = unittest.TextTestRunner(verbosity=1).run(Installtest_suite)
    assert isinstance(result, unittest.TestResult)
    if len(result.errors) + len(result.failures) == 0:
        print "Functionality tests - tests loader is correct, and the imported json creates a valid module"
        unittest.TextTestRunner(verbosity=1).run(test_suite)
