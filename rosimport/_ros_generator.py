from __future__ import absolute_import, division, print_function

import os
import sys
import tempfile
import traceback
import importlib

import time

import collections
import pkg_resources

"""
Module that can be used standalone, or as part of the rosimport package

It provides a set of functions to generate your ros messages, even when ROS is not installed on your system.
You might however need to have dependent messages definitions reachable by rospack somewhere.

Note : Generated modules/packages can only be imported once. So it is important to provide an API that : 
- makes it easy to generate the whole module/package at once, since this is our priority
- makes it easy to optionally import the whole generated module/package
- still allows to generate only one module / a part of the whole package, caveats apply / warning added.
"""

try:
    # Using genpy and genmsg directly if ROS has been setup (while using from ROS pkg)
    import genmsg as genmsg
    import genmsg.command_line as genmsg_command_line
    import genpy.generator as genpy_generator
    import genpy.generate_initpy as genpy_generate_initpy

except ImportError:

    # Otherwise we refer to our submodules here (setup.py usecase, or running from tox without site-packages)

    import site
    ros_site_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ros-packages')
    print("Adding site directory {ros_site_dir} to access genpy and genmsg.".format(**locals()))
    site.addsitedir(ros_site_dir)

    import genmsg as genmsg
    import genmsg.command_line as genmsg_command_line
    import genpy.generator as genpy_generator
    import genpy.generate_initpy as genpy_generate_initpy

    # Note we do not want to use pyros_setup here.
    # We do not want to do a full ROS setup, only import specific packages.
    # If needed it should have been done before (loading a parent package).
    # this handle the case where we want to be independent of any underlying ROS system.

# TMP bwcompat
try:
    import genmsg.MSG_DIR as genmsg_MSG_DIR
    import genmsg.SRV_DIR as genmsg_SRV_DIR
except ImportError:  # bwcompat
    genmsg_MSG_DIR = 'msg'
    genmsg_SRV_DIR = 'srv'


class MsgDependencyNotFound(Exception):
    pass


class PkgAlreadyExists(Exception):
    pass


# Class to allow dynamic search of packages
class RosSearchPath(dict):
    def __init__(self, **ros_package_paths):
        # we use the default ROS_PACKAGE_PATH if setup in environment
        package_paths = {}  # TODO : os.environ.get('ROS_PACKAGE_PATH', {})
        # we add any extra path
        package_paths.update(ros_package_paths)
        super(RosSearchPath, self).__init__(package_paths)

    def try_import(self, item):
        try:
            mod = importlib.import_module(item)
            # import succeeded : we should get the namespace path that has '/msg'
            # and add it to the list of paths to avoid going through this all over again...
            for p in mod.__path__:
                # Note we want dependencies here. dependencies are ALWAYS '.msg' files in 'msg' directory.
                msg_path = os.path.join(p, genmsg_MSG_DIR)
                # We add a path only if we can find the 'mg' directory
                self[item] = self.get(item, []) + ([msg_path] if os.path.exists(msg_path) else [])
            return mod
        except ImportError:
            # import failed
            return None

    def __contains__(self, item):
        """ True if D has a key k, else False. """
        has = super(RosSearchPath, self).__contains__(item)
        if not has:  # attempt importing. solving ROS path setup problem with python import paths setup.
            self.try_import(item)
        # try again (might work now)
        return super(RosSearchPath, self).__contains__(item)

    def __getitem__(self, item):
        """ x.__getitem__(y) <==> x[y] """
        got = super(RosSearchPath, self).get(item)
        if got is None:
            # attempt discovery by relying on python core import feature.
            self.try_import(item)
        return super(RosSearchPath, self).get(item)

# singleton instance, to keep used ros package paths in cache
ros_search_path = RosSearchPath()


def genros_py(rosfiles, generator, package, outdir, includepath=None):
    includepath = includepath or []

    if not os.path.exists(outdir):
        # This script can be run multiple times in parallel. We
        # don't mind if the makedirs call fails because somebody
        # else snuck in and created the directory before us.
        try:
            os.makedirs(outdir)
        except OSError as e:
            if not os.path.exists(outdir):
                raise
    # TODO : maybe we dont need this, and that translation should be handled before ?
    search_path = genmsg.command_line.includepath_to_dict(includepath)
    ros_search_path.update(search_path)
    retcode = generator.generate_messages(package, rosfiles, outdir, ros_search_path)
    assert retcode == 0
    # TODO : handle thrown exception (cleaner than hacking the search path dict...)
    # try:
    #     generator.generate_messages(package, rosfiles, outdir, search_path)
    # except genmsg.MsgNotFound as mnf:
    #     try:
    #         mod = importlib.import_module(mnf.package)
    #         # import succeeded : we should get the namespace path that has '/msg'
    #         # and add it to the list of paths to avoid going through this all over again...
    #         for p in mod.__path__:
    #             # Note we want dependencies here. dependencies are ALWAYS '.msg' files in 'msg' directory.
    #             msg_path = os.path.join(p, genmsg_MSG_DIR)
    #             # We add a path only if we can find the 'msg' directory
    #             search_path[mnf.package] = search_path[mnf.package] + ([msg_path] if os.path.exists(msg_path) else [])
    #         # Try generation again
    #         generator.generate_messages(package, rosfiles, outdir, search_path)
    #     except ImportError:
    #         # import failed
    #         return None


