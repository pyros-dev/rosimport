from __future__ import absolute_import, division, print_function

import tempfile
import unittest

"""
Testing executing rosmsg_generator directly (like setup.py would use it)
without relying on the import mechanism at all (careful with dependencies)
"""

import os
import sys
import runpy
import pkg_resources
import importlib
import site

from ._utils import load_from_path

from rosimport import genrosmsg_py, genrossrv_py, activate, deactivate


class TestGenerateBasic(unittest.TestCase):

    def test_generate_msgpkg_usable(self):
        """ Testing the generation for a msg package. """

        tmpsitedir = tempfile.mkdtemp('rosimport_subtests_site')

        # generating message class
        sitedir, generated_msg_code = genrosmsg_py(
            [os.path.join(os.path.dirname(__file__), 'msg', 'SubTestMsg.msg')],
            package='subtest_gen_msgs.subtests',
            sitedir=tmpsitedir
        )

        assert sitedir == tmpsitedir
        assert generated_msg_code == os.path.join(sitedir, 'subtest_gen_msgs', 'subtests', 'msg', '__init__.py')

        # Python code was generated properly
        assert os.path.exists(os.path.join(sitedir, 'subtest_gen_msgs', 'subtests', 'msg')), os.path.join(sitedir, 'subtest_gen_msgs', 'subtest', 'msg')
        assert os.path.exists(os.path.join(sitedir, 'subtest_gen_msgs', 'subtests', 'msg', '__init__.py')), os.path.join(sitedir, 'subtest_gen_msgs', 'subtest', 'msg', '__init__.py')
        assert os.path.exists(os.path.join(sitedir, 'subtest_gen_msgs', 'subtests', 'msg', '_SubTestMsg.py')), os.path.join(sitedir, 'subtest_gen_msgs', 'subtest', 'msg', '_SubTestMsg.py')

        # TODO : test the most basic way to import
        # msgs_mod = load_from_path('subtest_gen_msgs.subtests', generated_msg_code)
        # assert msgs_mod is not None
        # assert hasattr(msgs_mod, 'TestMsg')
        # assert msgs_mod.TestMsg._type == 'subtest_gen_msgs/TestMsg'

    def test_generate_srvpkg_usable(self):
        """ Testing our generated srv package is importable.
        Note this test require filefinder2 on python2 for passing."""

        tmpsitedir = tempfile.mkdtemp('rosimport_subtests_site')

        # generating message class
        sitedir, generated_srv_code = genrossrv_py(
            [os.path.join(os.path.dirname(__file__), 'srv', 'SubTestSrv.srv')],
            package='subtest_gen_srvs.subtests',
            sitedir=tmpsitedir
        )

        assert sitedir == tmpsitedir
        assert generated_srv_code == os.path.join(sitedir, 'subtest_gen_srvs', 'subtests', 'srv', '__init__.py')

        # Python code was generated properly
        assert os.path.exists(os.path.join(sitedir, 'subtest_gen_srvs', 'subtests', 'srv')), os.path.join(sitedir, 'subtest_gen_srvs', 'subtest', 'srv')
        assert os.path.exists(os.path.join(sitedir, 'subtest_gen_srvs', 'subtests', 'srv', '__init__.py')), os.path.join(sitedir, 'subtest_gen_srvs', 'subtest', 'srv', '__init__.py')
        assert os.path.exists(os.path.join(sitedir, 'subtest_gen_srvs', 'subtests', 'srv', '_SubTestSrv.py')), os.path.join(sitedir, 'subtest_gen_srvs', 'subtest', 'srv', '_SubTestSrv.py')

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

        tmpsitedir = tempfile.mkdtemp('rosimport_subtests_site')

        # generating message class
        search_path = {}  # to accumulate generated modules
        sitedir_deps, generated_msg_code = genrosmsg_py(
            [
                # Dependencies first !
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'msg', 'TestRosMsg.msg'),
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'msg', 'TestRosMsgDeps.msg'),
            ],
            package='subtest_gen_msgs_deps',
            sitedir=tmpsitedir,
            search_path=search_path,
        )

        sitedir, generated_submsg_code = genrosmsg_py(
            [
                os.path.join(os.path.dirname(__file__), 'msg', 'SubTestMsgDeps.msg'),
            ],
            package='subtest_gen_msgs_deps.subtests',
            sitedir=tmpsitedir,  # we reuse the previous site dir to make sure we end up in the same directory hierarchy
            search_path=search_path,
        )

        assert sitedir == sitedir_deps == tmpsitedir
        assert generated_msg_code == os.path.join(sitedir, 'subtest_gen_msgs_deps', 'msg', '__init__.py')
        assert generated_submsg_code == os.path.join(sitedir, 'subtest_gen_msgs_deps', 'subtests', 'msg', '__init__.py')

        # Python code was generated properly
        assert os.path.exists(os.path.join(sitedir_deps, 'subtest_gen_msgs_deps', 'msg')), os.path.join(sitedir_deps, 'subtest_gen_msgs_deps', 'msg')
        assert os.path.exists(os.path.join(sitedir_deps, 'subtest_gen_msgs_deps', 'msg', '__init__.py')), os.path.join(sitedir_deps, 'subtest_gen_msgs_deps', 'msg', '__init__.py')
        assert os.path.exists(os.path.join(sitedir_deps, 'subtest_gen_msgs_deps', 'msg', '_TestRosMsg.py')), os.path.join(sitedir_deps, 'subtest_gen_msgs_deps', 'msg', '_TestRosMsg.py')
        assert os.path.exists(os.path.join(sitedir_deps, 'subtest_gen_msgs_deps', 'msg', '_TestRosMsgDeps.py')), os.path.join(sitedir_deps, 'subtest_gen_msgs_deps', 'msg', '_TestRosMsgDeps.py')
        assert os.path.exists(os.path.join(sitedir_deps, 'subtest_gen_msgs_deps', 'subtests', 'msg', '__init__.py')), os.path.join(sitedir_deps, 'subtest_gen_msgs_deps', 'subtests', 'msg', '__init__.py')
        assert os.path.exists(os.path.join(sitedir_deps, 'subtest_gen_msgs_deps', 'subtests', 'msg', '_SubTestMsgDeps.py')), os.path.join(sitedir_deps, 'subtest_gen_msgs_deps', 'subtests', 'msg', '_SubTestMsgDeps.py')

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
        Note this test require filefinder2 on python2 for passing.
        We also depend on import feature here, since we need a message module
        to be able to import from another message module for dependencies,
        so the generation of the message cannot be independent from the import system."""

        # generating message dependencies
        search_path = {}  # to accumulate generated modules
        sitedir_deps, generated_msg_code = genrosmsg_py(
            [
                # Dependencies first !
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'msg', 'TestRosMsg.msg'),
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'msg', 'TestRosMsgDeps.msg'),
            ],
            package='subtest_gen_srvs_deps',
            sitedir=tempfile.mkdtemp('rosimport_subtests_site'),
            search_path=search_path
        )

        # generating message dependencies
        sitedir, generated_srv_code = genrossrv_py(
            [
                os.path.join(os.path.dirname(__file__), 'srv', 'SubTestSrvDeps.srv'),
            ],
            package='subtest_gen_srvs_deps.subtests',
            sitedir=sitedir_deps,  # we reuse the previous site dir to make sure we end up in the same directory
            search_path=search_path
        )

        assert sitedir == sitedir_deps
        assert generated_msg_code == os.path.join(sitedir, 'subtest_gen_srvs_deps', 'msg', '__init__.py')
        assert generated_srv_code == os.path.join(sitedir, 'subtest_gen_srvs_deps', 'subtests', 'srv', '__init__.py')

        # Python code was generated properly
        assert os.path.exists(os.path.join(sitedir_deps, 'subtest_gen_srvs_deps', 'msg')), os.path.join(sitedir_deps, 'subtest_gen_srvs_deps', 'msg')
        assert os.path.exists(os.path.join(sitedir_deps, 'subtest_gen_srvs_deps', 'msg', '__init__.py')), os.path.join(sitedir_deps, 'subtest_gen_srvs_deps', 'msg', '__init__.py')
        assert os.path.exists(os.path.join(sitedir_deps, 'subtest_gen_srvs_deps', 'msg', '_TestRosMsg.py')), os.path.join(sitedir_deps, 'subtest_gen_srvs_deps', 'msg', '_TestRosMsg.py')
        assert os.path.exists(os.path.join(sitedir_deps, 'subtest_gen_srvs_deps', 'msg', '_TestRosMsgDeps.py')), os.path.join(sitedir_deps, 'subtest_gen_srvs_deps', 'msg', '_TestRosMsgDeps.py')
        assert os.path.exists(os.path.join(sitedir_deps, 'subtest_gen_srvs_deps', 'subtests', 'srv', '__init__.py')), os.path.join(sitedir_deps, 'subtest_gen_srvs_deps', 'subtests', 'srv', '__init__.py')
        assert os.path.exists(os.path.join(sitedir_deps, 'subtest_gen_srvs_deps', 'subtests', 'srv', '_SubTestSrvDeps.py')), os.path.join(sitedir_deps, 'subtest_gen_srvs_deps', 'subtests', 'srv', '_SubTestSrvDeps.py')

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