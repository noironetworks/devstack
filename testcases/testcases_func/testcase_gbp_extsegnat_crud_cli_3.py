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


def main():
    # Run the Testcase: # when suite_runner is ready ensure to delete main &
    # __name__ at EOF
    test = testcase_gbp_extsegnat_crud_cli_3()
    test.test_runner()
    sys.exit(1)


class testcase_gbp_extsegnat_crud_cli_3(object):
    """
    This is a GBP NAT CRUD TestCase
    """
    # Initialize logging
    _log = logging.getLogger()
    hdlr = logging.FileHandler('/tmp/testcase_gbp_extsegnat_crud_cli_3.log')
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

    def test_runner(self):
        """
        Method to run the Testcase in Ordered Steps
        """
        test_name = 'TESTCASE_GBP_EXTERNAL_SEGMENT_CRUD_3'
        self._log.info(
            "\nSteps of the TESTCASE_GBP_EXTERNAL_SEGMENT_CRUD_3 to be executed\n")
        testcase_steps = [self.test_step_CreateExternalSeg,
                          self.test_step_CreateNaTPool,
                          self.test_step_VerifyExternalSeg,
                          self.test_step_VerifyNatPool,
                          self.test_step_DeleteNatPool,
                          self.test_step_DeleteExternalSeg,
                          self.test_step_VerifyExternalSegDel,
                          self.test_step_VerifyNatPoolDel,
                          self.test_step_VerifyImplicitNeutronObjsDel
                          ]
        failed = 0
        for step in testcase_steps:
            if step() == 0:
                    self._log.info("Test Failed at Step == %s" %
                                   (step.__name__.lstrip('self')))
                    self._log.info("On Cleanup deleting configured objects")
                    self.test_step_DeleteNatPool
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

    def test_step_CreateNaTPool(self):
        """
        Create the NAT Pool with reference to the existing External Segment
        """
        self._log.info(
            "\nStep: Create the NAT Pool with reference to the existing External Segment\n")
        self.natpool_id = self.config.gbp_policy_cfg_all(
            1, 'natpool', self.nat_pool_name, ip_pool=self.natippool, external_segment=self.extseg_id)
        if self.natpool_id == 0:
            self._log.info(
                "\nCreate the NAT Pool with reference to the existing External Segment failed\n")
            return 0

    def test_step_VerifyExternalSeg(self):
        """
        Step to Verify the External Segment with NAT Pool
        """
        self._log.info("\nStep: Verify External Segment and its NAT Pool\n")
        if self.verify.gbp_policy_verify_all(1, 'extseg', self.extseg_id, name=self.extseg_name, cidr=self.cidr, nat_pools=self.natpool_id) == 0:
            self._log.info(
                "\nVerify of External Segment and its NAT Pool failed\n")
            return 0

    def test_step_VerifyNatPool(self):
        """
        Step to Verify the NAT Pool
        """
        self._log.info("\nStep: Verify NAT Pool and its External Segment\n")
        if self.verify.gbp_policy_verify_all(1, 'natpool', self.natpool_id, name=self.nat_pool_name, ip_pool=self.natippool, external_segment_id=self.extseg_id) == 0:
            self._log.info(
                "\nVerify of NAT Pool and its External Segment failed\n")
            return 0

    def test_step_DeleteNatPool(self):
        """
        Delete NAT Pool
        """
        self._log.info("\nStep: Delete NAT Pool\n")
        if self.config.gbp_policy_cfg_all(0, 'natpool', self.natpool_id) == 0:
            self._log.info("\nDeletion of NAT Pool failed\n")
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

    def test_step_VerifyNatPoolDel(self):
        """
        NAT Pool got deleted from Dbase
        """
        self._log.info("\nStep: Verify the Deletion of NAT Pool\n")
        if self.verify.gbp_policy_verify_all(1, 'natpool', self.natpool_id) != 0:
            self._log.info(
                "\nNAT Pool still persists in dbase after deletion\n")
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

if __name__ == '__main__':
    main()
