HOW TO USE
==========

Use a virtualenv. If you are not sure how, you can do some very useful reading at https://packaging.python.org/tutorials/managing-dependencies/

If you have direnv (and pipenv) on your machine, this is done as soon as you 'cd' into rosimport working tree.


1) Install rosimport in the virtualenv::

  (rosimport--FuygrvY)alexv@AlexV-ROS-vbox:~/rosimport$ pipenv install -e .
  Installing -e .…
  Adding rosimport to Pipfile's [packages]…
  ✔ Installation Succeeded 
  Pipfile.lock (474337) out of date, updating to (c8604e)…
  Locking [dev-packages] dependencies…
  ✔ Success! 
  Locking [packages] dependencies…
  ✔ Success! 
  Updated Pipfile.lock (474337)!
  Installing dependencies from Pipfile.lock (474337)…
    🐍   ▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉ 5/5 — 00:00:02
  (rosimport--FuygrvY)alexv@AlexV-ROS-vbox:~/rosimport$ 

2) Import the package to trigger the import sequence



