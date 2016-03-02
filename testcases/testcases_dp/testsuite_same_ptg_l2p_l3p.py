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
from libs.gbp_utils import *
from testsuites_setup_cleanup import super_hdr


class test_same_ptg_same_l2p_same_l3p(object):
    """
    This is a TestCase Class comprising
    all Datapath testcases for the Test Header:   
    same_ptg_same_l2p_same_l3p
    Every new testcases should be added as a new method in this class
    and call the testcase method inside the 'test_runner' method
    """

    # Initialize logging
    #logging.basicConfig(level=logging.INFO)
    _log = logging.getLogger(__name__)
    _log.setLevel(logging.INFO)
    # create a logfile handler
    hdlr = logging.FileHandler('/tmp/testsuite_same_ptg_l2p_l3p.log')
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
        self.apic_ip = super_hdr.apic_ip
        self.ptg = objs_uuid['demo_same_ptg_l2p_l3p_ptg_id']
        self.test_2_prs = objs_uuid['demo_ruleset_norule_id']
        self.test_3_prs = objs_uuid['demo_ruleset_icmp_id']
        self.test_4_prs = objs_uuid['demo_ruleset_tcp_id']
        self.test_5_prs = objs_uuid['demo_ruleset_icmp_tcp_id']
        self.test_6_prs = objs_uuid['demo_ruleset_icmp_udp_id']
        self.test_7_prs = objs_uuid['demo_ruleset_all_id']
        self.vm1_ip = self.gbpcfg.get_vm_subnet('VM1')[0]
        self.vm1_subn = self.gbpcfg.get_vm_subnet('VM1')[1]
        self.dhcp_ns = self.gbpcfg.get_netns(self.ntk_node, self.vm1_subn)

    def test_runner(self, log_string, location):
        """
        Method to run all testcases for this test_suite
        """
        # Note: Cleanup per testcases is not required,since every testcase
        # updates the PTG, hence over-writing previous attr vals
        self.vm_loc = location
        test_list = [self.test_1_traff_with_no_prs,
                     self.test_2_traff_apply_prs_no_rule,
                     self.test_3_traff_apply_prs_icmp,
                     self.test_4_traff_apply_prs_tcp,
                     self.test_5_traff_apply_prs_icmp_tcp,
                     self.test_6_traff_apply_prs_icmp_udp,
                     self.test_7_traff_apply_prs_all_proto,
                     self.test_8_traff_rem_prs
                     ]
        test_results = {}
        for flag in ['enforced','unenforced']:
            self._log.info("Run the Intra-EPG TestSuite with %s" %(flag))
            ptg_name = 'demo_same_ptg_l2p_l3p_ptg' #TBD: JISHNU For now hardcoded, we will improve this
            if flag == 'enforced':
               expectedRetVal = 0
               addEnforcedToPtg(self.apic_ip,ptg_name,tenant='_noirolab_admin') #Cant use self.ptg as its a UUID instead of namestring
            else:
               addEnforcedToPtg(self.apic_ip,ptg_name,flag=flag,tenant='_noirolab_admin')
               expectedRetVal = 1
            for test in test_list:
                repeat_test = 1
                while repeat_test < 4:
                      if flag == 'enforced':
                         if test() == 0:
                            break
                      if flag == 'unenforced':
                         if test() == expectedRetVal:
                            break
                      self._log.info("Repeat Run of the Testcase = %s" %(test.__name__.lstrip('self.')))
                      repeat_test += 1
                if repeat_test == 4:
                    test_results[string.upper(
                        test.__name__.lstrip('self.'))+'_'+flag.upper()] = 'FAIL'
                    self._log.info("\n%s_%s_%s_%s == FAIL" % (self.__class__.__name__.upper(
                    ), log_string.upper(), string.upper(test.__name__.lstrip('self.')),flag.upper()))
                else:
                    if 'test_1' in test.__name__ or 'test_2' in test.__name__:
                        test_results[string.upper(
                            test.__name__.lstrip('self.'))+'_'+flag.upper()] = 'PASS'
                        self._log.info("\n%s_%s_%s_%s 10 subtestcases == PASS" % (self.__class__.__name__.upper(
                        ), log_string.upper(), string.upper(test.__name__.lstrip('self.')),flag.upper()))
                    else:
                        test_results[string.upper(
                            test.__name__.lstrip('self.'))+'_'+flag.upper()] = 'PASS'
                        self._log.info("\n%s_%s_%s_%s == PASS" % (self.__class__.__name__.upper(
                        ), log_string.upper(), string.upper(test.__name__.lstrip('self.')),flag.upper()))
        pprint.pprint(test_results)    

    def verify_traff(self):
        """
        Verifies the expected traffic result per testcase
        """
        # Incase of Same PTG all traffic is allowed irrespective what Policy-Ruleset is applied
        # Hence verify_traff will check for all protocols including the
        # implicit ones
        gbpcfg = Gbp_Config()
        if self.vm_loc == 'diff_host_same_leaf' or self.vm_loc == 'diff_host_diff_leaf':
            dest_ip = gbpcfg.get_vm_subnet('VM3', ret='ip')
            self._log.debug("VM1-IP: %s, VM1-subnet: %s, Dest-IP: %s, NetNS: %s" %(self.vm1_ip, self.vm1_subn, dest_ip, self.dhcp_ns))
            gbppexptraff = Gbp_pexp_traff(
                self.ntk_node, self.dhcp_ns, self.vm1_ip, dest_ip)
        if self.vm_loc == 'same_host':
            dest_ip = gbpcfg.get_vm_subnet('VM2', ret='ip')
            self._log.debug("VM1-IP: %s, VM1-subnet: %s, Dest-IP: %s, NetNS: %s" %(self.vm1_ip, self.vm1_subn, dest_ip, self.dhcp_ns))
            gbppexptraff = Gbp_pexp_traff(
                self.ntk_node, self.dhcp_ns, self.vm1_ip, dest_ip)
        results = gbppexptraff.test_run()
        self._log.info('Results from the Testcase == %s' %(results))
        if results == {}:
            return 0
        failed = {}
        failed = {key: val for key, val in results[
            dest_ip].iteritems() if val == 0}
        if len(failed) > 0:
            self._log.error('Following traffic_types %s = Failed' % (failed))
            return 0
        else:
            return 1

    def test_1_traff_with_no_prs(self):
        """
        Run traff test when PTG is with NO Contract
        """
        self._log.info(
            "\nTest_1_Traff_With_No_PRS: 10 Traffic Sub-Testcases with NO CONTRACT for arp,dns,dhcp,tcp,udp,icmp and their combos")
        return self.verify_traff()

    def test_2_traff_apply_prs_no_rule(self):
        """
        Update the in-use PTG with a PRS which has NO-Rule
        Send traff
        """
        self._log.info(
            "\nTest_2_Traff_Apply_PRS_No_Rule: 10 Traffic Sub-Testcases with CONTRACT But NO RULE for arp,dns,dhcp,tcp,udp,icmp and their combos")
        prs = self.test_2_prs
        if self.gbpcfg.gbp_policy_cfg_all(2, 'group', self.ptg, provided_policy_rule_sets="%s=scope" % (prs), consumed_policy_rule_sets="%s=scope" % (prs)) != 0:
            return self.verify_traff()
        else:
            self._log.error( 'Updating PTG: Failed')
            return 0

    def test_3_traff_apply_prs_icmp(self):
        """
        Apply Policy-RuleSet to the in-use PTG
        Send traffic
        """
        self._log.info(
            "\nTest_3_Traff_Apply_PRS_ICMP: Apply ICMP CONTRACT and Verify Traffic")
        prs = self.test_3_prs
        if self.gbpcfg.gbp_policy_cfg_all(2, 'group', self.ptg, provided_policy_rule_sets="%s=scope" % (prs), consumed_policy_rule_sets="%s=scope" % (prs)) != 0:
            return self.verify_traff()
        else:
            self._log.error('Updating PTG == Failed')
            return 0

    def test_4_traff_apply_prs_tcp(self):
        """
        Apply Policy-RuleSet to the in-use PTG
        Send traffic
        """
        self._log.info(
            "\nTest_4_Traff_Apply_PRS_TCP: Apply TCP CONTRACT and Verify Traffic")
        prs = self.test_4_prs
        if self.gbpcfg.gbp_policy_cfg_all(2, 'group', self.ptg, provided_policy_rule_sets="%s=scope" % (prs), consumed_policy_rule_sets="%s=scope" % (prs)) != 0:
            return self.verify_traff()
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
        if self.gbpcfg.gbp_policy_cfg_all(2, 'group', self.ptg, provided_policy_rule_sets="%s=scope" % (prs), consumed_policy_rule_sets="%s=scope" % (prs)) != 0:
            return self.verify_traff()
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
        if self.gbpcfg.gbp_policy_cfg_all(2, 'group', self.ptg, provided_policy_rule_sets="%s=scope" % (prs), consumed_policy_rule_sets="%s=scope" % (prs)) != 0:
            return self.verify_traff()
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
        if self.gbpcfg.gbp_policy_cfg_all(2, 'group', self.ptg, provided_policy_rule_sets="%s=scope" % (prs), consumed_policy_rule_sets="%s=scope" % (prs)) != 0:
            return self.verify_traff()
        else:
            self._log.error('Updating PTG: Failed')
            return 0

    def test_8_traff_rem_prs(self):
        """
        Remove the PRS/Contract from the PTG
        Test all traffic types
        """
        self._log.info(
            "\nTest_8_Traff_Rem_PRS: 10 Traffic Sub-Testcases REMOVE CONTRACT for arp,dns,dhcp,tcp,udp,icmp and their combos")
        if self.gbpcfg.gbp_policy_cfg_all(2, 'group', self.ptg, provided_policy_rule_sets="", consumed_policy_rule_sets="") != 0:
            return self.verify_traff()
        else:
            self._log.error('Updating PTG: Failed')
            return 0
