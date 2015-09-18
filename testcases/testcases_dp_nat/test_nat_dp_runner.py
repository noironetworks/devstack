#!/usr/bin/env python
import os,sys,optparse,platform
from commands import *
from time import sleep
from libs.gbp_verify_libs import Gbp_Verify
from natdptestsetup import nat_dp_main_config

def main():
    
    # Build the Test Config to be used for all DataPath Testcases
    cfg_file = sys.argv[1]
    print "Setting up global config for all NAT DP Testing"
    testbed_cfg = nat_dp_main_config(cfg_file)
    targetVmFips = testbed_cfg.setup(getfips=1)
    
    # Fetch gbp objects via heat output
    gbpverify = Gbp_Verify()
    print testbed_cfg.heat_temp_test,testbed_cfg.heat_stack_name
    objs_uuid = gbpverify.get_uuid_from_stack(testbed_cfg.heat_temp_test,testbed_cfg.heat_stack_name)
    objs_uuid['external_gw'] = testbed_cfg.extgw
    objs_uuid['ostack_controller'] = testbed_cfg.cntlr_ip
    objs_uuid['ipsofextgw'] = testbed_cfg.ips_of_extgw
    print 'OBJS_UUID == \n', objs_uuid
    print "Waiting for IP/MAC learning by Fabric via both VMM & Datapath before we start the test"
    sleep(30)
    from testcases.testcases_dp_nat.testsuite_dnat_extgw_to_vm import DNAT_ExtGw_to_VMs
    #test_dnat_extgw_to_vm = DNAT_ExtGw_to_VMs(objs_uuid,targetVmFips)
    #test_dnat_extgw_to_vm.test_runner()
    from testcases.testcases_dp_nat.testsuite_dnat_vm_to_vm import DNAT_VMs_to_VMs
    test_dnat_vm_to_allvms = DNAT_VMs_to_VMs(objs_uuid,targetVmFips)
    test_dnat_vm_to_allvms.test_runner()
    #from testcases.testcases_dp_nat.testsuite_snat_vm_to_extgw import SNAT_VMs_to_ExtGw
    #test_snat_allvms_to_extgw = SNAT_VMs_to_ExtGw(objs_uuid)
    #test_snat_allvms_to_extgw.test_runner()

if __name__ == "__main__":
    main()

