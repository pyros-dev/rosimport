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
import site
# Importing importer module
from rosimport import activate, deactivate

# importlib
# https://pymotw.com/3/importlib/index.html
# https://pymotw.com/2/importlib/index.html

#
# Note : we cannot assume anything about import implementation (different python version, different version of pytest)
# => we need to test them all...
#


from ._utils import (
    print_importers,
    BaseMsgTestCase,
    BaseSrvTestCase,
)



class TestImportLibMsg(BaseMsgTestCase):
    rosdeps_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rosdeps')

    @classmethod
    def setUpClass(cls):
        # This is used for message definitions, not for python code
        site.addsitedir(cls.rosdeps_path)
        activate()

    @classmethod
    def tearDownClass(cls):
        deactivate()

    @unittest.skipIf(not hasattr(importlib, '__import__'), reason="importlib does not have attribute __import__")
    def test_importlib_import_absolute_msg(self):
        # Verify that files exists and are importable
        std_msgs = importlib.__import__('std_msgs.msg')
        std_msgs = std_msgs.msg

        self.assert_std_message_classes(std_msgs.Bool, std_msgs.Header)

    @unittest.skipIf(not hasattr(importlib, '__import__'), reason="importlib does not have attribute __import__")
    def test_importlib_import_absolute_class_raises(self):
        with self.assertRaises(ImportError):
            importlib.__import__('std_msgs.msg.Bool')

    # BROKEN 3.4 ?
    @unittest.skipIf(not hasattr(importlib, '__import__'), reason="importlib does not have attribute __import__")
    def test_importlib_import_relative_msg(self):
        # Verify that files exists and are importable
        test_msgs = importlib.__import__('msg', globals=globals(), level=1)

        self.assert_test_message_classes(test_msgs.TestMsg, test_msgs.TestMsgDeps, test_msgs.TestRosMsgDeps, test_msgs.TestRosMsg)

    # BROKEN 3.4 ?
    @unittest.skipIf(not hasattr(importlib, '__import__'), reason="importlib does not have attribute __import__")
    def test_importlib_import_relative_class_raises(self):
        assert __package__
        with self.assertRaises(ImportError):
            importlib.__import__('msg.TestMsg', globals=globals(), level=1)

    # UNTESTED (do we care ?)
    # @unittest.skipIf(not hasattr(importlib, 'find_loader') or not hasattr(importlib, 'load_module'),
    #                  reason="importlib does not have attribute find_loader or load_module")
    # def test_importlib_loadmodule_absolute_msg(self):
    #     # Verify that files exists and are dynamically importable
    #     pkg_list = 'std_msgs.msg'.split('.')[:-1]
    #     mod_list = 'std_msgs.msg'.split('.')[1:]
    #     pkg = None
    #     for pkg_name, mod_name in zip(pkg_list, mod_list):
    #         pkg_loader = importlib.find_loader(pkg_name, pkg.__path__ if pkg else None)
    #         pkg = pkg_loader.load_module(mod_name)
    #
    #     std_msgs = pkg
    #
    #     self.assert_std_message_classes(std_msgs.Bool, std_msgs.Header)
    #
    #     # TODO : implement some differences and check we get them...
    #     if hasattr(importlib, 'reload'):  # recent version of importlib
    #         # attempting to reload
    #         importlib.reload(std_msgs)
    #     else:
    #         pass
    #
    # @unittest.skipIf(not hasattr(importlib, 'find_loader') or not hasattr(importlib, 'load_module'),
    #                  reason="importlib does not have attribute find_loader or load_module")
    # def test_importlib_loadmodule_absolute_class(self):
    #     # Verify that files exists and are dynamically importable
    #     pkg_list = 'std_msgs.msg.Bool'.split('.')[:-1]
    #     mod_list = 'std_msgs.msg.Bool'.split('.')[1:]
    #     pkg = None
    #     for pkg_name, mod_name in zip(pkg_list, mod_list):
    #         pkg_loader = importlib.find_loader(pkg_name, pkg.__path__ if pkg else None)
    #         pkg = pkg_loader.load_module(mod_name)
    #
    #     Bool = pkg
    #
    #     self.assert_std_message_classes(Bool, Header)
    #
    #     # TODO : implement some differences and check we get them...
    #     if hasattr(importlib, 'reload'):  # recent version of importlib
    #         # attempting to reload
    #         importlib.reload(Bool)
    #     else:
    #         pass
    #
    # @unittest.skipIf(not hasattr(importlib, 'find_loader') or not hasattr(importlib, 'load_module'),
    #                  reason="importlib does not have attribute find_loader or load_module")
    # def test_importlib_loadmodule_relative_msg(self):
    #     # Verify that files exists and are dynamically importable
    #     pkg_list = '.msg'.split('.')[:-1]
    #     mod_list = '.msg'.split('.')[1:]
    #     pkg = None
    #     for pkg_name, mod_name in zip(pkg_list, mod_list):
    #         pkg_loader = importlib.find_loader(pkg_name, pkg.__path__ if pkg else None)
    #         pkg = pkg_loader.load_module(mod_name)
    #
    #     test_msgs = pkg
    #
    #     self.assertTrue(test_msgs is not None)
    #     self.assertTrue(test_msgs.TestMsg is not None)
    #     self.assertTrue(callable(test_msgs.TestMsg))
    #     self.assertTrue(test_msgs.TestMsg._type == 'rosimport/TestMsg')  # careful between ros package name and python package name
    #
    #     # use it !
    #     self.assertTrue(test_msgs.TestMsg(test_bool=True, test_string='Test').test_bool)
    #
    #     # TODO : implement some differences and check we get them...
    #     if hasattr(importlib, 'reload'):  # recent version of importlib
    #         # attempting to reload
    #         importlib.reload(test_msgs)
    #     else:
    #         pass
    #
    # @unittest.skipIf(not hasattr(importlib, 'find_loader') or not hasattr(importlib, 'load_module'),
    #                  reason="importlib does not have attribute find_loader or load_module")
    # def test_importlib_loadmodule_relative_class(self):
    #     # Verify that files exists and are dynamically importable
    #     pkg_list = '.msg.TestMsg'.split('.')[:-1]
    #     mod_list = '.msg.TestMsg'.split('.')[1:]
    #     pkg = None
    #     for pkg_name, mod_name in zip(pkg_list, mod_list):
    #         pkg_loader = importlib.find_loader(pkg_name, pkg.__path__ if pkg else None)
    #         pkg = pkg_loader.load_module(mod_name)
    #
    #     TestMsg = pkg
    #
    #     self.assert_test_message_classes(TestMsg, TestMsgDeps, TestRosMsgDeps, TestRosMsg)
    #
    #     # TODO : implement some differences and check we get them...
    #     if hasattr(importlib, 'reload'):  # recent version of importlib
    #         # attempting to reload
    #         importlib.reload(TestMsg)
    #     else:
    #         pass

    # TODO : dynamic using module_spec (python 3.5)

    @unittest.skipIf(not hasattr(importlib, 'import_module'), reason="importlib does not have attribute import_module")
    def test_importlib_importmodule_absolute_msg(self):
        # Verify that files exists and are dynamically importable
        std_msgs = importlib.import_module('std_msgs.msg')

        self.assert_std_message_classes(std_msgs.Bool, std_msgs.Header)

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

        self.assert_test_message_classes(test_msgs.TestMsg, test_msgs.TestMsgDeps, test_msgs.TestRosMsgDeps, test_msgs.TestRosMsg)

        if hasattr(importlib, 'reload'):  # recent version of importlib
            # attempting to reload
            importlib.reload(test_msgs)
        else:
            pass

        assert test_msgs is not None

    @unittest.skipIf(not hasattr(importlib, 'import_module'), reason="importlib does not have attribute import_module")
    def test_importlib_importmodule_relative_msg_from_absolute(self):

        assert __package__
        # Verify that files exists and are dynamically importable
        test_msgs = importlib.import_module('tests.msg')

        self.assert_test_message_classes(test_msgs.TestMsg, test_msgs.TestMsgDeps, test_msgs.TestRosMsgDeps, test_msgs.TestRosMsg)

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


