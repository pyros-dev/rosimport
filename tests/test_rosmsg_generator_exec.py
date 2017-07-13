from __future__ import absolute_import, division, print_function

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

from rosimport import generate_rosdefs_py, activate_hook_for, deactivate_hook_for

if (2, 7) <= sys.version_info < (3, 4):
    import filefinder2
    filefinder2.activate()

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

        # The package was still not imported yet
        assert 'test_gen_srvs_deps' not in sys.modules

        # generating message class
        sitedir, generated_msg, _ = generate_rosdefs_py(
            [os.path.join(os.path.dirname(__file__), 'msg', 'TestMsg.msg')],
            package='test_gen_msgs',
        )

        # Python code was generated properly
        assert os.path.exists(os.path.join(sitedir, 'test_gen_msgs', 'msg'))
        assert os.path.exists(os.path.join(sitedir, 'test_gen_msgs', 'msg', '__init__.py'))
        assert os.path.exists(os.path.join(sitedir, 'test_gen_msgs', 'msg', '_TestMsg.py'))

        # The package was still not imported yet
        assert 'test_gen_msgs' not in sys.modules

        # Verify that files exists and are importable
        for m in [generated_msg]:
            # modules are generated where the file is launched
            gen_file = os.path.join(sitedir, *m.split("."))
            assert os.path.exists(gen_file + '.py') or os.path.exists(os.path.join(gen_file, '__init__.py'))

            msgs_mod = importlib.import_module(m)
            assert msgs_mod is not None
            assert hasattr(msgs_mod, 'TestMsg')
            assert msgs_mod.TestMsg._type == 'test_gen_msgs/TestMsg'

    def test_generate_srvpkg_usable(self):
        """ Testing our generated srv package is importable.
        Note this test require filefinder2 on python2 for passing."""

        # The package was still not imported yet
        assert 'test_gen_srvs' not in sys.modules

        # generating message class
        sitedir, _, generated_srv = generate_rosdefs_py(
            [os.path.join(os.path.dirname(__file__), 'srv', 'TestSrv.srv')],
            package='test_gen_srvs',
        )

        # Python code was generated properly
        assert os.path.exists(os.path.join(sitedir, 'test_gen_srvs', 'srv'))
        assert os.path.exists(os.path.join(sitedir, 'test_gen_srvs', 'srv', '__init__.py'))
        assert os.path.exists(os.path.join(sitedir, 'test_gen_srvs', 'srv', '_TestSrv.py'))

        # The package was still not imported yet
        assert 'test_gen_srvs' not in sys.modules

        # Verify that files exists and are importable
        for s in [generated_srv]:
            # modules are generated where the file is launched
            gen_file = os.path.join(sitedir, *s.split("."))
            assert os.path.exists(gen_file + '.py') or os.path.exists(os.path.join(gen_file, '__init__.py'))

            msgs_mod = importlib.import_module(s)
            assert msgs_mod is not None
            assert hasattr(msgs_mod, 'TestSrv')
            assert msgs_mod.TestSrv._type == 'test_gen_srvs/TestSrv'

            assert hasattr(msgs_mod, 'TestSrvRequest')
            assert msgs_mod.TestSrvRequest._type == 'test_gen_srvs/TestSrvRequest'

            assert hasattr(msgs_mod, 'TestSrvResponse')
            assert msgs_mod.TestSrvResponse._type == 'test_gen_srvs/TestSrvResponse'


