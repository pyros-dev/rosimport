from __future__ import absolute_import


# # This is useful only if we need relative imports. Ref : http://stackoverflow.com/a/28154841/4006172
# # declaring __package__ if needed (this module is run individually)
# if __package__ is None and not __name__.startswith('pyros_msgs.importer.'):
#     import os
#     import sys
#     # from pathlib2 import Path
#     # top = Path(__file__).resolve().parents[2]
#     # Or
#     from os.path import abspath, dirname
#     top = abspath(__file__)
#     for _ in range(4):
#          top = dirname(top)
#
#     if sys.path[0] == os.path.dirname(__file__):
#         sys.path[0] = str(
#             top)  # we replace first path in list (current module dir path) by the path of the package.
#         # this avoid unintentional relative import (even without point notation).
#     else:  # not sure in which case this could happen, but just in case we don't want to break stuff
#         sys.path.append(str(top))
#
#     if __name__ == '__main__':
#         __name__ = '__init__'
#
#     __package__ = 'pyros_msgs.importer'
#     # Note we do NOT want to import everything in pyros_msgs in this case


from .rosmsg_generator import (
    MsgDependencyNotFound,
    generate_msgsrv_nspkg
)

__all__ = [
    'MsgDependencyNotFound',
    'generate_msgsrv_nspkg',
]
