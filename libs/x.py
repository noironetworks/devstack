#!/usr/bin/env python
import sys, time
import paramiko
import subprocess
import re
import os
import sys
import itertools
from prettytable import PrettyTable
from Crypto.PublicKey import RSA

def foo():
  print 'Jishnu'

def foo1():
  print 'kalo'

class A(object):
   def setup(self):
      foo()
   def clean(self):
       foo1()

h=A()
h.setup()
h.clean()
