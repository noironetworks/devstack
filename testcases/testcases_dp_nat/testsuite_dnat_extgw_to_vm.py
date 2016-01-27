#!/usr/bin/env python

import sys
import logging
import os
import datetime
import pprint
import string
import uuid
from libs.gbp_crud_libs import GBPCrud
from libs.raise_exceptions import *
from traff_from_extgw import *
from libs.gbp_utils import *


class DNAT_ExtGw_to_VMs(object):

    # Initialize logging
    # logging.basicConfig(level=logging.INFO)
    _log = logging.getLogger(__name__)
    _log.setLevel(logging.INFO)
    # create a logfile handler
    hdlr = logging.FileHandler('/tmp/testsuite_dnat_extgw_to_vms.log')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    hdlr.setFormatter(formatter)
    # Add the handler to the logger
    _log.addHandler(hdlr)

    def __init__(self, objs_uuid, dest_vm_fips):
        """
        Traffic Test Class between ExternalGWRtr and Tenant VM
        VMs/Endpoints behind Border and Non-Border Leaf
        In this class we send Traffic b/w ExtGWRtr and end-points
        Web-Server(compnode-1)
        And App-Server(compnode-2)
        """
        self.extgwrtr = objs_uuid['external_gw']
        self.ostack_controller = objs_uuid['ostack_controller']
        self.external_pol_1 = objs_uuid['public_external_policy_id']
        self.external_pol_2 = objs_uuid['mgmt_external_policy_id']
        self.websrvr_ptg = objs_uuid['web_srvr_ptg_id']
        self.webclnt_ptg = objs_uuid['web_clnt_ptg_id']
        self.appsrvr_ptg = objs_uuid['app_ptg_id']
        self.test_2_prs = {objs_uuid['shared_ruleset_norule_id']}
        self.test_3_prs = {objs_uuid['shared_ruleset_icmp_id']}
        self.test_4_prs = {objs_uuid['shared_ruleset_tcp_id']}
        self.test_5_prs = {objs_uuid['shared_ruleset_icmp_tcp_id']}
        self.dest_vm_fips = dest_vm_fips
        self.gbp_crud = GBPCrud(self.ostack_controller)
        # Add external routes to the Shadow L3Out
        self.gbp_crud.gbp_ext_route_add_to_extseg_util(self.ext_seg_2,'Datacenter-Out')
        self.gbp_crud.gbp_ext_route_add_to_extseg_util(self.ext_seg_2,'Management-Out')


    def test_runner(self, vpc=0):
        """
        Method to run all testcases
        """
        # Note: Cleanup per testcases is not required,since every testcase
        # updates the PTG, hence over-writing previous attr vals
        test_list = [
            self.test_1_traff_with_no_prs,
            self.test_2_traff_app_prs_no_rule,
            self.test_3_traff_apply_prs_icmp,
            self.test_4_traff_apply_prs_tcp,
            self.test_5_traff_apply_prs_icmp_tcp,
            self.test_6_traff_rem_prs
        ]
        test_results = {}
        for test in test_list:
                repeat_test = 1
                while repeat_test < 4:
                  if test() == 1:
                     break
                  self._log.warning("Repeat Run of the Testcase = %s" %(test.__name__.lstrip('self.')))
                  repeat_test += 1
                if repeat_test == 4:
                    test_results[string.upper(test.__name__.lstrip('self.'))] = 'FAIL'
                    self._log.error("\n%s_%s == FAIL" % (
                        self.__class__.__name__.upper(), string.upper(test.__name__.lstrip('self.'))))
                else:
                    test_results[string.upper(test.__name__.lstrip('self.'))] = 'PASS'
                    self._log.info("\n%s_%s == PASS" % (
                        self.__class__.__name__.upper(), string.upper(test.__name__.lstrip('self.'))))
        pprint.pprint(test_results)

    def test_1_traff_with_no_prs(self):
        """
        Run traff test with NO CONTRACT between External PTG & Tenant PTG
        """
        self._log.info(
            "\nTestcase_DNAT_EXTGWRTR_TO_TENANT_VMs: NO CONTRACT APPLIED and VERIFY TRAFFIC")
        run_traffic = traff_from_extgwrtr(self.extgwrtr, self.dest_vm_fips)
        if not isinstance(run_traffic, dict):
            self._log.info(
                "\nFollowing Traffic Test from External GW Router Allowed, hence Failed == %s" % (run_traffic))
            return 0
        else:
            return 1

    def test_2_traff_app_prs_no_rule(self):
        """
        Update the in-use PTG with a PRS which has NO-Rule
        Send traff
        """
        self._log.info(
            "\nTestcase_DNAT_EXTGWRTR_TO_TENANT_VMs: APPLY CONTRACT BUT NO RULE and VERIFY TRAFFIC")
        prs = self.test_2_prs
        for ext_pol in [self.external_pol_1, self.external_pol_2]:
            if self.gbp_crud.update_gbp_external_policy(ext_pol, property_type='uuid', consumed_policy_rulesets=prs) == 0:
                return 0
        for ptg in [self.websrvr_ptg, self.webclnt_ptg, self.appsrvr_ptg]:
            if self.gbp_crud.update_gbp_policy_target_group(ptg, property_type='uuid', provided_policy_rulesets=prs) == 0:
                return 0
        run_traffic = traff_from_extgwrtr(self.extgwrtr, self.dest_vm_fips)
        if not isinstance(run_traffic, dict):
            self._log.info(
                "\nFollowing Traffic Test from External GW Router Allowed, hence Failed == %s" % (run_traffic))
            return 0
        else:
            return 1

    def test_3_traff_apply_prs_icmp(self):
        """
        Apply Policy-RuleSet to the in-use PTG
        Send traffic
        """
        self._log.info(
            "\nTestcase_DNAT_EXTGWRTR_TO_TENANT_VMs: APPLY ICMP CONTRACT and VERIFY TRAFFIC")
        prs = self.test_3_prs
        for ext_pol in [self.external_pol_1, self.external_pol_2]:
            if self.gbp_crud.update_gbp_external_policy(ext_pol, property_type='uuid', consumed_policy_rulesets=prs) == 0:
                return 0
        for ptg in [self.websrvr_ptg, self.webclnt_ptg, self.appsrvr_ptg]:
            if self.gbp_crud.update_gbp_policy_target_group(ptg, property_type='uuid', provided_policy_rulesets=prs) == 0:
                return 0
        run_traffic = traff_from_extgwrtr(
            self.extgwrtr, self.dest_vm_fips, proto='icmp')
        if isinstance(run_traffic, dict):
            self._log.info(
                "\nFollowing Traffic Test from External GW Router Failed == %s" % (run_traffic))
            return 0
        else:
            return 1

    def test_4_traff_apply_prs_tcp(self):
        """
        Apply Policy-RuleSet to the in-use PTG
        Send traffic
        """
        self._log.info(
            "\nTestcase_DNAT_EXTGWRTR_TO_TENANT_VMs: APPLY TCP CONTRACT and VERIFY TRAFFIC")
        prs = self.test_4_prs
        for ext_pol in [self.external_pol_1, self.external_pol_2]:
            if self.gbp_crud.update_gbp_external_policy(ext_pol, property_type='uuid', consumed_policy_rulesets=prs) == 0:
                return 0
        for ptg in [self.websrvr_ptg, self.webclnt_ptg, self.appsrvr_ptg]:
            if self.gbp_crud.update_gbp_policy_target_group(ptg, property_type='uuid', provided_policy_rulesets=prs) == 0:
                return 0
        run_traffic = traff_from_extgwrtr(
            self.extgwrtr, self.dest_vm_fips, proto='tcp')
        if isinstance(run_traffic, dict):
            self._log.info(
                "\nFollowing Traffic Test from External GW Router Failed == %s" % (run_traffic))
            return 0
        else:
            return 1

    def test_5_traff_apply_prs_icmp_tcp(self):
        """
        Apply Policy-RuleSet to the in-use PTG
        Send traffic
        """
        self._log.info(
            "\nTestcase_DNAT_EXTGWRTR_TO_TENANT_VMs: APPLY ICMP-TCP-COMBO CONTRACT and VERIFY TRAFFIC")
        prs = self.test_5_prs
        for ext_pol in [self.external_pol_1, self.external_pol_2]:
            if self.gbp_crud.update_gbp_external_policy(ext_pol, property_type='uuid', consumed_policy_rulesets=prs) == 0:
                return 0
        for ptg in [self.websrvr_ptg, self.webclnt_ptg, self.appsrvr_ptg]:
            if self.gbp_crud.update_gbp_policy_target_group(ptg, property_type='uuid', provided_policy_rulesets=prs) == 0:
                return 0
        run_traffic = traff_from_extgwrtr(self.extgwrtr, self.dest_vm_fips)
        if isinstance(run_traffic, dict):
            self._log.info(
                "\nFollowing Traffic Test from External GW Router Failed == %s" % (run_traffic))
            return 0
        else:
            return 1

    def test_6_traff_rem_prs(self):
        """
        Remove the PRS/Contract from the PTG
        Test all traffic types
        """
        self._log.info(
            "\nTestcase_DNAT_EXTGWRTR_TO_TENANT_VMs: REMOVING CONTRACT and VERIFY TRAFFIC")
        for ext_pol in [self.external_pol_1, self.external_pol_2]:
            if self.gbp_crud.update_gbp_external_policy(ext_pol, property_type='uuid') == 0:
                return 0
        for ptg in [self.websrvr_ptg, self.webclnt_ptg, self.appsrvr_ptg]:
            if self.gbp_crud.update_gbp_policy_target_group(ptg, property_type='uuid') == 0:
                return 0
        run_traffic = traff_from_extgwrtr(self.extgwrtr, self.dest_vm_fips)
        if isinstance(run_traffic, dict):
            return 1
