from __future__ import absolute_import, print_function

import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))


def test_ros_msg_patch():

    from provider.msg import TestRosMsgPatch

    msg = TestRosMsgPatch(7)
    assert msg.test_ros_int8 == 42

