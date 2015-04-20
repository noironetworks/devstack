#!/usr/bin/env python
import sys
import os
import glob
#from testcases.testcases_integ import *
import testcases.testcases_integ
modules = glob.glob(os.path.dirname(__file__)+"/*.py")
print modules
for f in modules:
   print os.path.basename(f)[:-3]

