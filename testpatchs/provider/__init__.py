from __future__ import absolute_import, print_function


import rosimport
rosimport.activate()

from .msg import TestRosMsgPatch


def duckpunch(msgmod):

    # a basic init patch overriding args with a constant value
    def init_punch(self, *args, **kwds):
        self.test_ros_int8 = 42

    msgmod.__init__ = init_punch


# alias
patch = duckpunch

duckpunch(TestRosMsgPatch)


msg = {
    'TestRosMsgPatch': TestRosMsgPatch,
}

__all__ = [
    'msg'
]

