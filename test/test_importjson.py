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

    def test_00_001_HookAppend(self):
        """Confirm that the Hook is correctly appended"""
        self.assertEqual(isinstance(sys.meta_path[-1], importjson.importjson.JSONLoader), True)

    def test_00_002_Version(self):
        """Confirm correct version - expecting 0.0.1a1 or better"""
        self.assertTrue(cmp_version(importjson.version.__version__, "0.0.1a1") > 0)

    @unittest.skipIf(cmp_version(importjson.version.__version__ ,"0.0.1a5") < 0,"Only gives exception on v0.0.1a5 or higher")
    def test_00_010_configuration(self):
        with self.assertRaises(ValueError):
            importjson.configure("AllDictionariesAreClasses",True)

class ModuleContentTest(unittest.TestCase):
    @staticmethod
    def write_module_json(json_str):
        if "test_module" in sys.modules:
            del sys.modules["test_modules"]

        with TestDirCont() as tempd:
            sys.path.append(tempd)
            with open(os.path.join(tempd, "test_module.json"), "w") as json_fp:
                json_fp.write(json_str)

        return importlib.import_module("test_module")


class ModuleAttributes(ModuleContentTest):
    def setUp(self):
        self.tm = None

    def tearDown(self):
        del sys.path[-1]
        if self.tm:
            del sys.modules[self.tm.__name__]

    def test_01_000a_SimpleJsonInt(self):
        """Import module with single Int value"""

        self.tm = self.write_module_json("""
{
    "test_value":0
}""")

        self.assertIs(sys.modules["test_module"], self.tm)
        self.assertEqual(self.tm.test_value, 0)

    def test_01_000b_SimpleJsonFloat(self):
        """Import module with single Float value"""

        self.tm = self.write_module_json("""
{
    "test_value":0.1
}""")

        self.assertIs(sys.modules["test_module"], self.tm)
        self.assertAlmostEquals(self.tm.test_value, 0.1, 5)

    def test_01_000c_SimpleJsonString(self):
        """Import module with single String value"""

        self.tm = self.write_module_json("""
{
    "test_value":"Hello"
}""")

        self.assertIs(sys.modules["test_module"], self.tm)
        self.assertEqual(self.tm.test_value, "Hello")

    @unittest.skip("will Always fail unless __classes__ exists in the same json")
    def test_01_000d_SimpleJsonDict(self):
        """Import module with single Dict value"""

        self.tm = self.write_module_json("""
{
    "test_value":{"key1":0, "key2":1}
}""")

        self.assertIs(sys.modules["test_module"], self.tm)
        self.assertDictEqual(self.tm.test_value, {"key1": 0, "key2": 1})

    def test_01_001_TwoModuleAttributes(self):
        """Import from directory with two attributes"""
        self.tm = self.write_module_json("""
{
    "test_value1":1,
    "test_value2":2
}""")

        self.assertIs(sys.modules["test_module"], self.tm)
        self.assertEqual(self.tm.test_value1, 1)
        self.assertEqual(self.tm.test_value2, 2)

    @staticmethod
    def docstringcontent():
        """Class name changed after 0.0.1a2"""
        if cmp_version(importjson.importjson.__version__, "0.0.1a2") > 0:
            return "Module test_module - Created by JSONLoader"
        else:
            return "Module test_module - Created by JSONFinder"

    def test_01_002_DefaultDocumentationString(self):
        """Test the Default Documentation String"""
        self.tm = self.write_module_json("""
{
    "test_value":0
}""")

        self.assertIs(sys.modules["test_module"], self.tm)
        self.assertTrue(isinstance(self.tm.__doc__, basestring))

        # Class name changes on version 0.0.1a2
        self.assertTrue(self.tm.__doc__.startswith(self.docstringcontent()))

        self.assertTrue("Original json data : {}".format(self.tm.__file__) in self.tm.__doc__)

    def test_01_003_OverrideDocumentationString(self):
        """Test the Overrider of the Documentation String"""
        self.tm = self.write_module_json("""
{
    "__doc__":"Override documentation string",
    "test_value":0
}""")
        self.assertIs(sys.modules["test_module"], self.tm)
        self.assertTrue(isinstance(self.tm.__doc__, basestring))
        self.assertEqual(self.tm.__doc__, "Override documentation string")


class ClassTests(ModuleContentTest):
    pass


