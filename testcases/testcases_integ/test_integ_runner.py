#!/usr/bin/env python
import os,sys,optparse,platform
import glob
from commands import *

def main():
    f = open(sys.argv[1],'rt')
    test_conf = yaml.load(f)
    test_runner = wrapper(test_conf)
    test_runner.run()

class wrapper(object):
   
    def __init__(self,config_file):
       self.cntrl_ip = config_file["controller_ip"]
       self.heat_stack_name = config_file["heat_stack_name"]

    def run(self):
       for name in glob.glob('testcase_aci_integ*.py'):
       cmd="python %s" %(name)
       getoutput(cmd)

if __name__ = '__main__':
    main()
