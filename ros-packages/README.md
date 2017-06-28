This folder is added with site.addsitedir() to provide a set of ROS python packages from source.
It happens when the import of one of these packages(usually found on ROS systems) fails.
This is the case from pure python, for our automated testing tox suite.

If ROS is setup before executing pyros_msgs/importer/rosmsg_generator.py,
then the ROS versions of these packages will be used instead 