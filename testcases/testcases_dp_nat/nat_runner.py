#!/usr/bin/env python
import os
import sys
import optparse
import platform
from commands import *
from time import sleep
from libs.gbp_verify_libs import Gbp_Verify
from natdptestsetup import nat_dp_main_config

def get_obj_uuids(cfgfile,nat_type=''):

    gbpverify = Gbp_Verify()
    testbed_cfg = nat_dp_main_config(cfgfile)
    if nat_type == '' or nat_type == 'dnat':
       objs_uuid = gbpverify.get_uuid_from_stack(
                    testbed_cfg.dnat_heat_temp,
                    testbed_cfg.heat_stack_name)
    if nat_type == 'snat':
       objs_uuid = gbpverify.get_uuid_from_stack(
                    testbed_cfg.snat_heat_temp,
                    testbed_cfg.heat_stack_name)
    objs_uuid['external_gw'] = testbed_cfg.extgw
    objs_uuid['ostack_controller'] = testbed_cfg.cntlr_ip
    objs_uuid['ipsofextgw'] = testbed_cfg.ips_of_extgw
    objs_uuid['ntk_node'] = testbed_cfg.ntk_node
    print 'OBJS_UUID == \n', objs_uuid
    return objs_uuid

def main():

    # Build the Test Config to be used for all NAT DataPath Testcases
    cfgfile = sys.argv[1]
    testbed_cfg = nat_dp_main_config(cfgfile)
    if len(sys.argv) == 3:
       nat_type = sys.argv[2]
    
    if nat_type == 'dnat':
        # RUN ONLY DNAT DP TESTs
        # TestSetup Configuration
        print 'Setting up global config for all DNAT DP Testing'
        targetVmFips = testbed_cfg.setup(nat_type, do_config=0)
        # Fetch gbp objects via heat output
        objs_uuid = get_obj_uuids(cfgfile)
        # Execution of DNAT DP Tests from ExtRtr to VMs
        from testcases.testcases_dp_nat.testsuite_dnat_extgw_to_vm import DNAT_ExtGw_to_VMs
        test_dnat_extgw_to_vm = DNAT_ExtGw_to_VMs(objs_uuid, targetVmFips)
        test_dnat_extgw_to_vm.test_runner()
        # Execution of DNAT DP Test from VM to ExtGW and VM-to-VM    
        from testcases.testcases_dp_nat.testsuite_dnat_vm_to_vm import DNAT_VMs_to_VMs
        test_dnat_vm_to_allvms = DNAT_VMs_to_VMs(objs_uuid, targetVmFips)
        test_dnat_vm_to_allvms.test_runner()
        # Cleanup
        testbed_cfg.cleanup()

    if nat_type == 'snat':
        # RUN ONLY SNAT DP TESTs
        # TestSetup Configuration
        print 'Setting up global config for SNAT DP Testing'
        testbed_cfg.setup('snat', do_config=0)
        # Fetch gbp objects via heat output
        objs_uuid = get_obj_uuids(cfgfile)
        # Execution of SNAT DP Tests
        from testcases.testcases_dp_nat.testsuite_snat_vm_to_extgw import SNAT_VMs_to_ExtGw
        test_snat_allvms_to_extgw = SNAT_VMs_to_ExtGw(objs_uuid)
        test_snat_allvms_to_extgw.test_runner()
        # Cleanup after the SNAT Testsuite is run
        testbed_cfg.cleanup()

if __name__ == "__main__":
    main()
