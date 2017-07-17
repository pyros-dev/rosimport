from __future__ import absolute_import

import os
import sys

from ._ros_generator import (
    MsgDependencyNotFound,
    genrosmsg_py,
    genrossrv_py,
)

from ._rosdef_loader import ROSMsgLoader, ROSSrvLoader, ros_import_search_path

from ._ros_directory_finder import get_supported_ros_loaders, ROSDirectoryFinder, ROSPathFinder

from ._utils import _verbose_message

ros_path_hook = ROSDirectoryFinder.path_hook(*get_supported_ros_loaders())


def activate():
    """Install the path-based import components."""
    if sys.version_info < (3, 4):
        # We should plug filefinder first to avoid plugging ROSDirectoryFinder, when it is not a ROS thing...
        import filefinder2
        filefinder2.activate()
        PathFinder = filefinder2.NamespaceMetaFinder2

        if ros_path_hook not in sys.path_hooks:
            # We need to be before FileFinder to be able to find our '.msg' and '.srv' files without making a namespace package
            # Note this must be early in the path_hook list, since we change the logic
            # and a namespace package becomes a ros importable package.
            sys.path_hooks.insert(sys.path_hooks.index(filefinder2.path_hook), ros_path_hook)
    else:
        from importlib.machinery import PathFinder

        if ros_path_hook not in sys.path_hooks:
            # Note : On py 3.5 the import system doesnt use hooks after FileFinder since it assumes
            # any directory not containing __init__.py is a namespace package
            sys.path_hooks.insert(1, ros_path_hook)

    if ROSPathFinder not in sys.meta_path:
        # adding metahook, before the usual pathfinder, to avoid interferences with python namespace mechanism...
        sys.meta_path.insert(sys.meta_path.index(PathFinder), ROSPathFinder)

    # Resetting sys.path_importer_cache
    # to support the case where we have an implicit (msg/srv) package inside an already loaded package,
    # since we need to replace the default importer.
    sys.path_importer_cache.clear()


def deactivate():
    # CAREFUL : Even though we remove the path from sys.path,
    # initialized finders will remain in sys.path_importer_cache

    # removing metahook
    sys.meta_path.remove(ROSPathFinder)
    sys.path_hooks.remove(ros_path_hook)

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
