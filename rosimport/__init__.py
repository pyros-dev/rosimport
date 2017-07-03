from __future__ import absolute_import

import sys

from ._ros_generator import (
    MsgDependencyNotFound,
    generate_msgpkg,
    generate_srvpkg,
    genmsg_py,
    gensrv_py,
)

from ._rosdef_loader import ROSMsgLoader, ROSSrvLoader

from ._ros_directory_finder import get_supported_ros_loaders

from ._ros_generator import ros_search_path


# Making the activation explicit for now
def activate_hook_for(*paths):
    """Install the path-based import components."""
    if sys.version_info < (3, 4):
        # We should plug filefinder first to avoid plugging ROSDirectoryFinder, when it is not a ROS thing...
        import filefinder2
        filefinder2.activate()

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

    # Resetting sys.path_importer_cache
    # to support the case where we have an implicit (msg/srv) package inside an already loaded package,
    # since we need to replace the default importer.
    sys.path_importer_cache.clear()

    # TODO : extend with os.environ['ROS_PACKAGE_PATH'] ??
    sys.path.extend(paths)


def deactivate_hook_for(*paths):
    # CAREFUL : Even though we remove the path from sys.path,
    # initialized finders will remain in sys.path_importer_cache
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
