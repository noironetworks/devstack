#!/usr/bin/python

import sys
import logging
import os
import datetime
import string
from time import sleep
from libs.gbp_conf_libs import Gbp_Config
from libs.gbp_verify_libs import Gbp_Verify
from libs.raise_exceptions import *
from libs.gbp_aci_libs import Gbp_Aci
from commands import *


class testcase_gbp_extsegnat_crud_cli_7(object):
    """
    This is a GBP NAT CRUD TestCase
    """
    # Initialize logging
    _log = logging.getLogger()
    hdlr = logging.FileHandler('/tmp/testcase_gbp_extsegnat_crud_cli.log')
    #formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    formatter = logging.Formatter('%(asctime)s %(message)s')
    hdlr.setFormatter(formatter)
    _log.addHandler(hdlr)
    _log.setLevel(logging.INFO)

    def __init__(self):

        self.config = Gbp_Config()
        self.verify = Gbp_Verify()
        self.extseg_name = 'Management-Out'
        self.natippool = '100.100.100.0/24'
        self.nat_pool_name = 'testnatpool'
        self.neutron_subnet = '169.254.0.0/25'
        cmd = 'crudini --get /etc/neutron/neutron.conf apic_external_network:%s cidr_exposed' %(self.extseg_name)
        self.cidr = getoutput(cmd)
        self.l3policy_name = 'l3pext'
        self.ptg_name = 'test_ptg'

    def test_runner(self):
        """
        Method to run the Testcase in Ordered Steps
        """
        test_name = 'TESTCASE_GBP_EXTERNAL_SEGMENT_CRUD_7'
        self._log.info(
            "\nSteps of the TESTCASE_GBP_EXTERNAL_SEGMENT_CRUD_7 to be executed\n")
        testcase_steps = [self.test_step_CreateExternalSeg,
                          self.test_step_CreatePtg,
                          self.test_step_UpdateDefL3PolWExtSeg,
                          self.test_step_VerifyExternalSeg,
                          self.test_step_VerifyL3Pol,
                          self.test_step_DeletePtg,
                          self.test_step_VerifyL3PInExternalSeg,
                          self.test_step_DeleteExternalSeg,
                          self.test_step_VerifyExternalSegDel,
                          self.test_step_VerifyImplicitNeutronObjsDel
                          ]
        failed = 0
        for step in testcase_steps:
            if step() == 0:
                    self._log.info("Test Failed at Step == %s" %
                                   (step.__name__.lstrip('self')))
                    self._log.info("On Cleanup deleting configured objects")
                    self.test_step_DeletePtg()
                    self.test_step_DeleteNatPool()
                    self.test_step_DeleteExternalSeg()
                    failed +=1
                    break
        if failed > 0:
           self._log.info("%s == FAIL" % (test_name))
        else:
           self._log.info("%s == PASS" % (test_name))


    def test_step_CreateExternalSeg(self):
        """
        Create External Segment
        """
        self._log.info("\nStep: Create External Segment\n")
        extseg = self.config.gbp_policy_cfg_all(1, 'extseg', self.extseg_name)
        if extseg == 0:
            self._log.info("\nExternal Segment Creation failed\n")
            return 0
        else:
            self.extseg_id = extseg[0]
            self.subnet = extseg[1]

    def test_step_CreatePtg(self):
        """
        Create the PTG, implicit L3Policy created
        """
        self._log.info(
            "\nStep: Create the PTG, implicit L3Policy gets created\n")
        try:
            self.l2p_id = self.config.gbp_policy_cfg_all(
                1, 'group', self.ptg_name)[1]
            self.l3p_id = self.verify.gbp_l2l3ntk_pol_ver_all(
                1, 'l2p', self.l2p_id, ret='default')[0]
        except Exception as e:
            self._log.info("\nException Error: %s\n" % (e))
            self._log.info("\nCreate of PTG failed\n")
            return 0

    def test_step_UpdateDefL3PolWExtSeg(self):
        """
        Update the Default L3Policy to associate an External Segment
        """
        self._log.info(
            "\nStep: Update the L3Policy with the existing External Segment\n")
        if self.config.gbp_policy_cfg_all(2, 'l3p', self.l3p_id, external_segment='%s=' % (self.extseg_id)) == 0:
            self._log.info(
                "\nUpdating the Default L3 Policy with External Seg failed\n")
            return 0

    def test_step_VerifyExternalSeg(self):
        """
        Step to Verify the External Segment with L3Policy
        """
        self._log.info("\nStep: Verify External Segment and its L3Policy\n")
        if self.verify.gbp_policy_verify_all(1, 'extseg', self.extseg_id, name=self.extseg_name, cidr=self.cidr, l3_policies=self.l3p_id) == 0:
            self._log.info(
                "\nVerify of External Segment and its L3Policy failed\n")
            return 0

    def test_step_VerifyL3Pol(self):
        """
        Step to Verify the Default L3Policy with External Segment
        """
        self._log.info(
            "\nStep: Verify Default L3Policy and its External Segment\n")
        self.rtr_id = self.verify.gbp_l2l3ntk_pol_ver_all(
            1, 'l3p', self.l3p_id, external_segments=self.extseg_id, ret='default')
        if self.rtr_id == 0:
            self._log.info(
                "\nVerify of L3Policy and its External Segment failed\n")
            return 0

    def test_step_DeletePtg(self):
        """
        Delete PTG
        """
        self._log.info("\nStep: Delete PTG\n")
        if self.config.gbp_policy_cfg_all(0, 'group', self.ptg_name) == 0:
            self._log.info("\nDeletion of PTG failed\n")
            return 0

    def test_step_VerifyL3PInExternalSeg(self):
        """
        Default L3Policy reference deleted from External Segment
        """
        self._log.info(
            "\nStep: Verify Default L3Policy reference deleted from External Segment\n")
        if self.verify.gbp_policy_verify_all(1, 'extseg', self.extseg_id, l3_policies=self.l3p_id) != 0:
            self._log.info(
                "\nDeleted L3Policy still persists in External Segment\n")
            return 0

    def test_step_DeleteExternalSeg(self):
        """
        Delete External Segment
        """
        self._log.info("\nStep: Delete External Segment\n")
        if self.config.gbp_policy_cfg_all(0, 'extseg', self.extseg_name) == 0:
            self._log.info("\nDeletion of External Segment failed\n")
            return 0

    def test_step_VerifyExternalSegDel(self):
        """
        External Segment got deleted from Dbase
        """
        self._log.info("\nStep: Verify the Deletion of External Segment\n")
        if self.verify.gbp_policy_verify_all(1, 'extseg', self.extseg_id) != 0:
            self._log.info(
                "\nExternal Segment still persists in dbase after deletion\n")
            return 0

    def test_step_VerifyImplicitNeutronObjsDel(self):
        """
        Verify that Implicit Neutron Subnet got deleted from Dbase
        """
        self._log.info(
            "\nStep: Verify Implicitly Neutron Subnet got deleted\n")
        if self.verify.neut_ver_all('subnet', self.subnet) != 0:
            self._log.info(
                "\nImplicit Neutron Subnet still persists in dbase after ext-seg deletion\n")
            return 0
        self._log.info(
            "\nStep: Verify Implicitly Neutron Router got deleted\n")
        if self.verify.neut_ver_all('router', self.rtr_id) != 0:
            self._log.info(
                "\nImplicit Neutron Router still persists in dbase after L3P & Ext-Seg deletion\n")
            return 0

if __name__ == '__main__':
    main()
