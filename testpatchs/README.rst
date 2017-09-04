Tests
=====

The tests package is NOT a namespace package, and not included in the distribution. This allows to ::

- not have the tests in the final product (people not interested in development will likely not use them)
- provide the advantage of isolating the tests from source code and enforce testing also the install procedure. (=> No need to add an artifical src/ subdir for the package )
- tests ways to dynamically patch generated ros code at import time
