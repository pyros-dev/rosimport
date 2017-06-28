from __future__ import absolute_import, division, print_function
"""
Testing dynamic import with importlib
"""

import os
import sys
import runpy
import logging.config

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
})

# Relying on basic unittest first, to be able to easily switch the test framework in case of import conflicts.
import unittest

# Ref : http://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path

import importlib

# Importing importer module
from pyros_msgs.importer import rosmsg_finder

# importlib
# https://pymotw.com/3/importlib/index.html
# https://pymotw.com/2/importlib/index.html

#
# Note : we cannot assume anything about import implementation (different python version, different version of pytest)
# => we need to test them all...
#


from ._utils import print_importers


class TestImportLibAnotherMsg(unittest.TestCase):
    rosdeps_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'rosdeps')

    @classmethod
    def setUpClass(cls):
        # We need to be before FileFinder to be able to find our '.msg' and '.srv' files without making a namespace package
        supported_loaders = rosmsg_finder._get_supported_ros_loaders()
        ros_hook = rosmsg_finder.ROSDirectoryFinder.path_hook(*supported_loaders)
        sys.path_hooks.insert(1, ros_hook)

        sys.path.append(cls.rosdeps_path)

    @classmethod
    def tearDownClass(cls):
        # CAREFUL : Even though we remove the path from sys.path,
        # initialized finders will remain in sys.path_importer_cache
        sys.path.remove(cls.rosdeps_path)

    @unittest.skipIf(not hasattr(importlib, '__import__'), reason="importlib does not have attribute __import__")
    def test_importlib_import_absolute_msg(self):
        # Verify that files exists and are importable
        std_msgs = importlib.__import__('std_msgs.msg')
        std_msgs = std_msgs.msg

        self.assertTrue(std_msgs is not None)
        self.assertTrue(std_msgs.Bool is not None)
        self.assertTrue(callable(std_msgs.Bool))
        self.assertTrue(std_msgs.Bool._type == 'std_msgs/Bool')

        # use it !
        self.assertTrue(std_msgs.Bool(True))

    @unittest.skipIf(not hasattr(importlib, '__import__'), reason="importlib does not have attribute __import__")
    def test_importlib_import_absolute_class_raises(self):
        with self.assertRaises(ImportError):
            importlib.__import__('std_msgs.msg.Bool')

    # BROKEN 3.4 ?
    @unittest.skipIf(not hasattr(importlib, '__import__'), reason="importlib does not have attribute __import__")
    def test_importlib_import_relative_pkg(self):
        # Verify that files exists and are importable
        test_msgs = importlib.__import__('msg', globals=globals(), level=1)

        self.assertTrue(test_msgs is not None)
        self.assertTrue(test_msgs.TestMsg is not None)
        self.assertTrue(callable(test_msgs.TestMsg))
        self.assertTrue(test_msgs.TestMsg._type == 'pyros_msgs/TestMsg')  # careful between ros package name and python package name

        # use it !
        self.assertTrue(test_msgs.TestMsg(test_bool=True, test_string='Test').test_bool)

    # BROKEN 3.4 ?
    @unittest.skipIf(not hasattr(importlib, '__import__'), reason="importlib does not have attribute __import__")
    def test_importlib_import_relative_mod(self):
        # Verify that files exists and are importable
        msg = importlib.__import__('msg.TestMsg', globals=globals(), level=1)
        TestMsg = msg.TestMsg

        self.assertTrue(TestMsg is not None)
        self.assertTrue(callable(TestMsg))
        self.assertTrue(TestMsg._type == 'pyros_msgs/TestMsg')  # careful between ros package name and python package name

        # use it !
        self.assertTrue(TestMsg(test_bool=True, test_string='Test').test_bool)

    @unittest.skipIf(not hasattr(importlib, 'find_loader') or not hasattr(importlib, 'load_module'),
                     reason="importlib does not have attribute find_loader or load_module")
    def test_importlib_loadmodule_absolute_msg(self):
        # Verify that files exists and are dynamically importable
        pkg_list = 'std_msgs.msg'.split('.')[:-1]
        mod_list = 'std_msgs.msg'.split('.')[1:]
        pkg = None
        for pkg_name, mod_name in zip(pkg_list, mod_list):
            pkg_loader = importlib.find_loader(pkg_name, pkg.__path__ if pkg else None)
            pkg = pkg_loader.load_module(mod_name)

        std_msgs = pkg

        self.assertTrue(std_msgs is not None)
        self.assertTrue(std_msgs.Bool is not None)
        self.assertTrue(callable(std_msgs.Bool))
        self.assertTrue(std_msgs.Bool._type == 'std_msgs/Bool')

        # use it !
        self.assertTrue(std_msgs.Bool(True))

        # TODO : implement some differences and check we get them...
        if hasattr(importlib, 'reload'):  # recent version of importlib
            # attempting to reload
            importlib.reload(std_msgs)
        else:
            pass

    @unittest.skipIf(not hasattr(importlib, 'find_loader') or not hasattr(importlib, 'load_module'),
                     reason="importlib does not have attribute find_loader or load_module")
    def test_importlib_loadmodule_absolute_class(self):
        # Verify that files exists and are dynamically importable
        pkg_list = 'std_msgs.msg.Bool'.split('.')[:-1]
        mod_list = 'std_msgs.msg.Bool'.split('.')[1:]
        pkg = None
        for pkg_name, mod_name in zip(pkg_list, mod_list):
            pkg_loader = importlib.find_loader(pkg_name, pkg.__path__ if pkg else None)
            pkg = pkg_loader.load_module(mod_name)

        Bool = pkg

        self.assertTrue(Bool is not None)
        self.assertTrue(callable(Bool))
        self.assertTrue(Bool._type == 'std_msgs/Bool')

        # use it !
        self.assertTrue(Bool(True))

        # TODO : implement some differences and check we get them...
        if hasattr(importlib, 'reload'):  # recent version of importlib
            # attempting to reload
            importlib.reload(Bool)
        else:
            pass

    @unittest.skipIf(not hasattr(importlib, 'find_loader') or not hasattr(importlib, 'load_module'),
                     reason="importlib does not have attribute find_loader or load_module")
    def test_importlib_loadmodule_relative_msg(self):
        # Verify that files exists and are dynamically importable
        pkg_list = '.msg'.split('.')[:-1]
        mod_list = '.msg'.split('.')[1:]
        pkg = None
        for pkg_name, mod_name in zip(pkg_list, mod_list):
            pkg_loader = importlib.find_loader(pkg_name, pkg.__path__ if pkg else None)
            pkg = pkg_loader.load_module(mod_name)

        test_msgs = pkg

        self.assertTrue(test_msgs is not None)
        self.assertTrue(test_msgs.TestMsg is not None)
        self.assertTrue(callable(test_msgs.TestMsg))
        self.assertTrue(test_msgs.TestMsg._type == 'pyros_msgs/TestMsg')  # careful between ros package name and python package name

        # use it !
        self.assertTrue(test_msgs.TestMsg(test_bool=True, test_string='Test').test_bool)

        # TODO : implement some differences and check we get them...
        if hasattr(importlib, 'reload'):  # recent version of importlib
            # attempting to reload
            importlib.reload(test_msgs)
        else:
            pass

    @unittest.skipIf(not hasattr(importlib, 'find_loader') or not hasattr(importlib, 'load_module'),
                     reason="importlib does not have attribute find_loader or load_module")
    def test_importlib_loadmodule_relative_class(self):
        # Verify that files exists and are dynamically importable
        pkg_list = '.msg.TestMsg'.split('.')[:-1]
        mod_list = '.msg.TestMsg'.split('.')[1:]
        pkg = None
        for pkg_name, mod_name in zip(pkg_list, mod_list):
            pkg_loader = importlib.find_loader(pkg_name, pkg.__path__ if pkg else None)
            pkg = pkg_loader.load_module(mod_name)

        TestMsg = pkg

        self.assertTrue(TestMsg is not None)
        self.assertTrue(callable(TestMsg))
        self.assertTrue(TestMsg._type == 'pyros_msgs/TestMsg')

        # use it !
        self.assertTrue(TestMsg(test_bool=True, test_string='Test').test_bool)

        # TODO : implement some differences and check we get them...
        if hasattr(importlib, 'reload'):  # recent version of importlib
            # attempting to reload
            importlib.reload(TestMsg)
        else:
            pass

    # TODO : dynamic using module_spec (python 3.5)

    @unittest.skipIf(not hasattr(importlib, 'import_module'), reason="importlib does not have attribute import_module")
    def test_importlib_importmodule_absolute_msg(self):
        # Verify that files exists and are dynamically importable
        std_msgs = importlib.import_module('std_msgs.msg')

        self.assertTrue(std_msgs is not None)
        self.assertTrue(std_msgs.Bool is not None)
        self.assertTrue(callable(std_msgs.Bool))
        self.assertTrue(std_msgs.Bool._type == 'std_msgs/Bool')

        # use it !
        self.assertTrue(std_msgs.Bool(True))

        if hasattr(importlib, 'reload'):  # recent version of importlib
            # attempting to reload
            importlib.reload(std_msgs)
        else:
            pass

        assert std_msgs is not None

    @unittest.skipIf(not hasattr(importlib, 'import_module'),
                     reason="importlib does not have attribute import_module")
    def test_importlib_importmodule_absolute_class_raises(self):
        with self.assertRaises(ImportError):
            importlib.import_module('std_msgs.msg.Bool')

    @unittest.skipIf(not hasattr(importlib, 'import_module'), reason="importlib does not have attribute import_module")
    def test_importlib_importmodule_relative_msg(self):

        assert __package__
        # Verify that files exists and are dynamically importable
        test_msgs = importlib.import_module('.msg', package=__package__)

        self.assertTrue(test_msgs is not None)
        self.assertTrue(test_msgs.TestMsg is not None)
        self.assertTrue(callable(test_msgs.TestMsg))
        self.assertTrue(test_msgs.TestMsg._type == 'pyros_msgs/TestMsg')  # careful between ros package name and python package name

        # use it !
        self.assertTrue(test_msgs.TestMsg(test_bool=True, test_string='Test').test_bool)

        if hasattr(importlib, 'reload'):  # recent version of importlib
            # attempting to reload
            importlib.reload(test_msgs)
        else:
            pass

        assert test_msgs is not None

    @unittest.skipIf(not hasattr(importlib, 'import_module'),
                     reason="importlib does not have attribute import_module")
    def test_importlib_importmodule_relative_class_raises(self):

        assert __package__
        with self.assertRaises(ImportError):
            importlib.import_module('.msg.TestMsg', package=__package__)

    # TODO
    # def test_double_import_uses_cache(self):  #
    #     print_importers()
    #     # Verify that files exists and are importable
    #     import std_msgs.msg as std_msgs
    #
    #     self.assertTrue(std_msgs.Bool is not None)
    #     self.assertTrue(callable(std_msgs.Bool))
    #     self.assertTrue(std_msgs.Bool._type == 'std_msgs/Bool')
    #
    #     import std_msgs.msg as std_msgs2
    #
    #     self.assertTrue(std_msgs == std_msgs2)




def test_importlib_srv_module():
    pass
    # TODO
    # # Verify that files exists and are importable
    # msg_mod = importlib.import_module('test_gen_msgs.srv.TestSrv')


if __name__ == '__main__':
    import pytest
    pytest.main(['-s', '-x', __file__, '--boxed'])
