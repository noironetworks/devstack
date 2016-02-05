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
    test = testcase_gbp_extsegnat_crud_cli_1()
    test.test_runner()
    sys.exit(1)


class testcase_gbp_extsegnat_crud_cli_1(object):
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
        self.neutron_subnet = '169.254.0.0/25'
        cmd = 'crudini --get /etc/neutron/neutron.conf apic_external_network:%s cidr_exposed' %(self.extseg_name)
        self.cidr = getoutput(cmd)

    def test_runner(self):
        """
        Method to run the Testcase in Ordered Steps
        """
        test_name = 'TESTCASE_GBP_EXTERNAL_SEGMENT_CRUD_1'
        self._log.info(
            "\nSteps of the TESTCASE_GBP_EXTERNAL_SEGMENT_CRUD_1 to be executed\n")
        testcase_steps = [self.test_step_CreateExternalSeg,
                          self.test_step_VerifyExternalSeg,
                          self.test_step_VerifyImplicitNeutronObjs,
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

    def test_step_VerifyExternalSeg(self):
        """
        Step to Verify the External Segment
        """
        self._log.info("\nStep: Verify External Segment\n")
        if self.verify.gbp_policy_verify_all(1, 'extseg', self.extseg_id, name=self.extseg_name, cidr=self.cidr) == 0:
            self._log.info("\nVerify of External Segment failed\n")
            return 0

    def test_step_VerifyImplicitNeutronObjs(self):
        """
        Verify the Implicit Neutron Subnet & Network created as a part of External Segment
        """
        self._log.info(
            "\nStep: Verify Implicitly created Neutron Subnet & Network\n")
        subnet_check = self.verify.neut_ver_all(
            'subnet', self.subnet, ret='network_id', cidr=self.neutron_subnet)
        if subnet_check == 0:
            self._log.info(
                "\nVerify of Implicitly created Neutron Subnet & Network failed\n")
            return 0
        else:
            self.network_id = subnet_check

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
        Verify that Implicit Neutron Subnet & Network got deleted from Dbase
        """
        self._log.info(
            "\nStep: Verify Implicitly Neutron Subnet & Network got deleted\n")
        if self.verify.neut_ver_all('subnet', self.subnet) != 0:
            self._log.info(
                "\nImplicit Neutron Subnet still persists in dbase after ext-seg deletion\n")
            return 0
        if self.verify.neut_ver_all('net', self.network_id) != 0:
            self._log.info(
                "\nImplicit Neutron Network still persists in dbase after ext-seg deletion\n")
            return 0


if __name__ == '__main__':
    main()
