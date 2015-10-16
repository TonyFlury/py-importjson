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

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '16 Oct 2015'


def split_version(v):
    return tuple(int(vp) for vp in v.split("."))


def cmp_version(x, y):
    return cmp(split_version(x), split_version(y))


class Installation(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_00_001_HookAppend(self):
        """Confirm that the Hook is correctly appended"""
        self.assertEqual(isinstance(sys.meta_path[-1], importjson.importjson.JSONFinder), True)

    def test_00_002_Version(self):
        """Confirm correct version - expecting 0.0.1a1 or better"""
        self.assertGreaterEqual(importjson.importjson.__version__, "0.0.1a1")


class ModuleContentTest(unittest.TestCase):
    @staticmethod
    def write_module_json(json_str):
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
        del sys.modules[self.tm.__name__]

    def test_01_000_SimpleJson(self):
        """Import from directory on the path"""

        self.tm = self.write_module_json("""
{
    "test_value":0
}""")

        self.assertIs(sys.modules["test_module"], self.tm)
        self.assertEqual(self.tm.test_value, 0)

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

    def test_01_002_DefaultDocumentationString(self):
        """Test the Default Documentation String"""
        self.tm = self.write_module_json("""
{
    "test_value":0
}""")

        self.assertIs(sys.modules["test_module"], self.tm)
        self.assertTrue(isinstance(self.tm.__doc__, basestring))
        self.assertTrue(self.tm.__doc__.startswith("Module test_module - Created by JSONFinder"))
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


class SingleAttrClass(ModuleContentTest):
    def setUp(self):
        self.tm = self.write_module_json("""
{
    "__classes__":{
        "classa":{
                "attr":1
                }
    }
}""")

        self.tm = importlib.import_module("test_module")
        self.assertIs(sys.modules["test_module"], self.tm)

    def tearDown(self):
        del sys.path[-1]
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


class MultipleAttrClass(ModuleContentTest):
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


class ClassAttributes(ModuleContentTest):
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

    def tearDown(self):
        del sys.path[-1]
        del sys.modules[self.tm.__name__]

    def test_04_000_ClassAttributes(self):
        """Import class - with class attributes"""
        self.assertTrue(inspect.isclass(self.tm.classa))
        self.assertEqual(self.tm.classa.cls_attr1, -1)
        self.assertAlmostEqual(self.tm.classa.cls_attr2, 0.1)


class ClassInheritance(ModuleContentTest):
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


# noinspection PyUnusedLocal
def load_tests(loader, tests=None, pattern=None):
    test_classes = [Installation,
                    ModuleAttributes,
                    SingleAttrClass,
                    MultipleAttrClass,
                    ClassAttributes,
                    ClassInheritance
                    ]
    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite


if __name__ == '__main__':
    ldr = unittest.TestLoader()

    test_suite = load_tests(ldr)

    unittest.TextTestRunner(verbosity=2).run(test_suite)
