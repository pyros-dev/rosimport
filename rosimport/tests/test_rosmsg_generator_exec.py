from __future__ import absolute_import, division, print_function

"""
Testing executing rosmsg_generator directly (like setup.py would)
"""

import os
import runpy

# Ref : http://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
# Including generator module directly from code to be able to generate our message classes
# import imp
# rosmsg_generator = imp.load_source('rosmsg_generator', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rosmsg_generator.py'))
from rosimport import generate_msgsrv_nspkg, import_msgsrv

def test_generate_msgsrv_nspkg_usable():
    # generating message class
    sitedir, generated_msg, generated_srv = generate_msgsrv_nspkg(
        [os.path.join(os.path.dirname(__file__), 'msg', 'TestMsg.msg')],
        package='test_gen_msgs',
        ns_pkg=True,
    )

    # Verify that files exists and are importable
    for m in [generated_msg, generated_srv]:
        # modules are generated where the file is launched
        gen_file = os.path.join(sitedir, *m.split("."))
        assert os.path.exists(gen_file + '.py') or os.path.exists(os.path.join(gen_file, '__init__.py'))

        msg_mod, srv_mod = import_msgsrv(sitedir, generated_msg, generated_srv)

        assert msg_mod is not None
        assert srv_mod is not None

# def test_generate_msgsrv_samepkg_usable():
#     # generating message class
#     sitedir, generated_msg, generated_srv = rosmsg_generator.generate_msgsrv_nspkg(
#         [os.path.join(os.path.dirname(__file__), 'msg', 'TestMsg.msg')],
#         package='test_gen_msgs',
#         ns_pkg=True,
#     )
#
#     # Verify that files exists and are importable
#     for m in [generated_msg, generated_srv]:
#         # modules are generated where the file is launched
#         gen_file = os.path.join(sitedir, *m.split("."))
#         assert os.path.exists(gen_file + '.py') or os.path.exists(os.path.join(gen_file, '__init__.py'))
#
#         msg_mod, srv_mod = rosmsg_generator.import_msgsrv(sitedir, generated_msg, generated_srv)
#
#         assert msg_mod is not None
#         assert srv_mod is not None

def test_generate_msgsrv_genpkg_usable():
    # generating message class
    sitedir, generated_msg, generated_srv = generate_msgsrv_nspkg(
        [os.path.join(os.path.dirname(__file__), 'msg', 'TestMsg.msg')],
        package='test_gen_msgs',
    )

    # Verify that files exists and are importable
    for m in [generated_msg, generated_srv]:
        # modules are generated where the file is launched
        gen_file = os.path.join(sitedir, *m.split("."))
        assert os.path.exists(gen_file + '.py') or os.path.exists(os.path.join(gen_file, '__init__.py'))

        msg_mod, srv_mod = import_msgsrv(sitedir, generated_msg, generated_srv)

        assert msg_mod is not None
        assert srv_mod is not None