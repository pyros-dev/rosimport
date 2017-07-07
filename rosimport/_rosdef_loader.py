from __future__ import absolute_import, division, print_function

import contextlib
import importlib
import site
import tempfile

import shutil


from rosimport import genros_py, ros_search_path

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


def RosLoader(rosdef_extension):
    """
    Function generating ROS loaders.
    This is used to keep .msg and .srv loaders very similar
    """
    if rosdef_extension == '.msg':
        loader_origin_subdir = 'msg'
        loader_file_extension = rosdef_extension
        loader_generated_subdir = 'msg'
    elif rosdef_extension == '.srv':
        loader_origin_subdir = 'srv'
        loader_file_extension = rosdef_extension
        loader_generated_subdir = 'srv'
    else:
        raise RuntimeError("RosLoader for a format {0} other than .msg or .srv is not supported".format(rosdef_extension))

    if (2, 7) <= sys.version_info < (3, 4):  # valid until which py3 version ?
        import filefinder2
        FileLoader = filefinder2.SourceFileLoader2
    elif sys.version_info >= (3, 4):  # we do not support 3.2 and 3.3 (unsupported but might work ?)
        import importlib.machinery
        FileLoader = importlib.machinery.SourceFileLoader
    else:
        raise ImportError("ros_loader : Unsupported python version")

    class ROSDefLoader(FileLoader):
        """
        Python Loader for Rosdef files.
        Note : Only messages at the lowest level of package
               along with package.xml, like for usual ROS message definitions,
               are usable as dependencies of current and other messages.
        """

        def __init__(self, fullname, path):

            self.logger = logging.getLogger(__name__)
            # to normalize input
            path = os.path.normpath(path)

            # Doing this in each loader, in case we are running from different processes,
            # avoiding to reload from same file (especially useful for boxed tests).
            # But deterministic path to avoid regenerating from the same interpreter
            self.rosimport_path = os.path.join(tempfile.gettempdir(), 'rosimport', str(os.getpid()))
            if not os.path.exists(self.rosimport_path):
                os.makedirs(self.rosimport_path)

            self.rospackage = fullname.partition('.')[0]
            self.outdir_pkg = os.path.join(self.rosimport_path, self.rospackage)

            if os.path.isdir(path):
                if path.endswith(loader_origin_subdir) and any([f.endswith(loader_file_extension) for f in os.listdir(path)]):  # if we get a non empty 'msg' folder

                    # The msg/srv subpackage should be generated all at once.
                    # If same package is present with same PID,
                    # it s a full new import in a new process, so we should clean existing code.
                    if os.path.exists(os.path.join(self.outdir_pkg, loader_generated_subdir)):
                        shutil.rmtree(os.path.join(self.outdir_pkg, loader_generated_subdir))

                    # CAREFUL : because of import logic and message generation logic for dependencies,
                    # we should add all rosdefs files that are found in parent directories,
                    # and that are not already in ros_search_path
                    rosdef_files = []
                    ros_pkg = fullname.partition('.')[0]
                    walking_path = path
                    while walking_path != os.path.dirname(walking_path) and not os.path.exists(os.path.join(walking_path, 'package.xml')):
                        walking_path = os.path.dirname(walking_path)
                        if walking_path not in ros_search_path.get(ros_pkg, []):
                            if os.path.exists(os.path.join(walking_path, loader_origin_subdir)):
                                msg_walking_path = os.path.join(walking_path, loader_origin_subdir)
                                rosdef_files += [os.path.join(msg_walking_path, f) for f in os.listdir(msg_walking_path) if f.endswith(loader_file_extension)]

                    # TODO : dynamic in memory generation (we do not need the file ultimately...)
                    self.gen_rosdefs = genros_py(
                        rosdef_files=rosdef_files,  # generate all message's python code at once.
                        package=self.rospackage,
                        outdir_pkg=self.outdir_pkg,
                        # include_path should be automatically taken care of by generator API (+ import mechanism)
                    )
                    init_path = None
                    for pyf in self.gen_rosdefs:
                        if pyf.endswith('__init__.py'):
                            init_path = pyf

                    if not init_path:
                        raise ImportError("__init__.py file not found".format(init_path))
                    if not os.path.exists(init_path):
                        raise ImportError("{0} file not found".format(init_path))

                    # relying on usual source file loader since we have generated normal python code
                    super(ROSDefLoader, self).__init__(fullname, init_path)

        def get_gen_path(self):
            """Returning the generated path matching the import"""
            return os.path.join(self.outdir_pkg, loader_generated_subdir)

        def __repr__(self):
            return "ROSDefLoader/{0}({1}, {2})".format(loader_file_extension, self.name, self.path)

        @staticmethod
        def get_file_extension():
            return loader_file_extension

        @staticmethod
        def get_origin_subdir():
            return loader_origin_subdir

        @staticmethod
        def get_generated_subdir():
            return loader_generated_subdir

    return ROSDefLoader

ROSMsgLoader = RosLoader(rosdef_extension='.msg')
ROSSrvLoader = RosLoader(rosdef_extension='.srv')