class TestGenerateWithDeps(unittest.TestCase):

    rosdeps_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rosdeps')

    @classmethod
    def setUpClass(cls):
        activate_hook_for(cls.rosdeps_path)

    @classmethod
    def tearDownClass(cls):
        deactivate_hook_for(cls.rosdeps_path)

    def test_generate_msgpkg_deps_usable(self):
        """ Testing our generated msg package is importable.
        Note this test require filefinder2 on python2 for passing.
        We also depend on import feature here, since we need a message module
        to be able to import from another message module for dependencies,
        so the generation of the message cannot be independent from the import system."""

        assert 'test_gen_msgs_deps' not in sys.modules

        # generating message class
        sitedir, generated_msg, _ = generate_rosdefs_py(
            [
                # Dependencies first !
                # Import system (and not generator) needs to take care of generating all rosdef python code
                # from one ros package at the same time, to avoid issues with dependencies
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'msg', 'TestRosMsg.msg'),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'msg', 'TestRosMsgDeps.msg'),
                os.path.join(os.path.dirname(__file__), 'msg', 'TestMsgDeps.msg'),
            ],
            package='test_gen_msgs_deps',  # Note we need a different name to avoid being messed up with modules cache
        )

        # Python code was generated properly
        assert os.path.exists(os.path.join(sitedir, 'test_gen_msgs_deps', 'msg'))
        assert os.path.exists(os.path.join(sitedir, 'test_gen_msgs_deps', 'msg', '__init__.py'))
        assert os.path.exists(os.path.join(sitedir, 'test_gen_msgs_deps', 'msg', '_TestRosMsg.py'))
        assert os.path.exists(os.path.join(sitedir, 'test_gen_msgs_deps', 'msg', '_TestRosMsgDeps.py'))
        assert os.path.exists(os.path.join(sitedir, 'test_gen_msgs_deps', 'msg', '_TestMsgDeps.py'))

        # The package was still not imported yet
        assert 'test_gen_msgs_deps' not in sys.modules

        # Verify that files exists and are importable
        for m in [generated_msg]:
            # modules are generated where the file is launched
            gen_file = os.path.join(sitedir, *m.split("."))
            assert os.path.exists(gen_file + '.py') or os.path.exists(os.path.join(gen_file, '__init__.py'))

            msgs_mod = importlib.import_module(m)
            assert msgs_mod is not None
            assert hasattr(msgs_mod, 'TestMsgDeps')
            assert msgs_mod.TestMsgDeps._type == 'test_gen_msgs_deps/TestMsgDeps'

    def test_generate_srvpkg_deps_usable(self):
        """ Testing our generated srv package is importable.
        Note this test require filefinder2 on python2 for passing."""

        # the service was not imported yet
        assert 'test_gen_srvs_deps' not in sys.modules

        # generating message dependencies
        sitedir, generated_msg, generated_srv = generate_rosdefs_py(
            [
                # Dependencies first !
                # Import system (and not generator) needs to take care of generating all rosdef python code
                # from one ros package at the same time, to avoid issues with dependencies
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'msg', 'TestRosMsg.msg'),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'msg', 'TestRosMsgDeps.msg'),
                os.path.join(os.path.dirname(__file__), 'srv', 'TestSrvDeps.srv'),
            ],
            package='test_gen_srvs_deps',  # Note we need a different name to avoid being messed up with modules cache
        )

        # Python code was generated properly
        assert os.path.exists(os.path.join(sitedir, 'test_gen_srvs_deps', 'msg'))
        assert os.path.exists(os.path.join(sitedir, 'test_gen_srvs_deps', 'msg', '__init__.py'))
        assert os.path.exists(os.path.join(sitedir, 'test_gen_srvs_deps', 'msg', '_TestRosMsg.py'))
        assert os.path.exists(os.path.join(sitedir, 'test_gen_srvs_deps', 'msg', '_TestRosMsgDeps.py'))
        assert os.path.exists(os.path.join(sitedir, 'test_gen_srvs_deps', 'srv', '__init__.py'))
        assert os.path.exists(os.path.join(sitedir, 'test_gen_srvs_deps', 'srv', '_TestSrvDeps.py'))

        # The package was still not imported yet
        assert 'test_gen_srvs_deps' not in sys.modules

        # Verify that files exists and are importable
        for s in [generated_srv]:
            # modules are generated where the file is launched
            gen_file = os.path.join(sitedir, *s.split("."))
            assert os.path.exists(gen_file + '.py') or os.path.exists(os.path.join(gen_file, '__init__.py'))

            # This should transitively import generate_msg module
            srvs_mod = importlib.import_module(s)
            assert srvs_mod is not None
            assert hasattr(srvs_mod, 'TestSrvDeps')
            assert srvs_mod.TestSrvDeps._type == 'test_gen_srvs_deps/TestSrvDeps'

            assert hasattr(srvs_mod, 'TestSrvDepsRequest')
            assert srvs_mod.TestSrvDepsRequest._type == 'test_gen_srvs_deps/TestSrvDepsRequest'

            assert hasattr(srvs_mod, 'TestSrvDepsResponse')
            assert srvs_mod.TestSrvDepsResponse._type == 'test_gen_srvs_deps/TestSrvDepsResponse'


