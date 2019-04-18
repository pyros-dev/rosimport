Changelog
=========


0.4.0 (2019-04-18)
------------------
- Merge pull request #16 from pyros-dev/pyros_deps. [AlexV]

  now relying on forked genmsg and genpy from PyPI.
- Now relying on forked genmsg and genpy from PyPI. [AlexV]


0.3.0 (2018-05-21)
------------------
- V0.3.0. [AlexV]
- Reviewed README after API change. [AlexV]
- Merge pull request #15 from pyros-dev/ff2_5. [AlexV]

  adapting to latest filefinder2
- Filefinder2 released. [AlexV]
- Replicating filefinder2 API changes with a RosImporter class as
  context manager. [AlexV]
- Fixed bugs where hook indexes were switched. [AlexV]
- Removing filefinder call where not needed. [AlexV]
- Adapting to latest filefinder2. [AlexV]
- Typo. [AlexV]
- Fixing badges after moving github url. [alexv]
- Fixing ignore list. [alexv]


0.2.1 (2017-08-08)
------------------
- V0.2.1. [alexv]
- Now depending on latest filefinder2 release. [alexv]
- Letting filefinder2 manage create_module API being available or not.
  [alexv]
- Removing python version restriction on filefinder since it now manages
  API compat. [alexv]
- Moving submodules used by tests. [alexv]
- Removign submodules that we can get with pip. restructured tests.
  [alexv]
- Fixing filefinder version. [alexv]
- Merge pull request #11 from asmodehn/import_23_api. [AlexV]

  Import 23 api
- Fixing tests after filefinder2 api change. [alexv]
- Small changes to attempt dealing with filefinder providing an importer
  API... [alexv]
- Now using ROS_PACKAGE_PATH as initial search path if setup in
  environment. [alexv]


0.1.1 (2017-07-17)
------------------
- V0.1.1. [alexv]
- Fixing tests after activate/deactivate api change. [alexv]
- Refining requirement after filefinder2 release v0.3. [alexv]
- Preventing multiple activation to pollute sys.path_hooks and
  sys.meta_path. [alexv]
- Merge pull request #3 from asmodehn/generate_refactor. [AlexV]

  Generate refactor
- Change activate to not use paths list. use site.addsiteir instead.
  fixing ROS pathfinder to handle case some msg folder is missing. extra
  fix since the search path contains sets and not lists. [alexv]
- Fixing tests and cleaning up message definitions. [alexv]
- All generator tests now passing locally. [alexv]
- Adding rospathfinder and refactoring to handle self dependencies
  between different subdirectories in same package. [alexv]
- Extracted tests again and got all tests to pass for py3. [alexv]
- Moving tests outside of pacakge, to make debugging import problems
  easier. improved generator and import tests now passing. [alexv]
- Adding comment to handle dependency message not found exception (when
  it will be available on genmsg). [alexv]
- Fixing import srv tests after adding msg dependency. added bwcompat
  code for genmsg. [alexv]
- Making generator test work by using searchpath from genmsg API.
  [alexv]
- Adding gitignore. [alexv]
- Merge branch 'namespace_meta' [alexv]
- Fixing quantified code link and usage example. [alexv]
- Merge pull request #1 from asmodehn/namespace_meta. [AlexV]

  fixing finder and loader for python3.5 to let default FileFinder do h…
- Organizing the public API. [alexv]
- Merging identical RosLoader code. [alexv]
- Merging identical Rosfinder code. [alexv]
- Added dependency on filefinder2. now using develop in tox since genpy
  and genmsg need to be used from source. temporarily using unreleased
  filefinder2. [alexv]
- Fixing finder for py2 by relying on meta_path instead of inheritance.
  [alexv]
- Adding python 3.6 to test. removing idea files. [alexv]
- Adding services test for importlib. [alexv]
- Fixing test for srv import. [alexv]
- Fixed issue with relative paths in finder. [alexv]
- Adding version module. [alexv]
- Fixing finder and loader for python3.5 to let default FileFinder do
  his thing when there is no ROS directory in sight. [alexv]
- Extracting from pyros-msgs. [alexv]
- Initial commit. [AlexV]


