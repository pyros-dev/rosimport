from __future__ import absolute_import, division, print_function

import tempfile
import unittest

"""
Testing executing rosmsg_generator directly (like setup.py would)
"""

import os
import sys
import runpy
import pkg_resources
import importlib
import site

from rosimport import genrosmsg_py, genrossrv_py, activate, deactivate


"""
Test module for generator ONLY.

None of the tests here should trigger the import mechanism.
Yet we are able to load all messages/services definitions in one (python) ros package.

We will keep the import mechanism to solve inter ros-package dependencies,
to avoid having the python import mechanism messing around within one package, for multiple rosdef locations
"""


class TestImportBasicMsg(unittest.TestCase):

    def test_generate_msgpkg_usable(self):
        """ Testing our generated msg package is importable.
        Note this test require filefinder2 on python2 for passing."""

        tmpsitedir = tempfile.mkdtemp('rosimport_tests_site')

        # generating message class
        sitedir, generated_msg_code = genrosmsg_py(
            [os.path.join(os.path.dirname(__file__), 'msg', 'TestMsg.msg')],
            package='test_gen_msgs',
            sitedir=tmpsitedir
        )

        assert sitedir == tmpsitedir
        assert generated_msg_code == os.path.join(sitedir, 'test_gen_msgs', 'msg', '__init__.py')

        # Python code was generated properly
        assert os.path.exists(os.path.join(sitedir, 'test_gen_msgs', 'msg')), os.path.join(sitedir, 'test_gen_msgs', 'msg')
        assert os.path.exists(os.path.join(sitedir, 'test_gen_msgs', 'msg', '__init__.py')), os.path.join(sitedir, 'test_gen_msgs', 'msg', '__init__.py')
        assert os.path.exists(os.path.join(sitedir, 'test_gen_msgs', 'msg', '_TestMsg.py')), os.path.join(sitedir, 'test_gen_msgs', 'msg', '_TestMsg.py')

        # TODO : test the most basic way to import
        # msgs_mod = load_from_path('subtest_gen_msgs.subtests', generated_msg_code)
        # assert msgs_mod is not None
        # assert hasattr(msgs_mod, 'TestMsg')
        # assert msgs_mod.TestMsg._type == 'subtest_gen_msgs/TestMsg'

    def test_generate_srvpkg_usable(self):
        """ Testing our generated srv package is importable.
        Note this test require filefinder2 on python2 for passing."""

        tmpsitedir = tempfile.mkdtemp('rosimport_tests_site')

        # generating message class
        sitedir, generated_srv_code = genrossrv_py(
            [os.path.join(os.path.dirname(__file__), 'srv', 'TestSrv.srv')],
            package='test_gen_srvs',
            sitedir=tmpsitedir
        )

        assert sitedir == tmpsitedir
        assert generated_srv_code == os.path.join(sitedir, 'test_gen_srvs', 'srv', '__init__.py')

        # Python code was generated properly
        assert os.path.exists(os.path.join(sitedir, 'test_gen_srvs', 'srv')), os.path.join(sitedir, 'test_gen_srvs', 'srv')
        assert os.path.exists(os.path.join(sitedir, 'test_gen_srvs', 'srv', '__init__.py')), os.path.join(sitedir, 'test_gen_srvs', 'srv', '__init__.py')
        assert os.path.exists(os.path.join(sitedir, 'test_gen_srvs', 'srv', '_TestSrv.py')), os.path.join(sitedir, 'test_gen_srvs', 'srv', '_TestSrv.py')

        # TODO : test the most basic way to import
        # subsrvs_mod = load_from_path('subtest_gen_srvs.subtests', generated_srv_code)
        # assert subsrvs_mod is not None
        # assert hasattr(subsrvs_mod, 'SubTestSrv')
        # assert subsrvs_mod.SubTestSrv._type == 'subtest_gen_srvs/SubTestSrv'
        #
        # assert hasattr(subsrvs_mod, 'SubTestSrvRequest')
        # assert subsrvs_mod.SubTestSrvRequest._type == 'subtest_gen_srvs/SubTestSrvRequest'
        #
        # assert hasattr(subsrvs_mod, 'SubTestSrvResponse')
        # assert subsrvs_mod.SubTestSrvResponse._type == 'subtest_gen_srvs/SubTestSrvResponse'