def genmsg_py(msg_files, package, outdir_pkg, includepath=None, initpy=True):
    """
    Generates message modules for a package, in that package directory, in a subpackage called 'msg', following ROS conventions
    :param msg_files: the .msg files to use as input for generating the python message classes 
    :param package: the package for which we want to generate these messages
    :param outdir_pkg: the directory of the package, where to put these messages. It should finish with <package> path
    :param includepath: optionally the list of path to include, in order to retrieve message dependencies
    :param initpy: whether create an __init__.py for this package
    :return: the list of files generated
    """
    includepath = includepath or []
    outdir = os.path.join(outdir_pkg, 'msg')

    # checking if we have files with unknown extension to except early
    for f in msg_files:
        if not f.endswith('.msg'):
            print("WARNING: {f} doesnt have the proper .msg extension. It has been Ignored.".format(**locals()), file=sys.stderr)

    try:
        genros_py(rosfiles=[f for f in msg_files if f.endswith('.msg')],
                  generator=genpy_generator.MsgGenerator(),
                  package=package,
                  outdir=outdir,
                  includepath=includepath,
        )
        # because the OS interface might not be synchronous....
        while not os.path.exists(outdir):
            time.sleep(.1)

    except genmsg.InvalidMsgSpec as e:
        print("ERROR: ", e, file=sys.stderr)
        raise
    except genmsg.MsgGenerationException as e:
        print("ERROR: ", e, file=sys.stderr)
        raise
    except Exception as e:
        traceback.print_exc()
        print("ERROR: ", e)
        raise

    genset = set()

    # optionally we can generate __init__.py
    if initpy:
        init_path = os.path.join(outdir, '__init__.py')
        if os.path.exists(init_path):
            raise PkgAlreadyExists("Keeping {init_path}, generation skipped.")
        else:
            genpy_generate_initpy.write_modules(outdir)
            genset.add(init_path)
    else:  # we list all files, only if init.py was not created (and user has to import one by one)
        for f in msg_files:
            f, _ = os.path.splitext(f)  # removing extension
            os.path.relpath(outdir)
            genset.add(os.path.join(outdir, '_' + os.path.basename(f) + '.py'))

    return genset


def gensrv_py(srv_files, package, outdir_pkg, includepath=None, initpy=True):
    """
    Generates service modules for a package, in that package directory, in a subpackage called 'srv', following ROS conventions
    :param srv_files: the .srv files to use as input for generating the python service classes 
    :param package: the package for which we want to generate these services
    :param outdir_pkg: the directory of the package, where to put these services. It should finish with <package> path
    :param includepath: optionally the list of path to include, in order to retrieve message dependencies
    :param initpy: whether create an __init__.py for this package
    :return: the list of files generated 
    """
    includepath = includepath or []
    outdir = os.path.join(outdir_pkg, 'srv')

    # checking if we have files with unknown extension to except early
    for f in srv_files:
        if not f.endswith('.srv'):
            print("WARNING: {f} doesnt have the proper .srv extension. It has been Ignored.".format(**locals()), file=sys.stderr)

    try:
        genros_py(rosfiles=[f for f in srv_files if f.endswith('.srv')],
                  generator=genpy_generator.SrvGenerator(),
                  package=package,
                  outdir=outdir,
                  includepath=includepath,
        )
        # because the OS interface might not be synchronous....
        while not os.path.exists(outdir):
            time.sleep(.1)

    except genmsg.InvalidMsgSpec as e:
        print("ERROR: ", e, file=sys.stderr)
        raise
    except genmsg.MsgGenerationException as e:
        print("ERROR: ", e, file=sys.stderr)
        raise
    except Exception as e:
        traceback.print_exc()
        print("ERROR: ", e)
        raise

    genset = set()

    # optionally we can generate __init__.py
    if initpy:
        init_path = os.path.join(outdir, '__init__.py')
        if os.path.exists(init_path):
            raise PkgAlreadyExists("Keeping {init_path}, generation skipped.")
        else:
            genpy_generate_initpy.write_modules(outdir)
            genset.add(init_path)
    else:  # we list all files, only if init.py was not created (and user has to import one by one)
        for f in srv_files:
            f, _ = os.path.splitext(f)  # removing extension
            os.path.relpath(outdir)
            genset.add(os.path.join(outdir, '_' + os.path.basename(f) + '.py'))

    return genset


