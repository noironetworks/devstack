#!/usr/bin/env python
import os,sys,optparse,platform
from commands import *
from time import sleep
from libs.gbp_verify_libs import Gbp_Verify
from natdptestsetup import nat_dp_main_config
from testcases.testcases_dp_nat.testsuite_nat_dp import DNAT_ExtGw_to_VMs

def main():
    
    # Build the Test Config to be used for all DataPath Testcases
    cfg_file = sys.argv[1]
    print "Setting up global config for all NAT DP Testing"
    testbed_cfg = nat_dp_main_config(cfg_file)
    targetVmFips = testbed_cfg.setup()
    
    # Fetch gbp objects via heat output
    gbpverify = Gbp_Verify()
    print testbed_cfg.heat_temp_test,testbed_cfg.heat_stack_name
    objs_uuid = gbpverify.get_uuid_from_stack(testbed_cfg.heat_temp_test,testbed_cfg.heat_stack_name)
    objs_uuid['external_gw'] = testbed_cfg.extgw
    objs_uuid['ostack_controller'] = testbed_cfg.cntlr_ip
    print 'OBJS_UUID == \n', objs_uuid
    #sys.exit(1)
    print "Waiting for IP/MAC learning by Fabric via both VMM & Datapath before we start the test"
    #sleep(30)
    test_dnat_extgw_to_vm = DNAT_ExtGw_to_VMs(objs_uuid,targetVmFips)
    test_dnat_extgw_to_vm.test_runner()
    
if __name__ == "__main__":
    main()

