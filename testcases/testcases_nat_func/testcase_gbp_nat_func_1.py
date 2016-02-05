#!/usr/bin/python

from commands import *
import datetime
import logging
import os
import string
import sys
from time import sleep

from libs.gbp_aci_libs import Gbp_Aci
from libs.gbp_conf_libs import Gbp_Config
from libs.gbp_crud_libs import GBPCrud
from libs.gbp_verify_libs import Gbp_Verify
from libs.gbp_nova_libs import Gbp_Nova
from libs.raise_exceptions import *


def main():
    # Run the Testcase: # when suite_runner is ready ensure to delete main &
    # __name__ at EOF
    test = testcase_gbp_nat_func_1()
    test.test_runner()
    sys.exit(1)


class testcase_gbp_nat_func_1(object):
    """
    This is a GBP NAT Functionality TestCase
    """
    # Initialize logging
    _log = logging.getLogger()
    hdlr = logging.FileHandler('/tmp/testcase_gbp_nat_func_1.log')
    #formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    formatter = logging.Formatter('%(asctime)s %(message)s')
    hdlr.setFormatter(formatter)
    _log.addHandler(hdlr)
    _log.setLevel(logging.INFO)

    def __init__(self):

        self.config = Gbp_Config()
        self.verify = Gbp_Verify()
        #self.ostack_controller = params['cntlr_ip']
        self.ostack_controller = '172.28.184.35'
        self.gbp_crud = GBPCrud(self.ostack_controller)
        self.gbp_nova = Gbp_Nova(self.ostack_controller)
        #self.ruleset_name = params['ruleset_name']
        #self.l3p_name = params['l3_policy_name']
        self.extseg_name = 'Management-Out'
        self.nat_pool_name = 'test_nat_pool'
        self.nat_ip_pool = '110.110.110.0/24'
        self.l3pname = 'L3PNat'
        self.l3pippool = '20.20.20.0/24'
        self.l3ppreflen = 26
        self.l2pname = 'L2PNat'
        self.ptg1_name = 'TestPtg1'
        self.ptg2_name = 'TestPtg2'
        self.extpol_name = 'ExtPolTest'
         
    def test_runner(self):
        """
        Method to run the Testcase in Ordered Steps
        """
        test_name = 'TESTCASE_GBP_NAT_FUNC_5'
        #self.get_global_config()
        self._log.info(
            "\nSteps of the TESTCASE_GBP_NAT_FUNC_1 to be executed\n")
        testcase_steps = [self.test_create_ext_seg_with_default,
                          self.test_create_nat_pool_associate_ext_seg,
                          self.test_create_ptg_default_l3p,
                          self.test_create_non_default_l3p_and_l2p,
                          self.test_create_ptg_with_nondefault_l3p,
                          self.test_associate_ext_seg_to_both_l3ps,
                          self.test_create_policy_target_for_each_ptg,
                          self.test_create_external_policy,
                          #self.test_launch_vms_each_pt,
                          #self.test_associate_fip_to_VMs,
                          #self.test_ping_and_tcp_from_ext_rtr,
                          ]
        for step in testcase_steps:  # TODO: Needs FIX
            try:
                if step() == 0:
                    self._log.error("Test Failed at Step == %s" %
                                   (step.__name__.lstrip('self')))
                    raise TestFailed("%s == FAIL" % (test_name))
            except TestFailed as err:
                self._log.info('\n%s' % (err))
        self._log.info("%s == PASS" % (test_name))

    def get_global_config(self):
        """
        Write External Segment Section into the Neutron.conf
        Restart the neutron server
        """
        self._log.info("\nGet Global config UUIDs\n")
        return 1 #JISHNU
        #self.prs_uuid = self.gbp_crud.verify_gbp_policy_rule_set(
        #                              self.ruleset_name)
        
        #self.l3p_uuid = self.gbp_crud.verify_gbp_l3policy(self.l3p_name)

    def test_create_ext_seg_with_default(self):
        """
        Create External Segment
        """
        self._log.info("\nStep: Create External Segment\n")
        self.extseg_id = self.gbp_crud.create_gbp_external_segment(
                                       self.extseg_name)
        if self.extseg_id == 0:
            self._log.error("\nStep: External Segment Creation failed")
            return 0

    def test_create_nat_pool_associate_ext_seg(self):
        """
        Create a NAT pool and associate the existing External Segment
        """
        self._log.info(
            "\nStep: Create a NAT pool and associate the existing External Segment\n")
        self.nat_pool_id = self.gbp_crud.create_gbp_nat_pool(
                                        self.nat_pool_name,
                                        ip_pool = self.nat_ip_pool,
                                        external_segment_id = self.extseg_id)
        if self.nat_pool_id == 0:
            self._log.error(
                "\nCreate the NAT pool with reference to the existing External Segment failed")
            return 0

    def test_create_ptg_default_l3p(self):
        """
        Step to Create Policy Target group with Default L3
        Fetch the UUID of the 'default' L3Policy
        """
        self._log.info(
                  "\nStep: Create Policy Target group with Default L3\n")
        self.ptg1_id = self.gbp_crud.create_gbp_policy_target_group(
                                     self.ptg1_name)
        if self.ptg1_id == 0:
            self._log.info(
                "\nCreate Policy Target group with Default L3 failed\n")
            return 0
        self.default_l3p_id = self.gbp_crud.verify_gbp_l3policy('default') 
        if self.default_l3p_id == 0:
           self._log.error(
                "\nFailed to fetch UUID of Default L3P\n")
           return 0

    def test_create_non_default_l3p_and_l2p(self):
        """
        Step to Create Non-default L3P
        """
        self._log.info("\nStep: Create non-default L3Policy and L2Policy\n")
        self.nondefault_l3p_id = self.gbp_crud.create_gbp_l3policy(
                                               self.l3pname,
                                               ip_pool=self.l3pippool,
                                               subnet_prefix_length=self.l3ppreflen)
        if self.nondefault_l3p_id == 0:
            self._log.info(
                "\nCreation of non-default L3Policy failed\n")
            return 0
        self.l2policy_id = self.gbp_crud.create_gbp_l2policy(
                                self.l2pname,
                                l3_policy_id=self.nondefault_l3p_id)
        if self.l2policy_id == 0:
            self._log.error(
                "\nCreation of non-default L2Policy failed\n")
            return 0

    def test_create_ptg_with_nondefault_l3p(self):
        """
        Step to Create Policy Target group with Created L3
        """
        self._log.info("\nStep: Create Policy Target group with Created L3\n")
        self.ptg2_id = self.gbp_crud.create_gbp_policy_target_group(
                                     self.ptg2_name,
                                     l2_policy_id=self.l2policy_id)
        if self.ptg2_id == 0:
            self._log.error(
                "\nCreate Policy Target group with non-default L3Policy failed\n")
            return 0

    def test_associate_ext_seg_to_both_l3ps(self):
        """
        Step to Associate External Segment to 
        both default & non-default L3Ps
        """
        self._log.info(
                     "\nStep: Associate External Segment to both L3Ps\n")
        for l3p in [self.default_l3p_id,self.nondefault_l3p_id]:
            if self.gbp_crud.update_gbp_l3policy(l3p,property_type='uuid',external_segments=self.extseg_id) == 0:
               self._log.error(
                     "\nAssociate External Segment to L3P failed\n")
               return 0
        
    def test_create_policy_target_for_each_ptg(self):
        """
        Created Port Targets
        """
        self._log.info(
                 "\nStep: Create Policy Targets for each of the two PTGs \n")
        self.pt1_id = self.gbp_crud.create_gbp_policy_target('pt1', self.ptg1_name, 1)
        if self.pt1_id == 0:
            self._log.error("\nCreation of Policy Targe failed for PTG=%s\n" %(self.ptg1_name))
            return 0
        self.pt2_id = self.gbp_crud.create_gbp_policy_target('pt2', self.ptg2_name, 1)
        if self.pt2_id == 0:
            self._log.error("\nCreation of Policy Targe failed for PTG=%s\n" %(self.ptg2_name))
            return 0

    def test_create_external_policy(self):
        """
        Create ExtPolicy with ExtSegment
        Apply Policy RuleSets
        """
        self._log.info(
                 "\nStep: Create ExtPolicy with ExtSegment and Apply PolicyRuleSets\n")
        extpol_uuid = self.gbp_crud.create_gbp_external_policy(self.extpol_name,
                                                 external_segments=[self.extseg_id])
        print 'ExtPolUUID', extpol_uuid
    def test_launch_vms_each_pt(self):
        """
        Lanuch VMs
        """
        self._log.info("\nStep: Launch VMs\n")
        
        # launch Nova VMs
        self.gbp_nova.vm_create_api('TestVM','ubuntu_multi_nics',self.pt1_id[1])

    def test_associate_fip_to_VMs(self):
        """
        Associate FIPs to VMs
        """
        self._log.info("\nStep: Associate FIPs to VMs\n")

    def test_ping_and_tcp_from_ext_rtr(self):
        """
        Ping and TCP test from external router to VMs
        """
        self._log.info("\nStep: Ping and TCP test from external router\n")
        

if __name__ == '__main__':
    main()

