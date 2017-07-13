from __future__ import absolute_import, division, print_function

import contextlib
import importlib
import site
from collections import OrderedDict

from rosimport import ROSMsgLoader, ROSSrvLoader

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

from ._utils import _ImportError, _verbose_message




if (2, 7) <= sys.version_info < (3, 4):  # valid until which py3 version ?
    import filefinder2
    PathFinder = filefinder2.PathFinder2
    FileFinder = filefinder2.FileFinder2
elif sys.version_info >= (3, 4):  # we do not support 3.2 and 3.3 (unsupported but might work ?)
    import importlib.machinery
    PathFinder = importlib.machinery.PathFinder
    FileFinder = importlib.machinery.FileFinder
else:
    raise ImportError("ros_loader : Unsupported python version")


class ROSPathFinder(PathFinder):
    """
    MetaFinder to handle Finding ROS package directories
    This is needed because python3 namespace package machinary can miss directories that are
    ROS package root directories, containing msg and srv subdirs.
    """

    def __init__(self, *modules):
        """Initialisation of the finder depending on namespaces.
        The issue here is that we do not have enough information at this stage
        to determine which finder will be most appropriate for this path.

        Only after find_module might we known which one should be chosen."""
        self.module_names = modules

    @classmethod
    def find_spec(cls, fullname, path, target=None):
        loader = cls.find_module(fullname, path)
        spec = importlib.util.spec_from_file_location(
            # will extract all useful information from loader
            fullname,
            loader=loader,
        )
        return spec

    @classmethod
    def find_module(cls, fullname, path=None):  # from importlib.PathFinder
        """Try to find the module on sys.path or 'path'
        The search is based on sys.path_hooks and sys.path_importer_cache.
        """
        if path is None:
            path = sys.path
        loader = None
        for entry in path:
            if not isinstance(entry, (str, bytes)):
                continue
            # first we check if the root import is doable with ROS recursively
            rospkg = fullname.partition('.')[0]
            dirlist = entry.split(os.sep)
            if rospkg in dirlist:
                dirlist[:] = dirlist[:dirlist.index(rospkg)+1]

                rootentry = os.path.join(os.sep if dirlist[0] == '' else '', *dirlist)
                rosentry = os.path.dirname(rootentry)

                # we need to keep order here to maintain strict dependency and generation order
                entrymap = [
                    (rospkg + '.msg', rosentry),
                    (rospkg + '.msg', rootentry),
                    (fullname, entry)
                ]

                for n, e in entrymap:
                    finder = cls._path_importer_cache(e)
                    if finder is not None:
                        if n == fullname:
                            loader = finder.find_module(n)
                        else:
                            finder.find_module(n)
            # else:
            # other cases handled later by the default python pathfinder.

        return loader


