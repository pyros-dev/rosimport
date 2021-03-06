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
import site

# Importing importer module
import rosimport

# importlib
# https://pymotw.com/3/importlib/index.html
# https://pymotw.com/2/importlib/index.html


from ._utils import (
    print_importers,
    print_importers_of,
    BaseMsgTestCase,
    BaseSrvTestCase,
)



class TestImportMsg(BaseMsgTestCase):

    rosdeps_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rosdeps')

    rosimporter = rosimport.RosImporter()

    @classmethod
    def setUpClass(cls):
        # This is used for message definitions, not for python code
        site.addsitedir(cls.rosdeps_path)
        cls.rosimporter.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.rosimporter.__exit__(None, None, None)

    def test_import_absolute_msg(self):
        print_importers()

        # Verify that files exists and are importable
        import std_msgs.msg as std_msgs

        print_importers_of(std_msgs)

        self.assert_std_message_classes(std_msgs.Bool, std_msgs.Header)

    def test_import_class_from_absolute_msg(self):
        """Verify that"""
        print_importers()

        # Verify that files exists and are importable
        from std_msgs.msg import Bool, Header

        self.assert_std_message_classes(Bool, Header)

    def test_import_relative_msg(self):
        """Verify that package is importable relatively"""
        print_importers()

        from . import msg as test_msgs

        print_importers_of(test_msgs)

        self.assert_test_message_classes(test_msgs.TestMsg, test_msgs.TestMsgDeps, test_msgs.TestRosMsgDeps, test_msgs.TestRosMsg)

    def test_import_relative_msg_from_absolute(self):
        """Verify that package is importable relatively"""
        print_importers()

        import test_rosimport.msg as test_msgs

        print_importers_of(test_msgs)

        self.assert_test_message_classes(test_msgs.TestMsg, test_msgs.TestMsgDeps, test_msgs.TestRosMsgDeps, test_msgs.TestRosMsg)

    def test_import_class_from_relative_msg(self):
        """Verify that message class is importable relatively"""
        print_importers()

        from .msg import TestMsg, TestMsgDeps, TestRosMsgDeps, TestRosMsg

        self.assert_test_message_classes(TestMsg, TestMsgDeps, TestRosMsgDeps, TestRosMsg)

    def test_import_absolute_class_raises(self):
        print_importers()

        with self.assertRaises(ImportError):
            import std_msgs.msg.Bool

    def test_double_import_uses_cache(self):
        print_importers()

        import std_msgs.msg as std_msgs

        self.assert_std_message_classes(std_msgs.Bool, std_msgs.Header)

        import std_msgs.msg as std_msgs2

        self.assertTrue(std_msgs == std_msgs2)


class TestImportSrv(BaseSrvTestCase):

    ros_comm_msgs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rosdeps', 'ros_comm_msgs')
    # For dependencies
    rosdeps_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rosdeps')

    rosimporter = rosimport.RosImporter()
    @classmethod
    def setUpClass(cls):
        # This is used for message definitions, not for python code
        site.addsitedir(cls.rosdeps_path)
        site.addsitedir(cls.ros_comm_msgs_path)
        cls.rosimporter.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.rosimporter.__exit__(None, None, None)

    def test_import_absolute_srv(self):
        print_importers()

        # Verify that files exists and are importable
        import std_srvs.srv as std_srvs

        print_importers_of(std_srvs)

        self.assert_std_service_classes(std_srvs.SetBool, std_srvs.SetBoolRequest, std_srvs.SetBoolResponse)

    def test_import_class_from_absolute_srv(self):
        """Verify that"""
        print_importers()

        # Verify that files exists and are importable
        from std_srvs.srv import SetBool, SetBoolRequest, SetBoolResponse

        self.assert_std_service_classes(SetBool, SetBoolRequest, SetBoolResponse)

    def test_import_relative_srv(self):
        """Verify that package is importable relatively"""
        print_importers()

        from . import srv as test_srvs

        print_importers_of(test_srvs)

        # importing this after to test implicit dependency import
        from . import msg as test_msgs

        print_importers_of(test_msgs)

        self.assert_test_service_classes(test_srvs.TestSrv, test_srvs.TestSrvRequest, test_srvs.TestSrvResponse,
                                         test_srvs.TestSrvDeps, test_srvs.TestSrvDepsRequest, test_srvs.TestSrvDepsResponse,
                                         test_msgs.TestRosMsgDeps, test_msgs.TestRosMsg)

    def test_import_relative_srv_from_absolute(self):
        """Verify that package is importable relatively"""
        print_importers()

        import test_rosimport.srv as test_srvs

        print_importers_of(test_srvs)

        import test_rosimport.msg as test_msgs

        print_importers_of(test_msgs)

        self.assert_test_service_classes(test_srvs.TestSrv, test_srvs.TestSrvRequest, test_srvs.TestSrvResponse,
                                         test_srvs.TestSrvDeps, test_srvs.TestSrvDepsRequest, test_srvs.TestSrvDepsResponse,
                                         test_msgs.TestRosMsgDeps, test_msgs.TestRosMsg)

    def test_import_class_from_relative_srv(self):
        """Verify that message class is importable relatively"""
        print_importers()

        from .srv import TestSrv, TestSrvRequest, TestSrvResponse, TestSrvDeps, TestSrvDepsRequest, TestSrvDepsResponse
        # importing message dependencies after services to verify they are transitively already imported when needed.
        from .msg import TestRosMsgDeps, TestRosMsg

        self.assert_test_service_classes(TestSrv, TestSrvRequest, TestSrvResponse,
                                         TestSrvDeps, TestSrvDepsRequest, TestSrvDepsResponse,
                                         TestRosMsgDeps, TestRosMsg)

    def test_import_absolute_class_raises(self):
        print_importers()

        with self.assertRaises(ImportError):
            import std_srvs.srv.SetBool

    def test_double_import_uses_cache(self):    #
        print_importers()
        # Verify that files exists and are importable
        import std_srvs.srv as std_srvs

        self.assert_std_service_classes(std_srvs.SetBool, std_srvs.SetBoolRequest, std_srvs.SetBoolResponse)

        import std_srvs.srv as std_srvs2

        self.assertTrue(std_srvs == std_srvs2)

if __name__ == '__main__':
    import pytest
    pytest.main(['-s', '-x', __file__, '--boxed'])