class SingleAttrClass(ClassTests):
    def setUp(self):
        self.tm = self.write_module_json("""
{
    "__classes__":{
        "classa":{
                "attr":1
                }
    }
}""")
        self.assertIs(sys.modules["test_module"], self.tm)

    def tearDown(self):
        del sys.path[-1]
        if self.tm:
            del sys.modules[self.tm.__name__]
        self.tm = None

    def test_02_000_SimpleClass(self):
        """Import simple single class"""

        self.assertTrue("classa" in dir(self.tm))
        self.assertTrue(inspect.isclass(self.tm.classa))
        self.assertTrue(inspect.isdatadescriptor(self.tm.classa.attr))
        self.assertTrue(inspect.ismethod(self.tm.classa.__init__))

    def test_02_001_SimpleClassInstantiatedDefaults(self):
        """Import simple single class - check the instance has the right defaults"""

        self.assertTrue(inspect.isclass(self.tm.classa))
        inst = self.tm.classa()
        self.assertTrue(inst.__class__ is self.tm.classa)
        self.assertEqual(inst.attr, 1)

    def test_02_002_SimpleClassInstantiatedKWord(self):
        """Import simple single attr class - keyword instantiation"""

        self.assertTrue(inspect.isclass(self.tm.classa))
        inst = self.tm.classa(attr=23)
        self.assertTrue(inst.__class__ is self.tm.classa)
        self.assertEqual(inst.attr, 23)

        inst = self.tm.classa(attr="Hello")
        self.assertTrue(inst.__class__ is self.tm.classa)
        self.assertEqual(inst.attr, "Hello")

    def test_02_003_SimpleClassInstantiatedNoKeyword(self):
        """Import simple single class - None key word instantiation"""

        self.assertTrue(inspect.isclass(self.tm.classa))
        inst = self.tm.classa(23)
        self.assertTrue(inst.__class__ is self.tm.classa)
        self.assertEqual(inst.attr, 23)

        inst = self.tm.classa("Hello")
        self.assertTrue(inst.__class__ is self.tm.classa)
        self.assertEqual(inst.attr, "Hello")


class SingAttrClassExplicit(SingleAttrClass):
    def setUp(self):
        self.tm = self.write_module_json("""
{
    "__classes__":{
        "classa":{
                "attr":1
                }
    }
}""")
        self.assertIs(sys.modules["test_module"], self.tm)


class SingleAttrClassImplicit(SingleAttrClass):
    def setUp(self):
        self.tm = self.write_module_json("""
{
    "classa":{
            "attr":1
            }
}""")
        self.assertIs(sys.modules["test_module"], self.tm)


class MultipleAttrClass(ClassTests):
    def setUp(self):
        self.tm = self.write_module_json("""
{
    "__classes__":{
        "classa":{
                "attr1":1,
                "attr2":2
                }
    }
}""")

    def tearDown(self):
        del sys.path[-1]
        del sys.modules[self.tm.__name__]

    def test_03_000_ClassTwoAttributes(self):
        """Import simple multiple attr class - check the instance has the right defaults"""
        self.assertTrue(inspect.isclass(self.tm.classa))
        inst = self.tm.classa()
        self.assertTrue(inst.__class__ is self.tm.classa)
        self.assertEqual(inst.attr1, 1)
        self.assertEqual(inst.attr2, 2)

    def test_03_001_SimpleClassInstantiatedKWord(self):
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

    def test_03_002_SimpleClassInstantiatedNoKeyWord(self):
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
        self.tm = self.write_module_json("""
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
        self.tm = self.write_module_json("""
{
    "classa":{
            "attr1":1,
            "attr2":2
            }
}""")


class ClassAttributes(ClassTests):
    def setUp(self):
        self.tm = None

    def tearDown(self):
        del sys.path[-1]
        if self.tm:
            del sys.modules[self.tm.__name__]

    def test_04_000_ClassAttributes(self):
        """Import class - with class attributes"""
        self.assertTrue(inspect.isclass(self.tm.classa))
        self.assertEqual(self.tm.classa.cls_attr1, -1)
        self.assertAlmostEqual(self.tm.classa.cls_attr2, 0.1)


class ClassAttributesExplicit(ClassAttributes):
    def setUp(self):
        self.tm = self.write_module_json("""
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


class ClassAttributesImplicit(ClassAttributes):
    def setUp(self):
        self.tm = self.write_module_json("""
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


class ClassInheritance(ClassTests):
    def setUp(self):
        self.tm = None

    def tearDown(self):
        del sys.path[-1]
        del sys.modules[self.tm.__name__]

    def test_05_000_ClassInheritance(self):
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
        self.tm = self.write_module_json("""
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
        self.tm = self.write_module_json("""
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
        if "test_module" in sys.modules:
            del sys.modules["test_module"]
        self.tm = None

    def tearDown(self):
        del sys.path[-1]
        if self.tm:
            del sys.modules[self.tm.__name__]
        self.tm = None

    # noinspection PyUnusedLocal
    def test_10_000_min_constraint(self):
        """Integer attribute with min constraint"""
        self.tm = self.write_module_json("""
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
    def test_10_010_max_constraint(self):
        """Integer attribute with max constraint"""
        self.tm = self.write_module_json("""
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
    def test_10_010_min_max_constraint(self):
        """Integer attribute with min/max constraint"""
        self.tm = self.write_module_json("""
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

    def test_10_020_type_int_constraint(self):
        """Integer attribute with type constraint"""
        self.tm = self.write_module_json("""
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

    def test_10_021_type_str_constraint(self):
        """String attribute with type constraint"""
        self.tm = self.write_module_json("""
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

    def test_10_022_type_float_constraint(self):
        """String attribute with type constraint"""
        self.tm = self.write_module_json("""
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

    result = unittest.TextTestRunner(verbosity=2).run(Installtest_suite)
    assert isinstance(result, unittest.TestResult)
    if len(result.errors) + len(result.failures) == 0:
        unittest.TextTestRunner(verbosity=2).run(test_suite)
