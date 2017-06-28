from __future__ import absolute_import, division, print_function

import os
import sys
import tempfile
import traceback
import importlib

import time

import pkg_resources

"""
Module that can be used standalone, or as part of the pyros_msgs.importer package

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


class MsgDependencyNotFound(Exception):
    pass


class PkgAlreadyExists(Exception):
    pass


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
    generator.generate_messages(package, rosfiles, outdir, search_path)


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


def genmsgsrv_py(msgsrv_files, package, outdir_pkg, includepath=None, ns_pkg=True):
    """"""
    includepath = includepath or []

    # checking if we have files with unknown extension to except early
    for f in msgsrv_files:
        if not f.endswith(('.msg', '.srv')):
            print("WARNING: {f} doesnt have the proper .msg or .srv extension. It has been Ignored.".format(**locals()), file=sys.stderr)

    genset = set()
    generated_msg = genmsg_py(msg_files=[f for f in msgsrv_files if f.endswith('.msg')],
                              package=package,
                              outdir_pkg=outdir_pkg,
                              includepath=includepath,
                              initpy=True)  # we always create an __init__.py when called from here.
    generated_srv = gensrv_py(srv_files=[f for f in msgsrv_files if f.endswith('.srv')],
                              package=package,
                              outdir_pkg=outdir_pkg,
                              includepath=includepath,
                              initpy=True)  # we always create an __init__.py when called from here.

    if ns_pkg:
        # The namespace package creation is only here to allow mixing different path for the same package
        # so that we do not have to generate messages and services in the package path (that might not be writeable)
        # Note : the *first* package imported need to declare the namespace package for this to work.
        # Ref : https://packaging.python.org/namespace_packages/
        nspkg_init_path = os.path.join(outdir_pkg, '__init__.py')
        if os.path.exists(nspkg_init_path):
            raise PkgAlreadyExists("Keeping {nspkg_init_path}, generation skipped.")
        else:
            with open(nspkg_init_path, "w") as nspkg_init:
                nspkg_init.writelines([
                    "from __future__ import absolute_import, division, print_function\n",
                    "# this is an autogenerated file for dynamic ROS message creation\n",
                    "import pkg_resources\n",
                    "pkg_resources.declare_namespace(__name__)\n",
                    ""
                ])

            # because the OS interface might not be synchronous....
            while not os.path.exists(nspkg_init_path):
                time.sleep(.1)

    # Whether or not we create the namespace package, we have to return back both msg and srv subpackages,
    #  since they need to be imported explicitely
    genset = genset.union(generated_msg)
    genset = genset.union(generated_srv)

    return genset


def generate_msgsrv_nspkg(msgsrvfiles, package=None, dependencies=None, include_path=None, outdir_pkg=None, ns_pkg=True):
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

    gen_files = genmsgsrv_py(msgsrv_files=msgsrvfiles, package=package, outdir_pkg=outdir_pkg, includepath=include_path, ns_pkg=ns_pkg)

    # computing module names that will be importable after outdir_pkg has been added as sitedir
    gen_msgs = None
    gen_srvs = None
    # Not ideal, but it will do until we implement a custom importer
    for f in gen_files:
        test_gen_msgs_parent = None
        f = f[:-len('.py')] if f.endswith('.py') else f
        f = f[:-len(os.sep + '__init__')] if f.endswith(os.sep + '__init__') else f

        if f.endswith('msg'):
            gen_msgs = package + '.msg'

        if f.endswith('srv'):
            gen_srvs = package + '.srv'

    # we need to get one level up to get the sitedir (containing the generated namespace package)
    return os.path.dirname(outdir_pkg), gen_msgs, gen_srvs
    # TODO : return something that can be imported later... with custom importer or following importlib API...


# This API is useful to import after a generation has been done with details.
# TODO : implement custom importer to do this as properly as possible
def import_msgsrv(sitedir, gen_msgs = None, gen_srvs = None):
    import site
    site.addsitedir(sitedir)  # we add our output dir as a site (to be able to import from it as usual)
    # because we modify sys.path, we also need to handle namespace packages
    pkg_resources.fixup_namespace_packages(sitedir)

    msgs_mod = importlib.import_module(gen_msgs)
    srvs_mod = importlib.import_module(gen_srvs)

    return msgs_mod, srvs_mod
    # TODO : doublecheck and fix that API to return the same thing as importlib.import_module returns, for consistency,...

