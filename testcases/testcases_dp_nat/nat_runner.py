#!/usr/bin/env python
import os
import sys
import optparse
import platform
from commands import *
from time import sleep
from libs.gbp_verify_libs import Gbp_Verify
from natdptestsetup import nat_dp_main_config


def main():

    # Build the Test Config to be used for all NAT DataPath Testcases
    cfg_file = sys.argv[1]
    testbed_cfg = nat_dp_main_config(cfg_file)

    # DNAT TEST SECTION:
    print 'Setting up global config for all DNAT DP Testing'
    targetVmFips = testbed_cfg.setup('dnat', do_config=0)

    # Fetch gbp objects via heat output
    gbpverify = Gbp_Verify()
    print testbed_cfg.heat_temp_test, testbed_cfg.heat_stack_name
    objs_uuid = gbpverify.get_uuid_from_stack(
        testbed_cfg.dnat_heat_temp, testbed_cfg.heat_stack_name)
    objs_uuid['external_gw'] = testbed_cfg.extgw
    objs_uuid['ostack_controller'] = testbed_cfg.cntlr_ip
    objs_uuid['ipsofextgw'] = testbed_cfg.ips_of_extgw
    objs_uuid['ntk_node'] = testbed_cfg.ntk_node
    print 'OBJS_UUID == \n', objs_uuid

    from testcases.testcases_dp_nat.testsuite_dnat_extgw_to_vm import DNAT_ExtGw_to_VMs
    test_dnat_extgw_to_vm = DNAT_ExtGw_to_VMs(objs_uuid, targetVmFips)
    test_dnat_extgw_to_vm.test_runner()

    from testcases.testcases_dp_nat.testsuite_dnat_vm_to_vm import DNAT_VMs_to_VMs
    test_dnat_vm_to_allvms = DNAT_VMs_to_VMs(objs_uuid, targetVmFips)
    test_dnat_vm_to_allvms.test_runner()

    # Cleanup before the SNAT Testsuite is run
    testbed_cfg.cleanup()

    # SNAT TEST SECTION:
    print 'Setting up global config for SNAT DP Testing'
    targetVmFips = testbed_cfg.setup('snat', do_config=0)
    gbpverify = Gbp_Verify()
    print testbed_cfg.heat_temp_test, testbed_cfg.heat_stack_name
    objs_uuid = gbpverify.get_uuid_from_stack(
        testbed_cfg.snat_heat_temp, testbed_cfg.heat_stack_name)

    from testcases.testcases_dp_nat.testsuite_snat_vm_to_extgw import SNAT_VMs_to_ExtGw
    test_snat_allvms_to_extgw = SNAT_VMs_to_ExtGw(objs_uuid)
    test_snat_allvms_to_extgw.test_runner()
    # Cleanup after the SNAT Testsuite is run
    testbed_cfg.cleanup()

if __name__ == "__main__":
    main()
