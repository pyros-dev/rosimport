from __future__ import absolute_import, division, print_function

import copy

"""
Testing rosmsg_import with import keyword.
CAREFUL : these tests should run with pytest --boxed in order to avoid polluting each other sys.modules
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

# Since test frameworks (like pytest) play with the import machinery, we cannot use it here...
import unittest

# Ref : http://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path

import importlib

# Importing importer module
from rosimport import rosmsg_finder

# importlib
# https://pymotw.com/3/importlib/index.html
# https://pymotw.com/2/importlib/index.html


from ._utils import print_importers


class TestImportMsg(unittest.TestCase):

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

    def test_import_absolute_msg(self):
        print_importers()

        # Verify that files exists and are importable
        import std_msgs.msg as std_msgs

        self.assertTrue(std_msgs is not None)
        self.assertTrue(std_msgs.Bool is not None)
        self.assertTrue(callable(std_msgs.Bool))
        self.assertTrue(std_msgs.Bool._type == 'std_msgs/Bool')

        # use it !
        self.assertTrue(std_msgs.Bool(True))

    def test_import_class_from_absolute_msg(self):
        """Verify that"""
        print_importers()

        # Verify that files exists and are importable
        from std_msgs.msg import Bool

        self.assertTrue(Bool is not None)
        self.assertTrue(callable(Bool))
        self.assertTrue(Bool._type == 'std_msgs/Bool')

        # use it !
        self.assertTrue(Bool(True))

    def test_import_relative_msg(self):
        """Verify that package is importable relatively"""
        print_importers()

        from . import msg as test_msgs

        self.assertTrue(test_msgs is not None)
        self.assertTrue(test_msgs.TestMsg is not None)
        self.assertTrue(callable(test_msgs.TestMsg))
        self.assertTrue(test_msgs.TestMsg._type == 'pyros_msgs/TestMsg')  # careful between ros package name and python package name

        # use it !
        self.assertTrue(test_msgs.TestMsg(test_bool=True, test_string='Test').test_bool)

    def test_import_class_from_relative_msg(self):
        """Verify that message class is importable relatively"""
        print_importers()

        from .msg import TestMsg

        self.assertTrue(TestMsg is not None)
        self.assertTrue(callable(TestMsg))
        self.assertTrue(TestMsg._type == 'pyros_msgs/TestMsg')

        # use it !
        self.assertTrue(TestMsg(test_bool=True, test_string='Test').test_bool)

    def test_import_absolute_class_raises(self):
        print_importers()

        with self.assertRaises(ImportError):
            import std_msgs.msg.Bool

    def test_double_import_uses_cache(self):    #
        print_importers()
        # Verify that files exists and are importable
        import std_msgs.msg as std_msgs

        self.assertTrue(std_msgs.Bool is not None)
        self.assertTrue(callable(std_msgs.Bool))
        self.assertTrue(std_msgs.Bool._type == 'std_msgs/Bool')

        import std_msgs.msg as std_msgs2

        self.assertTrue(std_msgs == std_msgs2)


class TestImportSrv(unittest.TestCase):

    rosdeps_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'rosdeps', 'ros_comm_msgs')

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

    def test_import_absolute_srv(self):
        print_importers()

        # Verify that files exists and are importable
        import std_srvs.srv as std_srvs

        self.assertTrue(std_srvs is not None)
        self.assertTrue(std_srvs.SetBool is not None)
        self.assertTrue(callable(std_srvs.SetBool))
        self.assertTrue(std_srvs.SetBool._type == 'std_srvs/SetBool')

        self.assertTrue(std_srvs is not None)
        self.assertTrue(std_srvs.SetBoolRequest is not None)
        self.assertTrue(callable(std_srvs.SetBoolRequest))
        self.assertTrue(std_srvs.SetBoolRequest._type == 'std_srvs/SetBoolRequest')

        self.assertTrue(std_srvs is not None)
        self.assertTrue(std_srvs.SetBoolResponse is not None)
        self.assertTrue(callable(std_srvs.SetBoolResponse))
        self.assertTrue(std_srvs.SetBoolResponse._type == 'std_srvs/SetBoolResponse')

        # use it !
        self.assertTrue(std_srvs.SetBoolRequest(data=True).data)
        self.assertTrue(std_srvs.SetBoolResponse(success=True, message='Test').success)

    def test_import_class_from_absolute_srv(self):
        """Verify that"""
        print_importers()

        # Verify that files exists and are importable
        from std_srvs.srv import SetBool, SetBoolRequest, SetBoolResponse

        self.assertTrue(SetBool is not None)
        self.assertTrue(callable(SetBool))
        self.assertTrue(SetBool._type == 'std_srvs/SetBool')

        self.assertTrue(SetBoolRequest is not None)
        self.assertTrue(callable(SetBoolRequest))
        self.assertTrue(SetBoolRequest._type == 'std_srvs/SetBoolRequest')

        self.assertTrue(SetBoolResponse is not None)
        self.assertTrue(callable(SetBoolResponse))
        self.assertTrue(SetBoolResponse._type == 'std_srvs/SetBoolResponse')

        # use it !
        self.assertTrue(SetBoolRequest(data=True).data)
        self.assertTrue(SetBoolResponse(success=True, message='Test').success)

    def test_import_relative_srv(self):
        """Verify that package is importable relatively"""
        print_importers()

        from . import srv as test_srvs

        self.assertTrue(test_srvs is not None)

        self.assertTrue(test_srvs.TestSrv is not None)
        self.assertTrue(callable(test_srvs.TestSrv))
        self.assertTrue(test_srvs.TestSrv._type == 'pyros_msgs/TestSrv')  # careful between ros package name and python package name

        self.assertTrue(test_srvs.TestSrvRequest is not None)
        self.assertTrue(callable(test_srvs.TestSrvRequest))
        self.assertTrue(test_srvs.TestSrvRequest._type == 'pyros_msgs/TestSrvRequest')  # careful between ros package name and python package name

        self.assertTrue(test_srvs.TestSrvResponse is not None)
        self.assertTrue(callable(test_srvs.TestSrvResponse))
        self.assertTrue(test_srvs.TestSrvResponse._type == 'pyros_msgs/TestSrvResponse')  # careful between ros package name and python package name

        # use it !
        self.assertTrue(test_srvs.TestSrvRequest(test_request='Test').test_request)
        self.assertTrue(test_srvs.TestSrvResponse(test_response=True).test_response)

    def test_import_class_from_relative_srv(self):
        """Verify that message class is importable relatively"""
        print_importers()

        from .srv import TestSrv, TestSrvRequest, TestSrvResponse

        self.assertTrue(TestSrv is not None)
        self.assertTrue(callable(TestSrv))
        self.assertTrue(TestSrv._type == 'pyros_msgs/TestSrv')  # careful between ros package name and python package name

        self.assertTrue(TestSrvRequest is not None)
        self.assertTrue(callable(TestSrvRequest))
        self.assertTrue(TestSrvRequest._type == 'pyros_msgs/TestSrvRequest')

        self.assertTrue(TestSrvResponse is not None)
        self.assertTrue(callable(TestSrvResponse))
        self.assertTrue(TestSrvResponse._type == 'pyros_msgs/TestSrvResponse')

        # use it !
        self.assertTrue(TestSrvRequest(test_request='Test').test_request)
        self.assertTrue(TestSrvResponse(test_response=True).test_response)

    def test_import_absolute_class_raises(self):
        print_importers()

        with self.assertRaises(ImportError):
            import std_srvs.srv.SetBool

    def test_double_import_uses_cache(self):    #
        print_importers()
        # Verify that files exists and are importable
        import std_srvs.srv as std_srvs

        self.assertTrue(std_srvs.SetBool is not None)
        self.assertTrue(std_srvs.SetBoolRequest is not None)
        self.assertTrue(std_srvs.SetBoolResponse is not None)

        import std_srvs.srv as std_srvs2

        self.assertTrue(std_srvs == std_srvs2)

if __name__ == '__main__':
    import pytest
    pytest.main(['-s', '-x', __file__, '--boxed'])
