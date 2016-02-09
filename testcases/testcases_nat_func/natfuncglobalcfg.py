#!/usr/bin/env python

import logging
import yaml
import sys

from libs.gbp_crud_libs import GBPCrud

class GbpNatFuncGlobalCfg(object):

    # Initialize logging
    # logging.basicConfig(level=logging.INFO)
    _log = logging.getLogger(__name__)
    _log.setLevel(logging.INFO)
    # create a logfile handler
    hdlr = logging.FileHandler('/tmp/natfuncglobalcfg.log')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    hdlr.setFormatter(formatter)
    # Add the handler to the logger
    _log.addHandler(hdlr)

    def __init__(self,cntlr_ip):
        """
        Init def
        """
        self._log.info(
            "\n## START OF GBP NAT FUNCTIONALITY TESTSUITE GLOBAL CONFIG\n")
        self.ostack_controller = 'cntlr_ip'
        self.gbpcrud = GBPCrud(self.ostack_controller)
        self.actname = 'ActAllow'
        self.clsicmpname = 'ClsIcmp'
        self.clstcpname = 'ClsTcp'
        self.pricmpname = 'PrIcmp'
        self.prtcpname = 'PrTcp'
        self.prsicmptcp = 'PrsIcmpTcp'
        self.prsicmp = 'PrsIcmp'
        self.prstcp = 'PrsTcp'

    def CfgGlobalObjs(self):
        self._log.info(
               '\n## Create a Policy Action needed for NAT Testing ##')
        self.gbpcrud.create_gbp_policy_action(self.actname,
                                             action_type='allow')
        self.act_uuid = self.gbpcrud.verify_gbp_policy_action(self.actname)
        if self.act_uuid == 0:
            self._log.error(
                "\n## Reqd Policy Action Create Failed, hence GBP "
                "NAT Functional Test Suite Run ABORTED\n")
            self._log.info("\nCleaning Up")
            self.cleanup()            
            return 0
        
        self._log.info(
               '\n## Create a ICMP Policy Classifier needed for NAT Testing ##')
        self.gbpcrud.create_gbp_policy_classifier(self.clsicmpname,
                                                  direction= 'bi',
                                                  protocol = 'icmp')
        self.cls_uuid_icmp = self.gbpcrud.verify_gbp_policy_classifier(self.clsicmpname)
        if self.cls_uuid_icmp == 0:
            self._log.error(
                "\nReqd ICMP Policy Classifier Create Failed, hence GBP "
                "NAT Functional Test Suite Run ABORTED\n")
            self._log.info("\nCleaning Up")
            self.cleanup()
            return 0
        
        self._log.info(
               '\n## Create a ICMP Policy Rule needed for NAT Testing ##')
        self.gbpcrud.create_gbp_policy_rule(self.pricmpname,
                                            self.cls_uuid_icmp,
                                            self.act_uuid,
                                            property_type = 'uuid')
        self.rule_uuid_icmp = self.gbpcrud.verify_gbp_policy_rule(self.pricmpname)
        if self.rule_uuid_icmp == 0:
            self._log.error(
                "\n## Reqd Policy Rule Create Failed, hence GBP NAT"
                " Functional Test Suite Run ABORTED\n ")
            self._log.info("\nCleaning Up")
            self.cleanup()
            return 0
        
        self._log.info(
               '\n## Create a TCP Policy Classifier needed for NAT Testing ##')
        self.gbpcrud.create_gbp_policy_classifier(self.clstcpname,
                                                  direction= 'bi',
                                                  protocol = 'tcp',
                                                  port_range = '20:2000')
        self.cls_uuid_tcp = self.gbpcrud.verify_gbp_policy_classifier(self.clstcpname)
        if self.cls_uuid_tcp == 0:
            self._log.error(
                "\nReqd TCP Policy Classifier Create Failed, hence GBP "
                "NAT Functional Test Suite Run ABORTED\n")
            self._log.info("\nCleaning Up")
            self.cleanup()
            return 0
        
        self._log.info(
               '\n## Create a TCP Policy Rule needed for NAT Testing ##')
        self.gbpcrud.create_gbp_policy_rule(self.prtcpname,
                                            self.cls_uuid_tcp,
                                            self.act_uuid,
                                            property_type = 'uuid')
        self.rule_uuid_tcp = self.gbpcrud.verify_gbp_policy_rule(self.prtcpname)
        if self.rule_uuid_tcp == 0:
            self._log.error(
                "\n## Reqd TCP Policy Rule Create Failed, hence GBP NAT"
                " Functional Test Suite Run ABORTED\n ")
            self._log.info("\nCleaning Up")
            self.cleanup()
            return 0
        
        self._log.info(
               '\n## Create a ICMP-TCP Policy Rule Set needed for NAT Testing ##')
        self.gbpcrud.create_gbp_policy_ruleset(self.prsicmptcp,
                     [self.rule_uuid_icmp, self.rule_uuid_tcp],
                                        property_type = 'uuid')
        self.prs_uuid_icmp_tcp = self.gbpcrud.verify_gbp_policy_rule_set(self.prsicmptcp)
        if self.prs_uuid == 0:
            self._log.error(
                "\n## Reqd ICMP-TCP Policy RuleSet Create Failed, hence "
                "GBP NAT Functional Test Suite "
                "Run ABORTED\n ")
            self._log.info("\nCleaning Up")
            self.cleanup()
            return 0

        self._log.info(
               '\n## Create a ICMP Policy Rule Set needed for NAT Testing ##')
        self.gbpcrud.create_gbp_policy_ruleset(self.prsicmp,
                                        [self.rule_uuid_icmp],
                                        property_type = 'uuid')
        self.prs_uuid_icmp = self.gbpcrud.verify_gbp_policy_rule_set(self.prsicmp)
        if self.prs_uuid_icmp == 0:
            self._log.error(
                "\n## Reqd ICMP Policy RuleSet Create Failed, hence "
                "GBP NAT Functional Test Suite "
                "Run ABORTED\n ")
            self._log.info("\nCleaning Up")
            self.cleanup()
            return 0

        self._log.info(
               '\n## Create a TCP Policy Rule Set needed for NAT Testing ##')
        self.gbpcrud.create_gbp_policy_ruleset(self.prstcp,
                                        [self.rule_uuid_tcp],
                                        property_type = 'uuid')
        self.prs_uuid_tcp = self.gbpcrud.verify_gbp_policy_rule_set(self.prstcp)
        if self.prs_uuid_tcp == 0:
            self._log.error(
                "\n## Reqd TCP Policy RuleSet Create Failed, hence "
                "GBP NAT Functional Test Suite "
                "Run ABORTED\n ")
            self._log.info("\nCleaning Up")
            self.cleanup()
            return 0


    def cleanup(self):
        # cleanup the resources created by a testcase(Blind Cleanup)
        prs_list = self.gbpcrud.get_gbp_policy_rule_set_list()
        if len(pr_list) > 0:
           for prs in prs_list:
               self.gbpcrud.delete_gbp_policy_rule_set(prs, property_type='uuid')
        pr_list = self.gbpcrud.get_gbp_policy_rule_list()
        if len(pr_list) > 0:
           for pr in pr_list:
               self.gbpcrud.delete_gbp_policy_rule(pr, property_type='uuid')
        cls_list = self.gbpcrud.get_gbp_policy_classifier_list()
        if len(cls_list) > 0:
           for cls in cls_list:
               self.gbpcrud.delete_gbp_policy_classifier(cls, property_type='uuid')
        act_list = self.gbpcrud.get_gbp_policy_action_list()
        if len(act_list) > 
           for act in act_list:
               self.gbpcrud.delete_gbp_policy_action(act, property_type='uuid')

    
