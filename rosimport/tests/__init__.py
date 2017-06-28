from __future__ import absolute_import, division, print_function
#
# import os
# try:
#     # Using std_msgs directly if ROS has been setup (while using from ROS pkg)
#     import std_msgs
#
# except ImportError:
#
#     # Otherwise we refer to our submodules here (setup.py usecase, or running from tox without site-packages)
#
#     import site
#     site.addsitedir(os.path.join(
#         os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
#         'ros-site'
#     ))
#
#     import std_msgs
#
#     # Note we do not want to use pyros_setup here.
#     # We do not want to do a full ROS setup, only import specific packages.
#     # If needed it should have been done before (loading a parent package).
#     # this handle the case where we want to be independent of any underlying ROS system.
