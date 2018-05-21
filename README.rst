rosimport
=========

ROS message definitions python importer

.. start-badges

.. list-table::
    :stub-columns: 1

    * - tests
      - |travis| |requires| |landscape| |quantifiedcode|
    * - Python
      - |version| |downloads| |wheel| |supported-versions| |supported-implementations|

.. |travis| image:: https://travis-ci.org/pyros-dev/rosimport.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/pyros-dev/rosimport

.. |quantifiedcode| image:: https://www.quantifiedcode.com/api/v1/project/4d473ef2517041c4adc1214c88e4abae/badge.svg
    :target: https://www.quantifiedcode.com/app/project/4d473ef2517041c4adc1214c88e4abae
    :alt: Code issues

.. |requires| image:: https://requires.io/github/pyros-dev/rosimport/requirements.svg?branch=master
    :alt: Requirements Status
    :target: hhttps://requires.io/github/pyros-dev/rosimport/requirements/?branch=master

.. |landscape| image:: https://landscape.io/github/pyros-dev/rosimport/master/landscape.svg?style=flat
    :target: hhttps://landscape.io/github/pyros-dev/rosimport/master
    :alt: Code Quality Status

.. |version| image:: https://img.shields.io/pypi/v/rosimport.svg?style=flat
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/rosimport

.. |downloads| image:: https://img.shields.io/pypi/dm/rosimport.svg?style=flat
    :alt: PyPI Package monthly downloads
    :target: https://pypi.python.org/pypi/rosimport

.. |wheel| image:: https://img.shields.io/pypi/wheel/rosimport.svg?style=flat
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/rosimport

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/rosimport.svg?style=flat
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/rosimport

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/rosimport.svg?style=flat
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/rosimport

.. end-badges


Usage:
------
::

    import sys
    import rosimport

    with rosimport.RosImporter():

        import my_msgs.msg  # directly from a my_msgs/msg directory containing My.msg ros definition
        # Or relatively :
        from . import msg

    # modules are still available, but importer has been deactivated.
