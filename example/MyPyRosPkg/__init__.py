import sys
import rosimport

with rosimport.RosImporter():

    from . import msg

print("dir(msg) ->" + repr(dir(msg)))

import inspect
print("inspect.getsource(msg.mymsg) ->")
print(inspect.getsource(msg.mymsg))
