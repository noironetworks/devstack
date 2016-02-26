#!/usr/bin/python

import sys
import logging
import os
import datetime
import string
import pprint
from libs.gbp_conf_libs import Gbp_Config
from libs.gbp_verify_libs import Gbp_Verify
from libs.gbp_fab_traff_libs import Gbp_def_traff
from libs.gbp_pexp_traff_libs import Gbp_pexp_traff
from libs.raise_exceptions import *
from testsuites_setup_cleanup import super_hdr
from libs.gbp_utils import *


class test_diff_ptg_diff_l2p_same_l3p(object):
    """
    This is a TestCase Class comprising
    all Datapath testcases for the Test Header:   
    diff_ptg_diff_l2p_same_l3p
    Every new testcases should be added as a new method in this class
    and call the testcase method inside the 'test_runner' method
    """
    # Initialize logging
    #logging.basicConfig(level=logging.INFO)
    _log = logging.getLogger(__name__)
    _log.setLevel(logging.INFO)
    # create a logfile handler
    hdlr = logging.FileHandler('/tmp/testsuite_diff_ptg_diff_l2p_same_l3p.log')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    hdlr.setFormatter(formatter)
    # Add the handler to the logger
    _log.addHandler(hdlr)

    def __init__(self, objs_uuid):

        self.gbpcfg = Gbp_Config()
        self.gbpverify = Gbp_Verify()
        self.gbpdeftraff = Gbp_def_traff()
        stack_name = super_hdr.stack_name
        heat_temp = super_hdr.heat_temp
        self.ntk_node = super_hdr.ntk_node
        self.ptg_1 = objs_uuid['demo_diff_ptg_l2p_same_l3p_ptg1_id']
        self.ptg_2 = objs_uuid['demo_diff_ptg_l2p_same_l3p_ptg2_id']
        self.test_2_prs = objs_uuid['demo_ruleset_norule_id']
        self.test_3_prs = objs_uuid['demo_ruleset_icmp_id']
        self.test_4_prs = objs_uuid['demo_ruleset_tcp_id']
        self.test_5_prs = objs_uuid['demo_ruleset_icmp_tcp_id']
        self.test_6_prs = objs_uuid['demo_ruleset_icmp_udp_id']
        self.test_7_prs = objs_uuid['demo_ruleset_all_id']
        self.udp_rule = 'demo_rule_udp'  # JISHNU: name appears as in heat template
        self.icmp_rule = 'demo_rule_icmp'
        self.tcp_rule = 'demo_rule_tcp'
        self.vm7_ip = self.gbpcfg.get_vm_subnet('VM7')[0]
        self.vm7_subn = self.gbpcfg.get_vm_subnet('VM7')[1]
        self.dhcp_ns = self.gbpcfg.get_netns(self.ntk_node, self.vm7_subn)

   
    def test_runner(self, log_string, location):
        """
        Method to run all testcases
        """
        self.vm_loc = location
        test_list = [self.test_1_traff_with_no_prs,
                     self.test_2_traff_app_prs_no_rule,
                     self.test_3_traff_apply_prs_icmp,
                     self.test_4_traff_apply_prs_tcp,
                     self.test_5_traff_apply_prs_icmp_tcp,
                     self.test_6_traff_apply_prs_icmp_udp,
                     self.test_7_traff_apply_prs_all_proto,
                     self.test_8_traff_rem_add_udp_rule,
                     self.test_9_traff_rem_add_tcp_rule,
                     self.test_9A_traff_rem_add_icmp_udp_rule,
                     self.test_11_traff_rem_prs
                     ]
        test_results = {}
        for test in test_list:
                repeat_test = 1
                while repeat_test < 4:
                  if test() == 1:
                     break
                  self._log.warn("Repeat Run of the Testcase = %s" %(test.__name__.lstrip('self.')))
                  repeat_test += 1
                if repeat_test == 4: #NOTE: JISHNU changed it below for BugRepro
                    for test in ['test_8','test_9','test_9A']:
                        if test in test.__name__:
                           self.test_revert_policy_ruleset(test.upper())
                    test_results[string.upper(
                        test.__name__.lstrip('self.'))] = 'FAIL'
                    self._log.info("\n%s_%s_%s == FAIL" % (self.__class__.__name__.upper(
                        ), log_string.upper(), string.upper(test.__name__.lstrip('self.'))))
                else:
                    if 'test_1' in test.__name__ or 'test_2' in test.__name__:
                        test_results[string.upper(
                            test.__name__.lstrip('self.'))] = 'PASS'
                        self._log.info("\n%s_%s_%s 10 subtestcases == PASS" % (self.__class__.__name__.upper(
                        ), log_string.upper(), string.upper(test.__name__.lstrip('self.'))))
                    else:
                        test_results[string.upper(
                            test.__name__.lstrip('self.'))] = 'PASS'
                        self._log.info("\n%s_%s_%s == PASS" % (self.__class__.__name__.upper(
                        ), log_string.upper(), string.upper(test.__name__.lstrip('self.'))))
        pprint.pprint(test_results)
 
    def verify_traff(self, proto=['all']):
        """
        Verifies the expected traffic result per testcase
        """
        # Incase of Diff PTG Same L2 & L3P all traffic is dis-allowed by default unless Policy-Ruleset is applied
        # Hence verify_traff will check for all protocols including the
        # implicit ones
        gbpcfg = Gbp_Config()
        if self.vm_loc == 'diff_host_same_leaf' or self.vm_loc == 'diff_host_diff_leaf':
            dest_ip = gbpcfg.get_vm_subnet('VM9', ret='ip')
            self._log.debug('VM7-IP: %s, VM7-subnet: %s, Dest-IP: %s, NetNS: %s' %(self.vm7_ip, self.vm7_subn, dest_ip, self.dhcp_ns))
            gbppexptraff = Gbp_pexp_traff(
                self.ntk_node, self.dhcp_ns, self.vm7_ip, dest_ip)
        if self.vm_loc == 'same_host':
            dest_ip = gbpcfg.get_vm_subnet('VM8', ret='ip')
            self._log.debug('VM7-IP: %s, VM7-subnet: %s, Dest-IP: %s, NetNS: %s' %(self.vm7_ip, self.vm7_subn, dest_ip, self.dhcp_ns))
            gbppexptraff = Gbp_pexp_traff(
                self.ntk_node, self.dhcp_ns, self.vm7_ip, dest_ip)
        results = gbppexptraff.test_run()
        self._log.info('Results from the Testcase == %s' %(results))
        if results == {}:
            return 0
        failed = {}
        # In 'all' proto is verified for PTGs with NO_PRS, PRS_NO_RULE,
        # REM_PRS, hence below val ==1, then Fail, because pkts were
        # expected to be dropped but they were NOT(hence the Test should
        # be marked FAIL.
        if proto[0] == 'all':
            failed = {key: val for key, val in results[
                dest_ip].iteritems() if val == 1}
            if len(failed) > 0:
                self._log.error('For All Protcol Following traffic_types %s = Failed' %(failed))
                return 0
            else:
                return 1
        else:
            implicit_allow = ['arp', 'dhcp', 'dns']
            allow_list = implicit_allow + proto
            failed = {key: val for key, val in results[
                dest_ip].iteritems() if val == 0 and key in allow_list}
            failed.update({key: val for key, val in results[
                          dest_ip].iteritems() if val == 1 and key not in allow_list})
            if len(failed) > 0:
                self._log.error('Following traffic_types %s = Failed' %(failed))
                return 0
            else:
                return 1


    def test_1_traff_with_no_prs(self):
        """
        Run traff test when PTG is with NO Contract
        """
        self._log.info(
            "\nTest_1_Traff_With_No_PRS 10 Traffic Sub-Testcases with NO CONTRACT for arp,dns,dhcp,udp,icmp and their combos")
        return self.verify_traff()

    def test_2_traff_app_prs_no_rule(self):
        """
        Update the in-use PTG with a PRS which has NO-Rule
        Send traff
        """
        self._log.info(
            "\nTest_2_Traff_Apply_PRS_No_Rule: 10 Traffic Sub-Testcases with CONTRACT But NO RULE for arp,dns,dhcp,tcp,udp,icmp and their combos")
        prs = self.test_2_prs
        if self.gbpcfg.gbp_policy_cfg_all(2, 'group', self.ptg_1, provided_policy_rule_sets="%s=scope" % (prs))\
           and self.gbpcfg.gbp_policy_cfg_all(2, 'group', self.ptg_2, consumed_policy_rule_sets="%s=scope" % (prs)) != 0:
            return self.verify_traff()
        else:
            self._log.error('Updating PTG: Failed')
            return 0

    def test_3_traff_apply_prs_icmp(self):
        """
        Apply Policy-RuleSet to the in-use PTG
        Send traffic
        """
        self._log.info(
            "\nTest_3_Traff_Apply_PRS_ICMP: Apply ICMP CONTRACT and Verify Traffic")
        prs = self.test_3_prs
        if self.gbpcfg.gbp_policy_cfg_all(2, 'group', self.ptg_1, provided_policy_rule_sets="%s=scope" % (prs))\
           and self.gbpcfg.gbp_policy_cfg_all(2, 'group', self.ptg_2, consumed_policy_rule_sets="%s=scope" % (prs)) != 0:
            return self.verify_traff(proto=['icmp'])
        else:
            self._log.error('Updating PTG: Failed')
            return 0

    def test_4_traff_apply_prs_tcp(self):
        """
        Apply Policy-RuleSet to the in-use PTG
        Send traffic
        """
        self._log.info(
            "\nTest_4_Traff_Apply_PRS_TCP: Apply TCP CONTRACT and Verify Traffic")
        prs = self.test_4_prs
        if self.gbpcfg.gbp_policy_cfg_all(2, 'group', self.ptg_1, provided_policy_rule_sets="%s=scope" % (prs))\
           and self.gbpcfg.gbp_policy_cfg_all(2, 'group', self.ptg_2, consumed_policy_rule_sets="%s=scope" % (prs)) != 0:
            return self.verify_traff(proto=['tcp'])
        else:
            self._log.error('Updating PTG: Failed')
            return 0

    def test_5_traff_apply_prs_icmp_tcp(self):
        """
        Apply Policy-RuleSet to the in-use PTG
        Send traffic
        """
        self._log.info(
            "\nTest_5_Traff_Apply_PRS_ICMP_TCP: Apply ICMP-TCP combo CONTRACT and Verify Traffic")
        prs = self.test_5_prs
        if self.gbpcfg.gbp_policy_cfg_all(2, 'group', self.ptg_1, provided_policy_rule_sets="%s=scope" % (prs))\
           and self.gbpcfg.gbp_policy_cfg_all(2, 'group', self.ptg_2, consumed_policy_rule_sets="%s=scope" % (prs)) != 0:
            return self.verify_traff(proto=['icmp', 'tcp'])
        else:
            self._log.error('Updating PTG: Failed')
            return 0

    def test_6_traff_apply_prs_icmp_udp(self):
        """
        Apply Policy-RuleSet to the in-use PTG
        Send traffic
        """
        self._log.info(
            "\nTest_6_Traff_Apply_PRS_ICMP_UDP: Apply ICMP-UDP combo CONTRACT and Verify Traffic")
        prs = self.test_6_prs
        if self.gbpcfg.gbp_policy_cfg_all(2, 'group', self.ptg_1, provided_policy_rule_sets="%s=scope" % (prs))\
           and self.gbpcfg.gbp_policy_cfg_all(2, 'group', self.ptg_2, consumed_policy_rule_sets="%s=scope" % (prs)) != 0:
            return self.verify_traff(proto=['icmp', 'udp'])
        else:
            self._log.error('Updating PTG: Failed')
            return 0

    def test_7_traff_apply_prs_all_proto(self):
        """
        Apply Policy-RuleSet to the in-use PTG
        Send traffic
        """
        self._log.info(
            "\nTest_7_Traff_Apply_PRS_All_Proto: Apply ICMP-TCP-UDP combo CONTRACT and Verify Traffic")
        prs = self.test_7_prs
        if self.gbpcfg.gbp_policy_cfg_all(2, 'group', self.ptg_1, provided_policy_rule_sets="%s=scope" % (prs))\
           and self.gbpcfg.gbp_policy_cfg_all(2, 'group', self.ptg_2, consumed_policy_rule_sets="%s=scope" % (prs)) != 0:
            return self.verify_traff(proto=['icmp', 'tcp', 'udp'])
        else:
            self._log.error('Updating PTG: Failed')
            return 0

    # Testcases 8-10 will need PRS=self.test_7_prs already applied
    def test_8_traff_rem_add_udp_rule(self):
        """
        Remove UDP Policy-Rule from in-use all-proto PRS
        Send traffic
        Add back UDP Policy-Rule to the PRS
        Send traffic
        """
        prs = self.test_7_prs
        self._log.info(
            "\nTest_8_Traff_Rem_Add_UDP_Rule: Remove and Apply back UDP Rule from CONTRACT and Verify Traffic")
        if self.gbpcfg.gbp_policy_cfg_all(2, 'ruleset', prs, policy_rule='%s,%s' % (self.tcp_rule, self.icmp_rule)) != 0:
            if self.verify_traff(proto=['icmp', 'tcp'])==1:
               return self.test_revert_policy_ruleset('Test_8',traff=1)
        else:
            self._log.error("Updating PRS by removing of UDP PolicyRule from All-Proto PRS: Failed")
            return 0

    def test_9_traff_rem_add_tcp_rule(self):
        """
        Remove TCP Policy-Rule from in-use all-proto PRS
        Send traffic
        Add back TCP Policy-Rule to the PRS
        Send traffic
        """
        prs = self.test_7_prs
        self._log.info(
            "\nTest_9_Traff_Rem_Add_TCP_Rule: Remove and Apply back TCP Rule from CONTRACT and Verify Traffic")
        if self.gbpcfg.gbp_policy_cfg_all(2, 'ruleset', prs, policy_rule='%s,%s' % (self.udp_rule, self.icmp_rule)) != 0:
            if self.verify_traff(proto=['icmp', 'udp'])==1:
               return self.test_revert_policy_ruleset('Test_9',traff=1)
        else:
            self._log.error("Updating PRS by removing of TCP PolicyRule from All-Proto PRS: Failed")
            return 0

    def test_9A_traff_rem_add_icmp_udp_rule(self):
        """
        Remove both ICMP & UDP Policy-Rules from in-use all-proto PRS
        Send traffic
        Add back ICMP & UDP Policy-Rules to the PRS
        Send traffic
        """
        prs = self.test_7_prs
        self._log.info(
            "\nTest_9A_Traff_Rem_Add_ICMP_UDP_Rule: Remove and Apply back ICMP & UDP Rules from CONTRACT and Verify Traffic")
        if self.gbpcfg.gbp_policy_cfg_all(2, 'ruleset', prs, policy_rule='%s' % (self.tcp_rule)) != 0:
            if self.verify_traff(proto=['tcp'])==1:
               return self.test_revert_policy_ruleset('Test_9A',traff=1)
        else:
            self._log.error("Updating PRS by removing of ICMP & UDP PolicyRules from All-Proto PRS: Failed")
            return 0

    def test_revert_policy_ruleset(self,tc,traff=0):
        """
        Reverts the All-Protocol PRS
        Runs and verifies traffic
        tc:: TestCase Name inside which this test runs
        traff:: 0--> send no traffic, 1--> send traffic
        Send Traff when the parent test traff PASS,ensuring that adding
        all PRs to the PRS works fine before invoking the next similar testcase
        """
        prs = self.test_7_prs
        if traff == 1:
           self._log.info("Adding TCP,UDP,ICMP PRs back to All-Proto PRS and Verify Traffic After %s" %(tc))
        else:
           self._log.info("Only Adding TCP,UDP,ICMP PRs back to All-Proto PRS After Test %s" %(tc))
        if self.gbpcfg.gbp_policy_cfg_all(2, 'ruleset', prs, policy_rule='%s,%s,%s' % (self.udp_rule, self.icmp_rule, self.tcp_rule)) != 0:
           if traff == 1:
              return self.verify_traff(proto=['icmp', 'tcp', 'udp'])
        else:
            self._log.error("Updating All-Proto PRS by adding ALL PRs back: Failed")
            return 0

    def test_11_traff_rem_prs(self):
        """
        Remove the PRS/Contract from the PTG
        Test all traffic types
        """
        self._log.info(
            "\nTest_11_Traff_Rem_PRS: 10 Sub-Testcases for REMOVING CONTRACT and Verify Traffic")
        if self.gbpcfg.gbp_policy_cfg_all(2, 'group', self.ptg_1, provided_policy_rule_sets="")\
           and self.gbpcfg.gbp_policy_cfg_all(2, 'group', self.ptg_2, consumed_policy_rule_sets="") != 0:
            return self.verify_traff()
        else:
            self._log.error('Updating PTG: Failed')
            return 0