class TestImportLibSrv(BaseSrvTestCase):

    ros_comm_msgs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rosdeps', 'ros_comm_msgs')
    # For dependencies
    rosdeps_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rosdeps')

    @classmethod
    def setUpClass(cls):
        # This is used for message definitions, not for python code
        site.addsitedir(cls.rosdeps_path)
        site.addsitedir(cls.ros_comm_msgs_path)
        activate()

    @classmethod
    def tearDownClass(cls):
        deactivate()

    @unittest.skipIf(not hasattr(importlib, '__import__'), reason="importlib does not have attribute __import__")
    def test_importlib_import_absolute_srv(self):
        # Verify that files exists and are importable
        std_srvs = importlib.__import__('std_srvs.srv')
        std_srvs = std_srvs.srv

        self.assert_std_service_classes(std_srvs.SetBool, std_srvs.SetBoolRequest, std_srvs.SetBoolResponse)

    @unittest.skipIf(not hasattr(importlib, '__import__'), reason="importlib does not have attribute __import__")
    def test_importlib_import_absolute_class_raises(self):
        with self.assertRaises(ImportError):
            importlib.__import__('std_srvs.srv.SetBool')

    # BROKEN 3.4 ?
    @unittest.skipIf(not hasattr(importlib, '__import__'), reason="importlib does not have attribute __import__")
    def test_importlib_import_relative_srv(self):
        # Verify that files exists and are importable
        test_srvs = importlib.__import__('srv', globals=globals(), level=1)
        test_msgs = importlib.__import__('msg', globals=globals(), level=1)

        self.assert_test_service_classes(test_srvs.TestSrv, test_srvs.TestSrvRequest, test_srvs.TestSrvResponse,
                                         test_srvs.TestSrvDeps, test_srvs.TestSrvDepsRequest, test_srvs.TestSrvDepsResponse,
                                         test_msgs.TestRosMsgDeps, test_msgs.TestRosMsg)

    # UNTESTED : do we care ?
    # @unittest.skipIf(not hasattr(importlib, '__import__'), reason="importlib does not have attribute __import__")
    # def test_importlib_import_relative_class_raises(self):
    #     assert __package__
    #     with self.assertRaises(ImportError):
    #         importlib.__import__('srv.SetBool', globals=globals(), level=1)
    #
    # @unittest.skipIf(not hasattr(importlib, 'find_loader') or not hasattr(importlib, 'load_module'),
    #                  reason="importlib does not have attribute find_loader or load_module")
    # def test_importlib_loadmodule_absolute_srv(self):
    #     # Verify that files exists and are dynamically importable
    #     pkg_list = 'std_srvs.srv'.split('.')[:-1]
    #     mod_list = 'std_srvs.srv'.split('.')[1:]
    #     pkg = None
    #     for pkg_name, mod_name in zip(pkg_list, mod_list):
    #         pkg_loader = importlib.find_loader(pkg_name, pkg.__path__ if pkg else None)
    #         pkg = pkg_loader.load_module(mod_name)
    #
    #     std_srvs = pkg
    #
    #     self.assert_std_service_classes(std_srvs.SetBool, std_srvs.SetBoolRequest, std_srvs.SetBoolResponse)
    #
    #     # TODO : implement some differences and check we get them...
    #     if hasattr(importlib, 'reload'):  # recent version of importlib
    #         # attempting to reload
    #         importlib.reload(std_srvs)
    #     else:
    #         pass
    #
    # @unittest.skipIf(not hasattr(importlib, 'find_loader') or not hasattr(importlib, 'load_module'),
    #                  reason="importlib does not have attribute find_loader or load_module")
    # def test_importlib_loadmodule_absolute_class(self):
    #     # Verify that files exists and are dynamically importable
    #     pkg_list = 'std_srvs.srv.SetBool'.split('.')[:-1]
    #     mod_list = 'std_srvs.srv.SetBool'.split('.')[1:]
    #     pkg = None
    #     for pkg_name, mod_name in zip(pkg_list, mod_list):
    #         pkg_loader = importlib.find_loader(pkg_name, pkg.__path__ if pkg else None)
    #         pkg = pkg_loader.load_module(mod_name)
    #
    #     SetBool = pkg
    #
    #     self.assert_test_service_classes(SetBool, SetBoolRequest, SetBoolResponse)
    #
    #     # TODO : implement some differences and check we get them...
    #     if hasattr(importlib, 'reload'):  # recent version of importlib
    #         # attempting to reload
    #         importlib.reload(SetBool)
    #     else:
    #         pass
    #
    # @unittest.skipIf(not hasattr(importlib, 'find_loader') or not hasattr(importlib, 'load_module'),
    #                  reason="importlib does not have attribute find_loader or load_module")
    # def test_importlib_loadmodule_relative_srv(self):
    #     # Verify that files exists and are dynamically importable
    #     pkg_list = '.srv'.split('.')[:-1]
    #     mod_list = '.srv'.split('.')[1:]
    #     pkg = None
    #     for pkg_name, mod_name in zip(pkg_list, mod_list):
    #         pkg_loader = importlib.find_loader(pkg_name, pkg.__path__ if pkg else None)
    #         pkg = pkg_loader.load_module(mod_name)
    #
    #     test_srvs = pkg
    #
    #     self.assert_test_service_classes()
    #
    #     # TODO : implement some differences and check we get them...
    #     if hasattr(importlib, 'reload'):  # recent version of importlib
    #         # attempting to reload
    #         importlib.reload(test_msgs)
    #     else:
    #         pass
    #
    # @unittest.skipIf(not hasattr(importlib, 'find_loader') or not hasattr(importlib, 'load_module'),
    #                  reason="importlib does not have attribute find_loader or load_module")
    # def test_importlib_loadmodule_relative_class(self):
    #     # Verify that files exists and are dynamically importable
    #     pkg_list = '.srv.TestSrv'.split('.')[:-1]
    #     mod_list = '.srv.TestSrv'.split('.')[1:]
    #     pkg = None
    #     for pkg_name, mod_name in zip(pkg_list, mod_list):
    #         pkg_loader = importlib.find_loader(pkg_name, pkg.__path__ if pkg else None)
    #         pkg = pkg_loader.load_module(mod_name)
    #
    #     TestSrv = pkg
    #
    #     self.assert_test_service_classes()
    #
    #     # TODO : implement some differences and check we get them...
    #     if hasattr(importlib, 'reload'):  # recent version of importlib
    #         # attempting to reload
    #         importlib.reload(TestSrv)
    #     else:
    #         pass

    # TODO : dynamic using module_spec (python 3.5)

    @unittest.skipIf(not hasattr(importlib, 'import_module'), reason="importlib does not have attribute import_module")
    def test_importlib_importmodule_absolute_srv(self):
        # Verify that files exists and are dynamically importable
        std_srvs = importlib.import_module('std_srvs.srv')

        self.assert_std_service_classes(std_srvs.SetBool, std_srvs.SetBoolRequest, std_srvs.SetBoolResponse)

        if hasattr(importlib, 'reload'):  # recent version of importlib
            # attempting to reload
            importlib.reload(std_srvs)
        else:
            pass

        assert std_srvs is not None

    @unittest.skipIf(not hasattr(importlib, 'import_module'),
                     reason="importlib does not have attribute import_module")
    def test_importlib_importmodule_absolute_class_raises(self):
        with self.assertRaises(ImportError):
            importlib.import_module('std_srvs.srv.SetBool')

    @unittest.skipIf(not hasattr(importlib, 'import_module'), reason="importlib does not have attribute import_module")
    def test_importlib_importmodule_relative_srv(self):

        assert __package__
        # Verify that files exists and are dynamically importable
        test_srvs = importlib.import_module('.srv', package=__package__)
        test_msgs = importlib.import_module('.msg', package=__package__)

        self.assert_test_service_classes(test_srvs.TestSrv, test_srvs.TestSrvRequest, test_srvs.TestSrvResponse,
                                         test_srvs.TestSrvDeps, test_srvs.TestSrvDepsRequest, test_srvs.TestSrvDepsResponse,
                                         test_msgs.TestRosMsgDeps, test_msgs.TestRosMsg)

        if hasattr(importlib, 'reload'):  # recent version of importlib
            # attempting to reload
            importlib.reload(test_srvs)
        else:
            pass

        assert test_srvs is not None

    @unittest.skipIf(not hasattr(importlib, 'import_module'), reason="importlib does not have attribute import_module")
    def test_importlib_importmodule_relative_srv_from_absolute(self):

        assert __package__
        # Verify that files exists and are dynamically importable
        test_srvs = importlib.import_module('tests.srv')
        test_msgs = importlib.import_module('tests.msg')

        self.assert_test_service_classes(test_srvs.TestSrv, test_srvs.TestSrvRequest, test_srvs.TestSrvResponse,
                                         test_srvs.TestSrvDeps, test_srvs.TestSrvDepsRequest, test_srvs.TestSrvDepsResponse,
                                         test_msgs.TestRosMsgDeps, test_msgs.TestRosMsg)

        if hasattr(importlib, 'reload'):  # recent version of importlib
            # attempting to reload
            importlib.reload(test_srvs)
        else:
            pass

        assert test_srvs is not None

    @unittest.skipIf(not hasattr(importlib, 'import_module'),
                     reason="importlib does not have attribute import_module")
    def test_importlib_importmodule_relative_class_raises(self):

        assert __package__
        with self.assertRaises(ImportError):
            importlib.import_module('.srv.TestSrv', package=__package__)

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




if __name__ == '__main__':
    import pytest
    pytest.main(['-s', '-x', __file__, '--boxed'])