class TestGenerateWithDeps(unittest.TestCase):

    def test_generate_msgpkg_deps_usable(self):
        """ Testing our generated msg package is importable.
        Note this test require filefinder2 on python2 for passing.
        We also depend on import feature here, since we need a message module
        to be able to import from another message module for dependencies,
        so the generation of the message cannot be independent from the import system."""

        tmpsitedir = tempfile.mkdtemp('rosimport_tests_site')

        # generating message class, ROS and root python all at once !
        sitedir, generated_msg_code = genrosmsg_py(
            [
                # Dependencies first !
                # Import system (and not generator) needs to take care of generating all rosdef python code
                # from one ros package at the same time, to avoid issues with dependencies
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'msg', 'TestRosMsg.msg'),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'msg', 'TestRosMsgDeps.msg'),
                os.path.join(os.path.dirname(__file__), 'msg', 'TestMsgDeps.msg'),
            ],
            package='test_gen_msgs_deps',  # Note we need a different name to avoid being messed up with modules cache
            sitedir=tmpsitedir
        )

        assert sitedir == tmpsitedir
        assert generated_msg_code == os.path.join(sitedir, 'test_gen_msgs_deps', 'msg', '__init__.py')

        # Python code was generated properly
        assert os.path.exists(os.path.join(sitedir, 'test_gen_msgs_deps', 'msg')), os.path.join(sitedir, 'test_gen_msgs_deps', 'msg')
        assert os.path.exists(os.path.join(sitedir, 'test_gen_msgs_deps', 'msg', '__init__.py')), os.path.join(sitedir, 'test_gen_msgs_deps', 'msg', '__init__.py')
        assert os.path.exists(os.path.join(sitedir, 'test_gen_msgs_deps', 'msg', '_TestRosMsg.py')), os.path.join(sitedir, 'test_gen_msgs_deps', 'msg', '_TestRosMsg.py')
        assert os.path.exists(os.path.join(sitedir, 'test_gen_msgs_deps', 'msg', '_TestRosMsgDeps.py')), os.path.join(sitedir, 'test_gen_msgs_deps', 'msg', '_TestRosMsgDeps.py')
        assert os.path.exists(os.path.join(sitedir, 'test_gen_msgs_deps', 'msg', '_TestMsgDeps.py')), os.path.join(sitedir, 'test_gen_msgs_deps', 'msg', '_TestMsgDeps.py')

        # TODO : test the most basic way to import
        # msgdeps_mod = load_from_path('subtest_gen_msgs_deps', generated_msg_code)
        # assert msgdeps_mod is not None
        # assert hasattr(msgdeps_mod, 'TestRosMsg')
        # assert msgdeps_mod.TestRosMsg._type == 'test_gen_msgs/TestRosMsg'
        # assert hasattr(msgdeps_mod, 'TestRosMsgDeps')
        # assert msgdeps_mod.TestRosMsgDeps._type == 'test_gen_msgs/TestRosMsgDeps'
        #
        # msgs_mod = load_from_path('subtest_gen_msgs_deps.subtests', generated_submsg_code)
        # assert msgs_mod is not None
        # assert hasattr(msgs_mod, 'SubTestMsgDeps')
        # assert msgs_mod.SubTestMsgDeps._type == 'subtest_gen_srvs/SubTestMsgDeps'

    def test_generate_srvpkg_deps_usable(self):
        """ Testing our generated srv package is importable.
        Note this test require filefinder2 on python2 for passing."""

        # generating message dependencies
        search_path = {}  # to accumulate generated modules
        sitedir_deps, generated_msg_code = genrosmsg_py(
            [
                # Dependencies first !
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'msg', 'TestRosMsg.msg'),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'msg', 'TestRosMsgDeps.msg'),
            ],
            package='test_gen_srvs_deps',
            sitedir=tempfile.mkdtemp('rosimport_tests_site'),
            search_path=search_path
        )

        # generating message dependencies
        sitedir, generated_srv_code = genrossrv_py(
            [
                os.path.join(os.path.dirname(__file__), 'srv', 'TestSrvDeps.srv'),
            ],
            package='test_gen_srvs_deps',
            sitedir=sitedir_deps,  # we reuse the previous site dir to make sure we end up in the same directory
            search_path=search_path
        )

        assert sitedir == sitedir_deps
        assert generated_msg_code == os.path.join(sitedir, 'test_gen_srvs_deps', 'msg', '__init__.py')
        assert generated_srv_code == os.path.join(sitedir, 'test_gen_srvs_deps', 'srv', '__init__.py')

        # Python code was generated properly
        assert os.path.exists(os.path.join(sitedir, 'test_gen_srvs_deps', 'msg')), os.path.join(sitedir, 'test_gen_srvs_deps', 'msg')
        assert os.path.exists(os.path.join(sitedir, 'test_gen_srvs_deps', 'msg', '__init__.py')), os.path.join(sitedir, 'test_gen_srvs_deps', 'msg', '__init__.py')
        assert os.path.exists(os.path.join(sitedir, 'test_gen_srvs_deps', 'msg', '_TestRosMsg.py')), os.path.join(sitedir, 'test_gen_srvs_deps', 'msg', '_TestRosMsg.py')
        assert os.path.exists(os.path.join(sitedir, 'test_gen_srvs_deps', 'msg', '_TestRosMsgDeps.py')), os.path.join(sitedir, 'test_gen_srvs_deps', 'msg', '_TestRosMsgDeps.py')
        assert os.path.exists(os.path.join(sitedir, 'test_gen_srvs_deps', 'srv', '__init__.py')), os.path.join(sitedir, 'test_gen_srvs_deps', 'srv', '__init__.py')
        assert os.path.exists(os.path.join(sitedir, 'test_gen_srvs_deps', 'srv', '_TestSrvDeps.py')), os.path.join(sitedir, 'test_gen_srvs_deps', 'srv', '_TestSrvDeps.py')

        # TODO : test the most basic way to import
        # msgdeps_mod = load_from_path('subtest_gen_msgs_deps', generated_msg_code)
        # assert msgdeps_mod is not None
        # assert hasattr(msgdeps_mod, 'TestRosMsg')
        # assert msgdeps_mod.TestRosMsg._type == 'test_gen_msgs/TestRosMsg'
        # assert hasattr(msgdeps_mod, 'TestRosMsgDeps')
        # assert msgdeps_mod.TestRosMsgDeps._type == 'test_gen_msgs/TestRosMsgDeps'
        #
        # subsrvs_mod = load_from_path('subtest_gen_srvs.subtests', generated_srv_code)
        # assert subsrvs_mod is not None
        # assert hasattr(subsrvs_mod, 'SubTestSrv')
        # assert subsrvs_mod.SubTestSrv._type == 'subtest_gen_srvs/SubTestSrv'
        #
        # assert hasattr(subsrvs_mod, 'SubTestSrvRequest')
        # assert subsrvs_mod.SubTestSrvRequest._type == 'subtest_gen_srvs/SubTestSrvRequest'
        #
        # assert hasattr(subsrvs_mod, 'SubTestSrvResponse')
        # assert subsrvs_mod.SubTestSrvResponse._type == 'subtest_gen_srvs/SubTestSrvResponse'


