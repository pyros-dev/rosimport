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


def get_rospathfinder_index_in_meta_hooks():
    return sys.meta_path.index(ROSPathFinder)


def get_rosdirectoryfinder_index_in_path_hooks():
    return sys.path_hooks.index(ros_path_hook)


def activate():
    """Install the path-based import components."""
    # We should plug filefinder first to avoid plugging ROSDirectoryFinder, when it is not a ROS thing...

    filefinder2.activate()

    if ros_path_hook not in sys.path_hooks:
        # We need to be before FileFinder to be able to find our '.msg' and '.srv' files without making a namespace package
        # Note this must be early in the path_hook list, since we change the logic
        # and a namespace package becomes a ros importable package.
        sys.path_hooks.insert(filefinder2.get_filefinder_index_in_path_hooks(), ros_path_hook)

    if ROSPathFinder not in sys.meta_path:
        # adding metahook, before the usual pathfinder, to avoid interferences with python namespace mechanism...
        sys.meta_path.insert(filefinder2.get_pathfinder_index_in_meta_hooks(), ROSPathFinder)

    # Resetting sys.path_importer_cache
    # to support the case where we have an implicit (msg/srv) package inside an already loaded package,
    # since we need to replace the default importer.
    sys.path_importer_cache.clear()


def deactivate():
    # CAREFUL : Even though we remove the path from sys.path,
    # initialized finders will remain in sys.path_importer_cache

    # removing metahook
    sys.meta_path.pop(get_rospathfinder_index_in_meta_hooks())
    # removing path_hook
    sys.path_hooks.pop(get_rosdirectoryfinder_index_in_path_hooks())

    filefinder2.deactivate()

    # Resetting sys.path_importer_cache to get rid of previous importers
    sys.path_importer_cache.clear()


__all__ = [
    'MsgDependencyNotFound',
    'generate_msgsrv_nspkg',
    'ROSMsgLoader',
    'ROSSrvLoader',
    'genmsg_py',
    'gensrv_py',
    'activate_hook_for',
    'deactivate_hook_for',
]
