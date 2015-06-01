#!/usr/bin/env python
import os,sys,optparse,platform
from commands import *
from time import sleep
from libs.gbp_verify_libs import Gbp_Verify
from test_main_config import gbp_main_config
from testcases.testcases_dp.testsuites_setup_cleanup import super_hdr,header1,header2,header3,header4
from testcases.testcases_dp.testsuite_same_ptg_l2p_l3p import test_same_ptg_same_l2p_same_l3p
from testcases.testcases_dp.testsuite_diff_ptg_same_l2p_l3p import test_diff_ptg_same_l2p_l3p
from testcases.testcases_dp.testsuite_diff_ptg_diff_l2p_same_l3p import test_diff_ptg_diff_l2p_same_l3p
from testcases.testcases_dp.testsuite_diff_ptg_diff_l2p_diff_l3p import test_diff_ptg_diff_l2p_diff_l3p

def main():
    header_to_suite_map = {'header1': [header1,test_same_ptg_same_l2p_same_l3p], 
                           'header2': [header2,test_diff_ptg_same_l2p_l3p],
                           'header3': [header3,test_diff_ptg_diff_l2p_same_l3p],
                           'header4': [header4,test_diff_ptg_diff_l2p_diff_l3p]}
    
    # Build the Test Config to be used for all DataPath Testcases
    cfg_file = sys.argv[1]
    print "Setting up global config for all DP Testing"
    testbed_cfg = gbp_main_config(cfg_file)
    testbed_cfg.setup()
    
    # Fetch gbp objects via heat output
    gbpverify = Gbp_Verify()
    objs_uuid = gbpverify.get_uuid_from_stack(super_hdr.heat_temp,super_hdr.stack_name)
    print "Before Running Test .. sleeping for 120 secs to enable SSH Contract"  #TODO: Will remove this once implicit ssh contract
    sleep(120)
    for val in header_to_suite_map.itervalues():
       #Initialize Testsuite specific config setup/cleanup class
       header = val[0]()

       #Build the Testsuite specific setup/config
       #header.setup()

       #Initialize Testsuite class to run its testcases
       testsuite = val[1](objs_uuid)

       #now run the loop of test-combos
       for vpc in ['novpc','vpc_novpc','vpc_vpc']:
        for ip in ['ipv4','ipv6']:  
         for bdtype in ['vxlan','vlan']:  
           for location in ['same_host','diff_host_same_leaf','diff_host_diff_leaf']: 
                   #Run the testcases specific to the initialized testsuite
                   log_string = "%s_%s_%s_%s" %(vpc,ip,bdtype,location)
                   testsuite.test_runner(log_string,location)
       #Testsuite specific cleanup
       #header.cleanup()
    testbed_cfg.cleanup()
    
if __name__ == "__main__":
    main()