def generate_msgpkg(msgfiles, package=None, dependencies=None, include_path=None, outdir_pkg=None):
    # TODO : since we return a full package, we should probably pass a dir, not the files one by one...
    # by default we generate for this package (does it make sense ?)
    # Careful it might still be None
    package = package or 'gen_msgs'

    # by default we have no dependencies
    dependencies = dependencies or []

    if not outdir_pkg or not outdir_pkg.startswith(os.sep):
        # if path is not absolute, we create a temporary directory to hold our generated package
        gendir = tempfile.mkdtemp('pyros_gen_site')
        outdir_pkg = os.path.join(gendir, outdir_pkg if outdir_pkg else package)

    include_path = include_path or []

    # we might need to resolve some dependencies
    unresolved_dependencies = [d for d in dependencies if d not in [p.split(':')[0] for p in include_path]]

    if unresolved_dependencies:
        try:
            # In that case we have no choice but to rely on ros packages (on the system) => ROS has to be setup.
            import rospkg

            # get an instance of RosPack with the default search paths
            rospack = rospkg.RosPack()
            for d in unresolved_dependencies:
                try:
                    # get the file path for a dependency
                    dpath = rospack.get_path(d)
                    # we populate include_path
                    include_path.append('{d}:{dpath}/msg'.format(**locals()))  # AFAIK only msg can be dependent msg types
                except rospkg.ResourceNotFound as rnf:
                    raise MsgDependencyNotFound(rnf.message)
        except ImportError:
            print("Attempt to import rospkg failed before attempting to resolve dependencies {0}".format(unresolved_dependencies))

    gen_files = genmsg_py(msg_files=msgfiles, package=package, outdir_pkg=outdir_pkg, includepath=include_path, initpy=True)

    # computing module names that will be importable after outdir_pkg has been added as sitedir
    gen_msgs = None
    # Not ideal, but it will do until we implement a custom importer
    for f in gen_files:
        test_gen_msgs_parent = None
        f = f[:-len('.py')] if f.endswith('.py') else f
        f = f[:-len(os.sep + '__init__')] if f.endswith(os.sep + '__init__') else f

        if f.endswith('msg'):
            gen_msgs = package + '.msg'

    # we need to get one level up to get the sitedir (containing the generated namespace package)
    return os.path.dirname(outdir_pkg), gen_msgs
    # TODO : return something that can be imported later... with custom importer or following importlib API...


def generate_srvpkg(srvfiles, package=None, dependencies=None, include_path=None, outdir_pkg=None, ns_pkg=True):
    # TODO : since we return a full package, we should probably pass a dir, not the files one by one...
    # by default we generate for this package (does it make sense ?)
    # Careful it might still be None
    package = package or 'gen_msgs'

    # by default we have no dependencies
    dependencies = dependencies or []

    if not outdir_pkg or not outdir_pkg.startswith(os.sep):
        # if path is not absolute, we create a temporary directory to hold our generated package
        gendir = tempfile.mkdtemp('pyros_gen_site')
        outdir_pkg = os.path.join(gendir, outdir_pkg if outdir_pkg else package)

    include_path = include_path or []

    # we might need to resolve some dependencies
    unresolved_dependencies = [d for d in dependencies if d not in [p.split(':')[0] for p in include_path]]

    if unresolved_dependencies:
        try:
            # In that case we have no choice but to rely on ros packages (on the system) => ROS has to be setup.
            import rospkg

            # get an instance of RosPack with the default search paths
            rospack = rospkg.RosPack()
            for d in unresolved_dependencies:
                try:
                    # get the file path for a dependency
                    dpath = rospack.get_path(d)
                    # we populate include_path
                    include_path.append('{d}:{dpath}/srv'.format(**locals()))  # AFAIK only msg can be dependent msg types
                except rospkg.ResourceNotFound as rnf:
                    raise MsgDependencyNotFound(rnf.message)
        except ImportError:
            print("Attempt to import rospkg failed before attempting to resolve dependencies {0}".format(unresolved_dependencies))

    gen_files = gensrv_py(srv_files=srvfiles, package=package, outdir_pkg=outdir_pkg, includepath=include_path, initpy=True)

    # computing module names that will be importable after outdir_pkg has been added as sitedir
    gen_srvs = None
    # Not ideal, but it will do until we implement a custom importer
    for f in gen_files:
        test_gen_msgs_parent = None
        f = f[:-len('.py')] if f.endswith('.py') else f
        f = f[:-len(os.sep + '__init__')] if f.endswith(os.sep + '__init__') else f

        if f.endswith('srv'):
            gen_srvs = package + '.srv'

    # we need to get one level up to get the sitedir (containing the generated namespace package)
    return os.path.dirname(outdir_pkg), gen_srvs
    # TODO : return something that can be imported later... with custom importer or following importlib API...

