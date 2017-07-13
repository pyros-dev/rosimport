from __future__ import absolute_import

import os
import sys

from ._ros_generator import (
    MsgDependencyNotFound,
    genrosmsg_py,
    genrossrv_py,
)

from ._rosdef_loader import ROSMsgLoader, ROSSrvLoader, ros_import_search_path

from ._ros_directory_finder import get_supported_ros_loaders

from ._utils import _verbose_message

# Making the activation explicit for now
def activate_hook_for(*paths):
    """Install the path-based import components."""
    if sys.version_info < (3, 4):
        # We should plug filefinder first to avoid plugging ROSDirectoryFinder, when it is not a ROS thing...
        import filefinder2
        filefinder2.activate()

    # TODO : python2 support ??
    from importlib.machinery import PathFinder

    # We need to be before FileFinder to be able to find our '.msg' and '.srv' files without making a namespace package
    supported_loaders = _ros_directory_finder.get_supported_ros_loaders()
    ros_hook = _ros_directory_finder.ROSDirectoryFinder.path_hook(*supported_loaders)
    if sys.version_info < (3, 4):
        # Note this must be early in the list (before filefinder2),
        # since we change the logic regarding what is a package or not
        sys.path_hooks.insert(1, ros_hook)
        # sys.path_hooks.append(ros_hook)
    else:
        # Note this must be early in the path_hook list, since we change the logic
        # and a namespace package becomes a ros importable package.
        # Note : On py 3.5 the import system doesnt use hooks after FileFinder since it assumes
        # any directory not containing __init__.py is a namespace package
        sys.path_hooks.insert(1, ros_hook)
        #sys.path_hooks.append(ros_hook)

    # adding metahook
    sys.meta_path.insert(sys.meta_path.index(PathFinder), _ros_directory_finder.ROSPathFinder)


    # Resetting sys.path_importer_cache
    # to support the case where we have an implicit (msg/srv) package inside an already loaded package,
    # since we need to replace the default importer.
    sys.path_importer_cache.clear()

    for p in paths:
        if not os.path.exists(p):
            _verbose_message("WARNING : p does not exists. Please double check your environment setup...")
    # TODO : extend with os.environ['ROS_PACKAGE_PATH'] ??
    sys.path.extend(paths)


def deactivate_hook_for(*paths):
    # CAREFUL : Even though we remove the path from sys.path,
    # initialized finders will remain in sys.path_importer_cache

    # removing metahook
    sys.meta_path.remove(_ros_directory_finder.ROSPathFinder)

    for p in paths:
        sys.path.remove(p)

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
