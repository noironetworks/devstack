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


class NatFuncTestMethods(object):
    """
    This is a GBP NAT Functionality TestCase
    """
    # Initialize logging
    _log = logging.getLogger()
    hdlr = logging.FileHandler('/tmp/nattestmethod.log')
    #formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    formatter = logging.Formatter('%(asctime)s %(message)s')
    hdlr.setFormatter(formatter)
    _log.addHandler(hdlr)
    _log.setLevel(logging.INFO)

    def __init__(self,cntlrip):

        self.config = Gbp_Config()
        self.verify = Gbp_Verify()
        self.gbpcrud = GBPCrud(cntlrip)
        self.gbpnova = Gbp_Nova(cntlrip)
        self.extsegname = 'Management-Out'
        self.natpoolname = 'GbpNatPool'
        self.natippool = '110.110.110.0/24'
        self.l3pname = 'L3PNat'
        self.l3pippool = '20.20.20.0/24'
        self.l3ppreflen = 26
        self.l2pname = 'L2PNat'
        self.ptg1name = 'TestPtg1'
        self.ptg2name = 'TestPtg2'
        self.extpolname = 'ExtPolTest'
        self.vm1name = 'TestVM1'
        self.vm2name = 'TestVM2'
     

    def testCreateExtSegWithDefault(self):
        """
        Create External Segment
        """
        self._log.info("\nStep: Create External Segment\n")
        self.extsegid = self.gbpcrud.create_gbp_external_segment(
                                       self.extsegname)
        if self.extsegid == 0:
            self._log.error("\nStep: External Segment Creation failed")
            return 0

    def testCreateNatPoolAssociateExtSeg(self):
        """
        Create a NAT pool and associate the existing External Segment
        """
        self._log.info(
            "\nStep: Create a NAT pool and associate the existing External Segment\n")
        self.nat_pool_id = self.gbpcrud.create_gbp_nat_pool(
                                        self.natpoolname,
                                        ip_pool = self.natippool,
                                        external_segment_id = self.extsegid)
        if self.nat_pool_id == 0:
            self._log.error(
                "\nCreate the NAT pool with reference to the existing External Segment failed")
            return 0

    def testCreatePtgDefaultL3p(self):
        """
        Step to Create Policy Target group with Default L3
        Fetch the UUID of the 'default' L3Policy
        """
        self._log.info(
                  "\nStep: Create Policy Target group with Default L3\n")
        self.ptg1id = self.gbpcrud.create_gbp_policy_target_group(
                                     self.ptg1name)
        if self.ptg1id == 0:
            self._log.info(
                "\nCreate Policy Target group with Default L3 failed\n")
            return 0
        self.defaultl3pid = self.gbpcrud.verify_gbp_l3policy('default') 
        if self.defaultl3pid == 0:
           self._log.error(
                "\nFailed to fetch UUID of Default L3P\n")
           return 0

    def testCreateNonDefaultL3pAndL2p(self):
        """
        Step to Create Non-default L3P
        """
        self._log.info("\nStep: Create non-default L3Policy and L2Policy\n")
        self.nondefaultl3pid = self.gbpcrud.create_gbp_l3policy(
                                               self.l3pname,
                                               ip_pool=self.l3pippool,
                                               subnet_prefix_length=self.l3ppreflen)
        if self.nondefaultl3pid == 0:
            self._log.info(
                "\nCreation of non-default L3Policy failed\n")
            return 0
        self.l2policy_id = self.gbpcrud.create_gbp_l2policy(
                                self.l2pname,
                                l3_policy_id=self.nondefaultl3pid)
        if self.l2policy_id == 0:
            self._log.error(
                "\nCreation of non-default L2Policy failed\n")
            return 0

    def testCreatePtgWithNonDefaultL3p(self):
        """
        Step to Create Policy Target group with Created L3
        """
        self._log.info("\nStep: Create Policy Target group with Created L3\n")
        self.ptg2id = self.gbpcrud.create_gbp_policy_target_group(
                                     self.ptg2name,
                                     l2_policy_id=self.l2policy_id)
        if self.ptg2id == 0:
            self._log.error(
                "\nCreate Policy Target group with non-default L3Policy failed\n")
            return 0

    def testAssociateExtSegToBothL3ps(self):
        """
        Step to Associate External Segment to 
        both default & non-default L3Ps
        """
        self._log.info(
                     "\nStep: Associate External Segment to both L3Ps\n")
        for l3p in [self.defaultl3pid,self.nondefaultl3pid]:
            if self.gbpcrud.update_gbp_l3policy(l3p,property_type='uuid',external_segments=self.extsegid) == 0:
               self._log.error(
                     "\nAssociate External Segment to L3P failed\n")
               return 0
        
    def testCreatePolicyTargetForEachPtg(self):
        """
        Created Port Targets
        """
        self._log.info(
                 "\nStep: Create Policy Targets for each of the two PTGs \n")
        self.pt1id = self.gbpcrud.create_gbp_policy_target('pt1', self.ptg1name, 1)
        if self.pt1id == 0:
            self._log.error("\nCreation of Policy Targe failed for PTG=%s\n" %(self.ptg1name))
            return 0
        self.pt2id = self.gbpcrud.create_gbp_policy_target('pt2', self.ptg2name, 1)
        if self.pt2id == 0:
            self._log.error("\nCreation of Policy Targe failed for PTG=%s\n" %(self.ptg2name))
            return 0

    def testCreateExternalPolicy(self):
        """
        Create ExtPolicy with ExtSegment
        Apply Policy RuleSets
        """
        self._log.info(
                 "\nStep: Create ExtPolicy with ExtSegment and Apply PolicyRuleSets\n")
        self.extpol_uuid = self.gbpcrud.create_gbp_external_policy(self.extpolname,
                                                 external_segments=[self.extsegid])
        print 'ExtPolUUID', self.extpol_uuid

    def testVerifyCfgdObjects(self):
        """
        Verify all the configured objects and their atts
        """
        self._log.info(
                 "\nStep: Verify the Configured Objects and their Attributes\n")
        if self.gbpcrud.verify_gbp_any_object('l3_policy',
                                               self.nondefaultl3pid,
                                               external_segments = self.extsegid,
                                               l2_policies = self.l2policy_id,
                                               ip_pool = self.l3pippool
                                              ) == 0:  
           return 0
        if self.gbpcrud.verify_gbp_any_object('l2_policy',
                                               self.l2policy_id,
                                               l3_policy_id = self.nondefaultl3pid,
                                               policy_target_groups = self.ptg2id
                                              ) == 0:
           return 0
        if self.gbpcrud.verify_gbp_any_object('external_segment',
                                               self.extsegid,
                                               l3_policies = [self.defaultl3pid,
                                                              self.nondefaultl3pid],
                                               nat_pools = self.nat_pool_id,
                                               external_policies = self.extpol_uuid
                                              ) == 0:
           return 0

    def testLaunchVmsForEachPt(self):
        """
        Lanuch VMs
        """
        self._log.info("\nStep: Launch VMs\n")
        
        # launch Nova VMs
        if self.gbpnova.vm_create_api(self.vm1name,
                                      'ubuntu_multi_nics',
                                      self.pt1id[1]) == 0:
           self._log.error(
                "\n VM Create using PTG %s Failed" %(self.ptg1name))
           return 0
        if self.gbpnova.vm_create_api(self.vm2name,
                                      'ubuntu_multi_nics',
                                      self.pt2id[1]) == 0:
           self._log.error(
                "\n VM Create using PTG %s Failed" %(self.ptg2name))
           return 0


    def testAssociateFipToVMs(self):
        """
        Associate FIPs to VMs
        """
        self._log.info("\nStep: Associate FIPs to VMs\n")
        for vm in [self.vm1name,self.vm2name]:
            if self.gbpnova.action_fip_to_vm(
                                            'associate',
                                            vm,
                                            extsegname='Management-Out'
                                            ) == 0:
               self._log.error(
                        "\n Associating FIP to VM %s" %(vm))
               return 0


    def testTrafficFromExtRtrToVmFip(self,action,obj=None,uuid=''):
        """
        Ping and TCP test from external router to VMs
        """
        self._log.info("\nStep: Ping and TCP test from external router\n")
        
    def DeleteOrCleanup(self,action,obj=None,uuid=''):
        """
        Specific Delete or Blind Cleanup
        """
        if action == 'delete':
           if obj == 'external_segment' and uuid != '':
              self.gbpcrud.delete_gbp_external_segment(uuid)
           elif obj == 'nat_pool' and uuid != '':
              self.gbpcrud.delete_gbp_nat_pool(uuid)
           elif obj == 'external_policy' and uuid != '':
              self.gbpcrud.delete_gbp_external_policy(uuid)
           elif obj == 'policy_target_group' and uuid != '':
              self.gbpcrud.delete_gbp_policy_target_group(uuid)
           else:
              self._log.info("\n Incorrect params passed for delete action")
        if action == 'cleanup':
           for vm in [self.vm1name, self.vm2name]:
               self.gbpnova.vm_delete(vm)
           pt_list = self.gbpcrud.get_gbp_policy_target_list()
           if len(pt_list) > 0:
              for pt in pt_list:
                self.gbpcrud.delete_gbp_policy_target(pt, property_type='uuid')
           ptg_list = self.gbpcrud.get_gbp_policy_target_group_list()
           if len(ptg_list) > 0:
              for ptg in ptg_list:
                self.gbpcrud.delete_gbp_policy_target_group(ptg, property_type='uuid')
           l2p_list = self.gbpcrud.get_gbp_l2policy_list()
           if len(l2p_list) > 0:
              for l2p in l2p_list:
                 self.gbpcrud.delete_gbp_l2policy(l2p, property_type='uuid')
           l3p_list = self.gbpcrud.get_gbp_l3policy_list()
           if len(l3p_list) > 0:
              for l3p in l3p_list:
                 self.gbpcrud.delete_gbp_l3policy(l3p, property_type='uuid')
           natpool_list = self.gbpcrud.get_gbp_nat_pool_list()
           if len(natpool_list) > 0:
              for natpool in natpool_list:
                 self.gbpcrud.delete_gbp_nat_pool(natpool, property_type='uuid')
           extpol_list = self.gbpcrud.get_gbp_external_policy_list()
           if len(extpol_list) > 0:
              for extpol in extpol_list:
                 self.gbpcrud.delete_gbp_external_policy(extpol, property_type='uuid')
           extseg_list = self.gbpcrud.get_gbp_external_segment_list()
           if len(extseg_list) > 0:
              for extseg in extseg_list:
                 self.gbpcrud.delete_gbp_external_segment(extseg, property_type='uuid')
             
