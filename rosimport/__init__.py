from __future__ import absolute_import

import os
import sys

# we rely on filefinder2 as a py2/3 wrapper of importlib
import filefinder2

from ._ros_generator import (
    MsgDependencyNotFound,
    genrosmsg_py,
    genrossrv_py,
)

from ._rosdef_loader import ROSMsgLoader, ROSSrvLoader, ros_import_search_path

from ._ros_directory_finder import get_supported_ros_loaders, ROSDirectoryFinder, ROSPathFinder

from ._utils import _verbose_message

ros_path_hook = ROSDirectoryFinder.path_hook(*get_supported_ros_loaders())


py3importer = filefinder2.Py3Importer()


def activate():
    """Install the path-based import components."""
    # We should plug filefinder first to avoid plugging ROSDirectoryFinder, when it is not a ROS thing...

    py3importer.__enter__()

    if ros_path_hook not in sys.path_hooks:
        # We need to be before FileFinder to be able to find our '.msg' and '.srv' files without making a namespace package
        # Note this must be early in the path_hook list, since we change the logic
        # and a namespace package becomes a ros importable package.
        ff2_idx = sys.path_hooks.index(filefinder2.ff_path_hook)
        sys.path_hooks.insert(ff2_idx, ros_path_hook)

    if ROSPathFinder not in sys.meta_path:
        # adding metahook, before the usual pathfinder, to avoid interferences with python namespace mechanism...
        pf2_idx = sys.meta_path.index(filefinder2.PathFinder)
        sys.meta_path.insert(pf2_idx, ROSPathFinder)


def deactivate():
    # CAREFUL : Even though we remove the path from sys.path,
    # initialized finders will remain in sys.path_importer_cache

    # removing metahook
    ff2_idx = sys.path_hooks.index(ros_path_hook)
    sys.meta_path.pop(ff2_idx)
    # removing path_hook
    pf2_idx = sys.meta_path.index(ROSPathFinder)
    sys.path_hooks.pop(pf2_idx)

    py3importer.__exit__(None, None, None)


__all__ = [
    'MsgDependencyNotFound',
    'ROSMsgLoader',
    'ROSSrvLoader',
]
