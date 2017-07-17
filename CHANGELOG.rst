Changelog
=========


0.1.1 (2017-07-17)
------------------
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


