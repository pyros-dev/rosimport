from __future__ import absolute_import, division, print_function

import contextlib
import importlib
import site

from pyros_msgs.importer import rosmsg_loader

"""
A module to setup custom importer for .msg and .srv files
Upon import, it will first find the .msg file, then generate the python module for it, then load it.

TODO...
"""

# We need to be extra careful with python versions
# Ref : https://docs.python.org/dev/library/importlib.html#importlib.import_module

# Ref : http://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
# Note : Couldn't find a way to make imp.load_source deal with packages or relative imports (necessary for our generated message classes)
import os
import sys

import logging

from .rosmsg_loader import ROSMsgLoader, ROSSrvLoader

if (2, 7) <= sys.version_info < (3, 4):  # valid until which py3 version ?
    # from .importlib2 import machinery as importlib_machinery
    # from .importlib2 import util as importlib_util
    import pkg_resources  # useful to have empty directory imply namespace package (like for py3)
    import filefinder2
    from ._utils import _ImportError, _verbose_message

    class ROSDirectoryFinder(filefinder2.FileFinder2):
        """Finder to interpret directories as modules, and files as classes"""

        def __init__(self, path, *ros_loader_details):
            """
            Finder to get directories containing ROS message and service files.
            It need to be inserted in sys.path_hooks before FileFinder, since these are Directories but not containing __init__ as per python hardcoded convention.

            Note: There is a matching issue between msg/ folder and msg/My.msg on one side, and package, module, class concepts on the other.
            Since a module is not callable, but we need to call My(data) to build a message class (ROS convention), we match the msg/ folder to a module (and not a package)
            And to keep matching ROS conventions, a directory without __init__ or any message/service file, will become a namespace (sub)package.

            :param path_entry: the msg or srv directory path (no finder should have been instantiated yet)
            """

            ros_loaders = []
            for loader, suffixes in ros_loader_details:
                ros_loaders.extend((suffix, loader) for suffix in suffixes)
            self._ros_loaders = ros_loaders

            # We rely on FileFinder and python loader to deal with our generated code
            super(ROSDirectoryFinder, self).__init__(
                path,
                *filefinder2.get_supported_ns_loaders()
            )

        def __repr__(self):
            return 'ROSDirectoryFinder({!r})'.format(self.path)

        def find_module(self, fullname, path=None):
            path = path or self.path
            tail_module = fullname.rpartition('.')[2]
            loader = None

            base_path = os.path.join(path, tail_module)
            # special code here since FileFinder expect a "__init__" that we don't need for msg or srv.
            if os.path.isdir(base_path):
                loader_class = None
                rosdir = None
                # Figuring out if we should care about this directory at all
                for root, dirs, files in os.walk(base_path):
                    for suffix, loader_cls in self._ros_loaders:
                        if any(f.endswith(suffix) for f in files):
                            loader_class = loader_cls
                            rosdir = root
                if loader_class and rosdir and rosdir == base_path:  # we found a message/service file in the hierarchy, that belong to our module
                    # Generate something !
                    # we are looking for submodules either in generated location (to be able to load generated python files) or in original msg location
                    loader = loader_class(fullname, base_path)  # loader.get_gen_path()])
                    # We DO NOT WANT TO add the generated dir in sys.path to use a python loader
                    # since the plan is to eventually not have to rely on files at all TODO

            # if we couldn't build a loader before we forward the call to our parent FileFinder2 (useful for implicit namespace packages)
            loader = loader or super(ROSDirectoryFinder, self).find_module(fullname, path)
            # If we couldnt find any loader before, we return None
            return loader

        @classmethod
        def path_hook(cls, *loader_details):
            # Same as FileFinder2
            def path_hook_for_ROSDirectoryFinder(path):
                """Path hook for ROSDirectoryFinder."""
                if not os.path.isdir(path):
                    raise _ImportError('only directories are supported', path=path)
                return cls(path, *loader_details)

            return path_hook_for_ROSDirectoryFinder

