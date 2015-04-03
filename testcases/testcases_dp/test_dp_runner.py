#!/usr/bin/env python
import os,sys,optparse,platform
from commands import *
from time import sleep
from test_main_config import gbp_main_config
from testsuites_setup_cleanup import header1,header2,header3,header4

def main():
    
    ## Initialize the Base Headers Class
    #cfg_file = sys.argv[1]
    #print "setting up global config for all DP Testing"
    #testbed_cfg = gbp_main_config(cfg_file)
    #testbed_cfg.setup()
    print 'Going to Initialize Header Specific TestClass'
    h=header1()
    h.setup()
    print 'Going to sleep now for 180 secs'
    sleep(180)
    testbed_cfg.cleanup()
    
if __name__ == "__main__":
    main()

