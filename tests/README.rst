Tests
=====

The tests package is a namespace package, and not included in the distribution. This allows to ::

- not have the tests in the final product (people not interested in development will likely not use them)
- provide the advantage of isolating the tests from source code and enforce testing also the install procedure. (=> No need to add an artifical src/ subdir for the package )
- merge the tests with other packages' tests using the same structure, when running from source, so that running `py.test --pyargs tests` will run *all* tests at once
