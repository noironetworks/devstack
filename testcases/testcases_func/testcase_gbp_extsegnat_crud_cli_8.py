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
    test = testcase_gbp_extsegnat_crud_cli_8()
    test.test_runner()
    sys.exit(1)


class testcase_gbp_extsegnat_crud_cli_8(object):
    """
    This is a GBP NAT CRUD TestCase
    """
    # Initialize logging
    _log = logging.getLogger()
    hdlr = logging.FileHandler('/tmp/testcase_gbp_extsegnat_crud_cli_8.log')
    #formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    formatter = logging.Formatter('%(asctime)s %(message)s')
    hdlr.setFormatter(formatter)
    _log.addHandler(hdlr)
    _log.setLevel(logging.INFO)

    def __init__(self):

        self.config = Gbp_Config()
        self.verify = Gbp_Verify()
        self.extseg_name = 'Management-Out'

    def test_runner(self):
        """
        Method to run the Testcase in Ordered Steps
        """
        test_name = 'TESTCASE_GBP_EXTERNAL_SEGMENT_CRUD_8'
        # self.write_neutron_conf()
        self._log.info(
            "\nSteps of the TESTCASE_GBP_EXTERNAL_SEGMENT_CRUD_8 to be executed\n")
        testcase_steps = [self.test_step_CreateExternalSeg,
                          self.test_step_CreateMultiL3PolWExtSeg,
                          self.test_step_VerifyExternalSeg,
                          self.test_step_VerifyAllL3Pol,
                          self.test_step_DeleteAllL3Pol,
                          self.test_step_VerifyL3PRemInExternalSeg,
                          self.test_step_DeleteExternalSeg,
                          self.test_step_VerifyExternalSegDel,
                          self.test_step_VerifyAllL3PolDel,
                          self.test_step_VerifyImplicitNeutronObjsDel
                          ]
        for step in testcase_steps:  # TODO: Needs FIX
            try:
                if step() == 0:
                    self._log.info("Test Failed at Step == %s" %
                                   (step.__name__.lstrip('self')))
                    raise TestFailed("%s == FAIL" % (test_name))
            except TestFailed as err:
                self._log.info('\n%s' % (err))
        self._log.info("%s ::PASS" % (test_name))

    def write_neutron_conf(self):
        """
        Write External Segment Section into the Neutron.conf
        Restart the neutron server
        """
        self._log.info(
            "\nWrite ExtSeg Section into Neutron.conf & Restart Neutron Server\n")
        self.config.write_to_conf_file('/etc/neutron/neutron.conf', 'apic_external_network:%s' % (self.extseg_name),
                                       router_id=self.router_id, switch=self.leafnodeid, cidr_exposed=self.cidr,
                                       gateway_ip=self.gateway, port=self.leafport, encap=self.encap)
        getoutput('systemctl restart neutron-server.service')
        sleep(2)

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

    def test_step_CreateMultiL3PolWExtSeg(self):
        """
        Create Multiple L3Policy with External Segment
        """
        self._log.info(
            "\nStep: Create Multiple(n=4) L3 Policies referencing One External Segment\n")
        self.l3p_list = []
        l3p_name_ip_pool_dict = {'l3p_ext_1': '20.20.20.0/24', 'l3p_ext_2': '25.25.25.0/24',
                                 'l3p_ext_3': '30.30.30.0/24', 'l3p_ext_4': '35.35.35.0/24'}
        for key, val in l3p_name_ip_pool_dict.iteritems():
            try:
                l3p_id = self.config.gbp_policy_cfg_all(
                    1, 'l3p', key, ip_pool=val, external_segment='%s=' % (self.extseg_id))
                self.l3p_list.append(l3p_id)
            except Exception as e:
                self._log.info("\nException Error = %s\n" % (e))
                self._log.info(
                    "\nCreate Multiple(n=4) L3 Policies referencing One External Segment failed\n")
                return 0

    def test_step_VerifyExternalSeg(self):
        """
        Step to Verify the External Segment and all L3Policies associated
        """
        self._log.info(
            "\nStep: Verify External Segment and it's associated L3Policies\n")
        if self.verify.gbp_obj_ver_attr_all_values('extseg', self.extseg_id, 'l3_policies', self.l3p_list) == 0:
            self._log.info(
                "\nVerify of External Segment and it's associated L3Policies failed\n")
            return 0

    def test_step_VerifyAllL3Pol(self):
        """
        Step to Verify All the L3Policy
        """
        self._log.info(
            "\nStep: Verify All(n=4) L3Policies and their External Segment\n")
        self.rtr_id_list = []
        for l3p in self.l3p_list:
            try:
                rtr_id = self.verify.gbp_l2l3ntk_pol_ver_all(
                    1, 'l3p', l3p, external_segments=self.extseg_id, ret='default')
                self.rtr_id_list.append(rtr_id)
            except Exception as e:
                self._log.info("\nException Error = %s\n" % (e))
                self._log.info(
                    "\nVerify of L3Policy and its External Segment failed\n")
                return 0

    def test_step_DeleteAllL3Pol(self):
        """
        Delete All L3Policies
        """
        self._log.info("\nStep: Delete All L3Policies\n")
        for l3p in self.l3p_list:
            if self.config.gbp_policy_cfg_all(0, 'l3p', l3p) == 0:
                self._log.info("\nDeletion of L3Policy failed\n")
                return 0

    def test_step_VerifyL3PRemInExternalSeg(self):
        """
        References of L3Policies in External Segment removed
        """
        self._log.info(
            "\nStep: Verify the references of L3Policies got removed from External Segment\n")
        if self.verify.gbp_obj_ver_attr_all_values('extseg', self.extseg_id, 'l3_policies', self.l3p_list) != 0:
            self._log.info(
                "\nReferences of L3Policies still persists in External Segment even after their deletion\n")
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

    def test_step_VerifyAllL3PolDel(self):
        """
        L3Policies got deleted from Dbase
        """
        self._log.info("\nStep: Verify the Deletion of All L3Policies\n")
        for l3p in self.l3p_list:
            if self.verify.gbp_l2l3ntk_pol_ver_all(1, 'l3p', l3p) != 0:
                self._log.info(
                    "\nL3Policy still persists in dbase after deletion\n")
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
        for rtr in self.rtr_id_list:
            if self.verify.neut_ver_all('router', rtr) != 0:
                self._log.info(
                    "\nImplicit Neutron Router still persists in dbase after L3P & Ext-Seg deletion\n")
                return 0

if __name__ == '__main__':
    main()
