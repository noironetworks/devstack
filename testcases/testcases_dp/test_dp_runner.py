#!/usr/bin/env python
import os,sys,optparse,platform
from commands import *
from time import sleep
from test_main_config import gbp_main_config
from testcases.testcases_dp.testsuites_setup_cleanup import header1,header2,header3,header4
from testcases.testcases_dp.testsuite_same_ptg_l2p_l3p import test_same_ptg_same_l2p_same_l3p
from testcases.testcases_dp.testsuite_diff_ptg_same_l2p_l3p import test_diff_ptg_same_l2p_l3p
from testcases.testcases_dp.testsuite_diff_ptg_diff_l2p_same_l3p import test_diff_ptg_diff_l2p_same_l3p
from testcases.testcases_dp.testsuite_diff_ptg_diff_l2p_diff_l3p import test_diff_ptg_diff_l2p_diff_l3p

def main():
    
    header_to_suite_map = {'header1': [header1,test_same_ptg_same_l2p_same_l3p],
                           'header2': [header2,test_diff_ptg_same_l2p_l3p],
                           'header3': [header3,test_diff_ptg_diff_l2p_same_l3p],
                           'header4': [header4,test_diff_ptg_diff_l2p_diff_l3p]}

    ## Build the Test Config to be used for all DataPath Testcases
    cfg_file = sys.argv[1]
    print "Setting up global config for all DP Testing"
    testbed_cfg = gbp_main_config(cfg_file)
    testbed_cfg.setup()
    for val in header_to_suite_map.itervalues():
       #Initialize Testsuite specific config setup/cleanup class
       header = val[0]()
       #Build the Testsuite specific setup/config
       #header.setup()
       #Initialize Testsuite class to run its testcases
       testsuite = val[1]()
       #now run the loop of test-combos
       print "Before Running Test .. sleeping for 60 secs to enable SSH Contract"  #TODO: Will remove this once implicit ssh contract
       #for ip in ['ipv4','ipv6']:  #TODO: Enable this when ipv6 support is known
       for ip in ['ipv4']:
         #for bdtype in ['vxlan','vlan']:  #TODO: Enable this when vlan support is known
         for bdtype in ['vxlan']:
           #for location in ['same_host','diff_host_same_leaf','diff_host_diff_leaf']: #TODO: Enable this when diff_leaf support is known
           for location in ['same_host','diff_host_same_leaf']: #location strings MUST NOT BE CHANGED
                   #Run the testcases specific to the initialized testsuite
                   log_string = "%s_%s" %(bdtype,location)
                   testsuite.test_runner(log_string,location)
       #Testsuite specific cleanup
       header.cleanup()
    testbed_cfg.cleanup()
    
if __name__ == "__main__":
    main()