class ROSDirectoryFinder(FileFinder):
    """Finder to interpret directories as modules, and files as classes"""

    def __init__(self, path, *ros_loader_details):
        """
        Finder to get directories 'msg' & 'srv' containing ROS message and service files.
        It need to be inserted in sys.path_hooks before FileFinder, since these are Directories
        but not containing __init__ as per python (hardcoded) convention.

        Note: There is a matching issue between msg/ folder and msg/My.msg on one side,
         and package, module, class concepts on the other.
        Since a module is not callable, but we need to call My(data) to build a message class (ROS convention),
         we match the msg/ folder to a module (and not a package)
        And to keep matching ROS conventions, a directory without __init__ or any message/service file,
        will become a namespace (sub)package.

        :param path_entry: the msg or srv directory path (no finder should have been instantiated yet)
        """

        ros_loaders = []
        for loader, suffixes in ros_loader_details:
            ros_loaders.extend((suffix, loader) for suffix in suffixes)
        self._ros_loaders = ros_loaders

        # We need to check that we will be able to find a module or package,
        # or raise ImportError to allow other finders to be instantiated for this path.
        # => the logic must correspond to find_module()
        findable = False
        for f in [p for p in os.listdir(path) if os.path.isdir(os.path.join(path,p))]:  # we are only interested in directories
            findable = findable or any(  # we make sure we have at least a directory that :
                    f == l.get_origin_subdir() and  # has the right name and
                    [subf for subf in os.listdir(os.path.join(path, f)) if subf.endswith(s)]
                    # contain at least one file with the right extension
                    for s, l in self._ros_loaders
            )
        # Note that testing for extensions of file in path is already too late here,
        # since we generate the whole directory at one time, and each file is a class (not a module)

        if not findable:
            raise _ImportError(
                "cannot find any matching module based on extensions {0} or origin subdirs {1} ".format(
                    [s for s, _ in self._ros_loaders], [l.get_origin_subdir() for _, l in self._ros_loaders]),
                path=path
            )
            # This is needed to not override default behavior in path where there is NO ROS files/directories.

        self.path = path or '.'

    def __repr__(self):
        return 'ROSDirectoryFinder({!r})'.format(self.path)

    @classmethod
    def path_hook(cls, *loader_details):
        def rosimporter_path_hook(path):
            """Path hook for ROSDirectoryFinder."""
            if not os.path.isdir(path):
                raise _ImportError('only directories are supported', path=path)
            return cls(path, *loader_details)

        return rosimporter_path_hook

    def find_spec(self, fullname, target=None):
        import importlib.util  # called only in python 3, which should have this

        loader = self.find_module(fullname)
        spec = importlib.util.spec_from_file_location(
            # will extract all useful information from loader
            fullname,
            loader=loader,
        )
        return spec

    def find_module(self, fullname, path=None):
        """
        Try to find a spec for the specified module.
                Returns the matching spec, or None if not found.
        :param fullname: the name of the package we are trying to import
        :param target: what we plan to do with it
        :return:
        """

        tail_module = fullname.rpartition('.')[2]
        loader = None
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
                        break  # breaking as soon as we find something interesting
                        # we need to take care of msgs before srvs (because they can be used as dependencies
            if loader_class and rosdir and rosdir == base_path:  # we found a message/service file in the hierarchy, that belong to our module
                # rospackage = fullname.partition('.')[0]
                # # We should reproduce package structure in generated file structure
                # dirlist = base_path.split(os.sep)
                # pkgidx = dirlist[::-1].index(rospackage)
                # # find root package folder
                # pkgrootdir = os.path.join('/' if dirlist[0] == '' else '', *dirlist[:len(dirlist) - pkgidx])

                # # Find the the public ROS interface definition (that we can also depend on)
                # if not os.path.exists(os.path.join(pkgrootdir, 'package.xml')):
                #     public_msg = None
                #     # we try to find a lower 'msg' to use as dependency (only if we are not at the 'package' level, or at root (dirname(d) == d) )
                #     while os.path.dirname(pkgrootdir) != pkgrootdir and not os.path.exists(
                #             os.path.join(pkgrootdir, 'package.xml')):
                #         parentdirmsg = os.path.join(os.path.dirname(pkgrootdir), 'msg')
                #         if os.path.exists(parentdirmsg) and [f for f in os.listdir(parentdirmsg) if f.endswith('.msg')]:
                #             public_msg = parentdirmsg
                #         pkgrootdir = os.path.dirname(pkgrootdir)
                #     # TODO : maybe discover and load all messages at a "closer to root" level in package tree ??
                #     if public_msg:
                #         # we need to load the public interface first (to avoid caching an ungenerated root module)
                #         public_msg_spec = self.build_spec_loader(fullname, base_path, loader_class)


                # we are looking for submodules either in generated location
                # to be able to load generated python files) or in original msg location
                loader = loader_class(fullname, base_path)
                # We DO NOT WANT TO add the generated dir in sys.path to use a python loader
                # since the plan is to eventually not have to rely on files at all TODO

        # we return None if we couldn't build a loader before
        return loader


MSG_SUFFIXES = ['.msg']
SRV_SUFFIXES = ['.srv']


def get_supported_ros_loaders():
    """Returns a list of file-based module loaders.
    Each item is a tuple (loader, suffixes).
    """
    msg = ROSMsgLoader, MSG_SUFFIXES
    srv = ROSSrvLoader, SRV_SUFFIXES
    return [msg, srv]


def _install():
    """Install the path-based import components."""
    supported_loaders = get_supported_ros_loaders()
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
