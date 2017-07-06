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
from rosimport import activate_hook_for, deactivate_hook_for

# importlib
# https://pymotw.com/3/importlib/index.html
# https://pymotw.com/2/importlib/index.html


from ._utils import print_importers


class TestImportMsg(unittest.TestCase):

    rosdeps_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rosdeps')

    @classmethod
    def setUpClass(cls):
        activate_hook_for(cls.rosdeps_path)

    @classmethod
    def tearDownClass(cls):
        deactivate_hook_for(cls.rosdeps_path)

    def test_import_absolute_msg(self):
        print_importers()

        # Verify that files exists and are importable
        import std_msgs.msg as std_msgs
        import genpy

        self.assertTrue(std_msgs is not None)
        self.assertTrue(std_msgs.Bool is not None)
        self.assertTrue(callable(std_msgs.Bool))
        self.assertTrue(std_msgs.Bool._type == 'std_msgs/Bool')

        # A more complex message type
        self.assertTrue(std_msgs.Header is not None)
        self.assertTrue(callable(std_msgs.Header))
        self.assertTrue(std_msgs.Header._type == 'std_msgs/Header')

        # use it !
        self.assertTrue(std_msgs.Bool(True))
        self.assertTrue(std_msgs.Header(seq=42, stamp=genpy.Time(secs=21, nsecs=7), frame_id=0))

    def test_import_class_from_absolute_msg(self):
        """Verify that"""
        print_importers()

        # Verify that files exists and are importable
        from std_msgs.msg import Bool, Header
        import genpy

        self.assertTrue(Bool is not None)
        self.assertTrue(callable(Bool))
        self.assertTrue(Bool._type == 'std_msgs/Bool')

        # A more complex message type
        self.assertTrue(Header is not None)
        self.assertTrue(callable(Header))
        self.assertTrue(Header._type == 'std_msgs/Header')

        # use it !
        self.assertTrue(Bool(True))
        self.assertTrue(Header(seq=42, stamp=genpy.Time(secs=21, nsecs=7), frame_id=0))

    def test_import_relative_msg(self):
        """Verify that package is importable relatively"""
        print_importers()

        # import first to be able to use as dependency later
        # from rosimport.msg import TestRosMsg

        from . import msg as test_msgs

        self.assertTrue(test_msgs is not None)
        self.assertTrue(test_msgs.TestMsg is not None)
        self.assertTrue(callable(test_msgs.TestMsg))
        self.assertTrue(test_msgs.TestMsg._type == 'tests/TestMsg')  # careful between ros package name and python package name

        self.assertTrue(test_msgs.TestMsgDeps is not None)
        self.assertTrue(callable(test_msgs.TestMsgDeps))
        self.assertTrue(test_msgs.TestMsgDeps._type == 'tests/TestMsgDeps')  # careful between ros package name and python package name

        # use it !
        self.assertTrue(test_msgs.TestMsg(test_bool=True, test_string='Test').test_bool)

        self.assertTrue(test_msgs.TestMsgDeps(
            test_bool=True,
            test_std_bool=True,  # implicit import of std_msgs
            test_ros_deps=test_msgs.TestRosMsgDeps(   # dependency imported
                test_ros_std_bool=True,  # implicit import of std_msgs
                test_ros_msg=test_msgs.TestRosMsg(test_ros_bool=True)  # dependency of dependency
            )))

    def test_import_class_from_relative_msg(self):
        """Verify that message class is importable relatively"""
        print_importers()

        from .msg import TestMsg, TestMsgDeps, TestRosMsgDeps, TestRosMsg

        self.assertTrue(TestMsg is not None)
        self.assertTrue(callable(TestMsg))
        self.assertTrue(TestMsg._type == 'tests/TestMsg')  # careful between ros package name and python package name

        self.assertTrue(TestMsgDeps is not None)
        self.assertTrue(callable(TestMsgDeps))
        self.assertTrue(TestMsgDeps._type == 'tests/TestMsgDeps')  # careful between ros package name and python package name

        # use it !
        self.assertTrue(TestMsg(test_bool=True, test_string='Test').test_bool)

        self.assertTrue(TestMsgDeps(
            test_bool=True,
            test_std_bool=True,  # implicit import of std_msgs
            test_ros_deps=TestRosMsgDeps(   # dependency imported
                test_ros_std_bool=True,  # implicit import of std_msgs
                test_ros_msg=TestRosMsg(test_ros_bool=True)  # dependency of dependency
            )))

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

    ros_comm_msgs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rosdeps', 'ros_comm_msgs')
    # For dependencies
    rosdeps_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rosdeps')

    @classmethod
    def setUpClass(cls):
        activate_hook_for(cls.rosdeps_path, cls.ros_comm_msgs_path)

    @classmethod
    def tearDownClass(cls):
        deactivate_hook_for(cls.rosdeps_path, cls.ros_comm_msgs_path)

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
        from . import msg as test_msgs

        self.assertTrue(test_srvs is not None)

        self.assertTrue(test_srvs.TestSrv is not None)
        self.assertTrue(callable(test_srvs.TestSrv))
        self.assertTrue(test_srvs.TestSrv._type == 'tests/TestSrv')  # careful between ros package name and python package name

        self.assertTrue(test_srvs.TestSrvRequest is not None)
        self.assertTrue(callable(test_srvs.TestSrvRequest))
        self.assertTrue(test_srvs.TestSrvRequest._type == 'tests/TestSrvRequest')  # careful between ros package name and python package name

        self.assertTrue(test_srvs.TestSrvResponse is not None)
        self.assertTrue(callable(test_srvs.TestSrvResponse))
        self.assertTrue(test_srvs.TestSrvResponse._type == 'tests/TestSrvResponse')  # careful between ros package name and python package name

        # use it !
        self.assertTrue(test_srvs.TestSrvRequest(test_request='Test').test_request)
        self.assertTrue(test_srvs.TestSrvResponse(test_response=True).test_response)

        self.assertTrue(test_srvs.TestSrvDeps is not None)
        self.assertTrue(callable(test_srvs.TestSrvDeps))
        self.assertTrue(test_srvs.TestSrvDeps._type == 'tests/TestSrvDeps')  # careful between ros package name and python package name

        self.assertTrue(test_srvs.TestSrvDepsRequest is not None)
        self.assertTrue(callable(test_srvs.TestSrvDepsRequest))
        self.assertTrue(test_srvs.TestSrvDepsRequest._type == 'tests/TestSrvDepsRequest')  # careful between ros package name and python package name

        self.assertTrue(test_srvs.TestSrvDepsResponse is not None)
        self.assertTrue(callable(test_srvs.TestSrvDepsResponse))
        self.assertTrue(test_srvs.TestSrvDepsResponse._type == 'tests/TestSrvDepsResponse')  # careful between ros package name and python package name

        # use it !
        self.assertTrue(test_srvs.TestSrvDepsRequest(
            test_request='Test',
            test_ros_deps=test_msgs.TestRosMsgDeps(  # dependency imported
                test_ros_std_bool=True,  # implicit import of std_msgs
                test_ros_msg=test_msgs.TestRosMsg(test_ros_bool=True)  # dependency of dependency
            )))
        self.assertTrue(test_srvs.TestSrvDepsResponse(
            test_response='Test',
            test_std_bool=True,  # implicit import of std_msgs
        ))

    def test_import_class_from_relative_srv(self):
        """Verify that message class is importable relatively"""
        print_importers()

        from .srv import TestSrv, TestSrvRequest, TestSrvResponse, TestSrvDeps, TestSrvDepsRequest, TestSrvDepsResponse
        # importing message dependencies after services to verify they are transitively already imported when needed.
        from .msg import TestRosMsgDeps, TestRosMsg

        self.assertTrue(TestSrv is not None)
        self.assertTrue(callable(TestSrv))
        self.assertTrue(TestSrv._type == 'tests/TestSrv')  # careful between ros package name and python package name

        self.assertTrue(TestSrvRequest is not None)
        self.assertTrue(callable(TestSrvRequest))
        self.assertTrue(TestSrvRequest._type == 'tests/TestSrvRequest')

        self.assertTrue(TestSrvResponse is not None)
        self.assertTrue(callable(TestSrvResponse))
        self.assertTrue(TestSrvResponse._type == 'tests/TestSrvResponse')

        # use it !
        self.assertTrue(TestSrvRequest(test_request='Test').test_request)
        self.assertTrue(TestSrvResponse(test_response=True).test_response)

        #  A more complex service
        self.assertTrue(TestSrvDeps is not None)
        self.assertTrue(callable(TestSrvDeps))
        self.assertTrue(TestSrvDeps._type == 'tests/TestSrvDeps')  # careful between ros package name and python package name

        self.assertTrue(TestSrvDepsRequest is not None)
        self.assertTrue(callable(TestSrvDepsRequest))
        self.assertTrue(TestSrvDepsRequest._type == 'tests/TestSrvDepsRequest')  # careful between ros package name and python package name

        self.assertTrue(TestSrvDepsResponse is not None)
        self.assertTrue(callable(TestSrvDepsResponse))
        self.assertTrue(TestSrvDepsResponse._type == 'tests/TestSrvDepsResponse')  # careful between ros package name and python package name

        # use it !
        self.assertTrue(TestSrvDepsRequest(
            test_request='Test',
            test_ros_deps=TestRosMsgDeps(  # dependency imported
                test_ros_std_bool=True,  # implicit import of std_msgs
                test_ros_msg=TestRosMsg(test_ros_bool=True)  # dependency of dependency
            )))
        self.assertTrue(TestSrvDepsResponse(
            test_response='Test',
            test_std_bool=True,  # implicit import of std_msgs
            ))

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