elif sys.version_info >= (3, 4):  # we do not support 3.2 and 3.3 (maybe we could, if it was worth it...)
    import importlib.machinery as importlib_machinery
    import importlib.util as importlib_util


    class ROSDirectoryFinder(importlib_machinery.FileFinder):
        """Finder to interpret directories as modules, and files as classes"""

        def __init__(self, path, *ros_loader_details):
            """
            Finder to get directories containing ROS message and service files.
            It need to be inserted in sys.path_hooks before FileFinder, since these are Directories but not containing __init__ as per python hardcoded convention.

            Note: There is a matching issue between msg/ folder and msg/My.msg on one side, and package, module, class concepts on the other.
            Since a module is not callable, but we need to call My(data) to build a message class (ROS convention), we match the msg/ folder to a module (and not a package)
            And to keep matching ROS conventions, a directory without __init__ or any message/service file, will become a namespace (sub)package.

            :param path_entry: the msg or srv directory path (no finder should have been instantiated yet)
            """

            ros_loaders = []
            for loader, suffixes in ros_loader_details:
                ros_loaders.extend((suffix, loader) for suffix in suffixes)
            self._ros_loaders = ros_loaders

            # We rely on FileFinder and python loader to deal with our generated code
            super(ROSDirectoryFinder, self).__init__(
                path,
                (importlib_machinery.SourceFileLoader, ['.py']),
                (importlib_machinery.SourcelessFileLoader, ['.pyc']),
            )

        def __repr__(self):
            return 'ROSDirectoryFinder({!r})'.format(self.path)

        def find_spec(self, fullname, target=None):
            """
            Try to find a spec for the specified module.
                    Returns the matching spec, or None if not found.
            :param fullname: the name of the package we are trying to import
            :param target: what we plan to do with it
            :return:
            """

            tail_module = fullname.rpartition('.')[2]
            spec = None
            base_path = os.path.join(self.path, tail_module)

            # special code here since FileFinder expect a "__init__" that we don't need for msg or srv.
            if os.path.isdir(base_path):
                loader_class = None
                rosdir = None
                # Figuring out if we should care about this directory at all
                for root, dirs, files in os.walk(base_path):
                    for suffix, loader_cls in self._ros_loaders:
                        if any(f.endswith(suffix) for f in files):
                            loader_class = loader_cls
                            rosdir = root
                if loader_class and rosdir:
                    if rosdir == base_path:  # we found a message/service file in the hierarchy, that belong to our module
                        # Generate something !
                        loader = loader_class(fullname, base_path)
                        # we are looking for submodules either in generated location (to be able to load generated python files) or in original msg location
                        spec = importlib_util.spec_from_file_location(fullname, base_path, loader=loader, submodule_search_locations=[base_path, loader.get_gen_path()])
                        # We DO NOT WANT TO add the generated dir in sys.path to use a python loader
                        # since the plan is to eventually not have to rely on files at all TODO

            # Relying on FileFinder if we couldn't find any specific directory structure/content
            # It will return a namespace spec if no file can be found
            # or will return a proper loader for already generated python files
            spec = spec or super(ROSDirectoryFinder, self).find_spec(fullname, target=target)
            # we return None if we couldn't find a spec before
            return spec


else:
    raise ImportError("ros_loader : Unsupported python version")


MSG_SUFFIXES = ['.msg']
SRV_SUFFIXES = ['.srv']

def _get_supported_ros_loaders():
    """Returns a list of file-based module loaders.
    Each item is a tuple (loader, suffixes).
    """
    msg = ROSMsgLoader, MSG_SUFFIXES
    srv = ROSSrvLoader, SRV_SUFFIXES
    return [msg, srv]


def _install():
    """Install the path-based import components."""
    supported_loaders = _get_supported_ros_loaders()
    sys.path_hooks.extend([ROSDirectoryFinder.path_hook(*supported_loaders)])
    # TODO : sys.meta_path.append(DistroFinder)



# Useless ?
#_ros_finder_instance_obsolete_python = ROSImportFinder

ros_distro_finder = None

# TODO : metafinder
def activate(rosdistro_path=None, *workspaces):
    global ros_distro_finder
    if rosdistro_path is None:  # autodetect most recent installed distro
        if os.path.exists('/opt/ros/lunar'):
            rosdistro_path = '/opt/ros/lunar'
        elif os.path.exists('/opt/ros/kinetic'):
            rosdistro_path = '/opt/ros/kinetic'
        elif os.path.exists('/opt/ros/jade'):
            rosdistro_path = '/opt/ros/jade'
        elif os.path.exists('/opt/ros/indigo'):
            rosdistro_path = '/opt/ros/indigo'
        else:
            raise ImportError(
                "No ROS distro detected on this system. Please specify the path when calling ROSImportMetaFinder()")

    ros_distro_finder = ROSImportMetaFinder(rosdistro_path, *workspaces)
    sys.meta_path.append(ros_distro_finder)

    #if sys.version_info >= (2, 7, 12):  # TODO : which exact version matters ?

    # We need to be before FileFinder to be able to find our (non .py[c]) files
    # inside, maybe already imported, python packages...
    sys.path_hooks.insert(1, ROSImportFinder)

    # else:  # older (trusty) version
    #     sys.path_hooks.append(_ros_finder_instance_obsolete_python)

    for hook in sys.path_hooks:
        print('Path hook: {}'.format(hook))

    # TODO : mix that with ROS PYTHONPATH shenanigans... to enable the finder only for 'ROS aware' paths
    if paths:
        sys.path.append(*paths)


def deactivate(*paths):
    """ CAREFUL : even if we remove our path_hooks, the created finder are still cached in sys.path_importer_cache."""
    #if sys.version_info >= (2, 7, 12):  # TODO : which exact version matters ?
    sys.path_hooks.remove(ROSImportFinder)
    # else:  # older (trusty) version
    #     sys.path_hooks.remove(_ros_finder_instance_obsolete_python)
    if paths:
        sys.path.remove(*paths)

    sys.meta_path.remove(ros_distro_finder)


@contextlib.contextmanager
def ROSImportContext(*paths):
    activate(*paths)
    yield
    deactivate(*paths)


# TODO : a meta finder could find a full ROS distro...
