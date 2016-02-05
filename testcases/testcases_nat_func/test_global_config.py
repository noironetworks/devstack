#!/usr/bin/env python

import logging
import yaml
import sys

from libs.gbp_crud_libs import GBPCrud
from traff_from_extgw import *


def main():

    # Run the Testcases:
    f = open(sys.argv[1], 'rt')
    config_file = yaml.load(f)
    all_class_init_params = {
                                     'cntlr_ip' : config_file['controller_ip'],
                                    }
    test = gbp_nat_func_global_config(all_class_init_params)
    test.global_cfg()
    sys.exit(1)


class gbp_nat_func_global_config(object):

    # Initialize logging
    # logging.basicConfig(level=logging.INFO)
    _log = logging.getLogger(__name__)
    _log.setLevel(logging.INFO)
    # create a logfile handler
    hdlr = logging.FileHandler('/tmp/testsuite_nat_functionality.log')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    hdlr.setFormatter(formatter)
    # Add the handler to the logger
    _log.addHandler(hdlr)

    def __init__(self, params):
        """
        Init def
        """
        self._log.info(
            "\n## START OF GBP NAT FUNCTIONALITY TESTSUITE GLOBAL CONFIG\n")
        self.ostack_controller = params['cntlr_ip']
        #self.leaf_ip = params['leaf1_ip']
        #self.apic_ip = params['apic_ip']
        #self.ntk_node = params['ntk_node']
        self.gbp_crud = GBPCrud(self.ostack_controller)
        self.act_name = params['act_name']
        self.cls_name_icmp = params['cls_name_icmp']
        self.rule_name_icmp = params['rule_name_icmp']
        self.cls_name_tcp = params['cls_name_tcp']
        self.rule_name_tcp = params['rule_name_tcp']
        self.ruleset_name = params['ruleset_name']
        self.l3p_name = params['l3_policy_name']
        #self.pt_name = 'test_pt'
        self.def_ip_pool = params['l3_ip_pool']

    def global_cfg(self):
        self._log.info('\n## Create a Policy Action needed for NAT Testing ##')
        self.gbp_crud.create_gbp_policy_action(self.act_name, action_type='allow')
        self.act_uuid = self.gbp_crud.verify_gbp_policy_action(self.act_name)
        if self.act_uuid == 0:
            self._log.info(
                "\n## Reqd Policy Action Create Failed, hence GBP "
                "NAT Functional Test Suite Run ABORTED\n")
            return 0
        
        self._log.info('\n## Create a Policy Classifier needed for NAT Testing ##')
        self.gbp_crud.create_gbp_policy_classifier(self.cls_name_icmp, direction= 'bi', protocol = 'icmp')
        self.cls_uuid_icmp = self.gbp_crud.verify_gbp_policy_classifier(self.cls_name_icmp)
        if self.cls_uuid_icmp == 0:
            self._log.info(
                "\nReqd Policy Classifier Create Failed, hence GBP "
                "NAT Functional Test Suite Run ABORTED\n")
            return 0
        
        self._log.info('\n## Create a Policy Rule needed for NAT Testing ##')
        self.gbp_crud.create_gbp_policy_rule(self.rule_name_icmp, self.cls_uuid, self.act_uuid, 'uuid')
        self.rule_uuid_icmp = self.gbp_crud.verify_gbp_policy_rule(self.rule_name_icmp)
        if self.rule_uuid_icmp == 0:
            self._log.info(
                "\n## Reqd Policy Rule Create Failed, hence GBP NAT"
                " Functional Test Suite Run ABORTED\n ")
            return 0
        
        self._log.info('\n## Create a Policy Classifier needed for NAT Testing ##')
        self.gbp_crud.create_gbp_policy_classifier(self.cls_name_tcp, direction= 'bi', protocol = 'tcp')
        self.cls_uuid_tcp = self.gbp_crud.verify_gbp_policy_classifier(self.cls_name_tcp)
        if self.cls_uuid_tcp == 0:
            self._log.info(
                "\nReqd Policy Classifier Create Failed, hence GBP "
                "NAT Functional Test Suite Run ABORTED\n")
            return 0
        
        self._log.info('\n## Create a Policy Rule needed for NAT Testing ##')
        self.gbp_crud.create_gbp_policy_rule(self.rule_name_tcp, self.cls_uuid, self.act_uuid, 'uuid')
        self.rule_uuid_tcp = self.gbp_crud.verify_gbp_policy_rule(self.rule_name_tcp)
        if self.rule_uuid_tcp == 0:
            self._log.info(
                "\n## Reqd Policy Rule Create Failed, hence GBP NAT"
                " Functional Test Suite Run ABORTED\n ")
            return 0
        
        self._log.info('\n## Create a Policy Rule Set needed for NAT Testing ##')
        self.gbp_crud.create_gbp_policy_ruleset(self.ruleset_name, [self.rule_uuid_icmp, self.rule_uuid_tcp] ,'uuid')
        self.prs_uuid = self.gbp_crud.verify_gbp_policy_rule_set(self.ruleset_name)
        if self.prs_uuid == 0:
            self._log.info(
                "\n## Reqd Policy Target-Group Create Failed, hence "
                "GBP NAT Functional Test Suite "
                "Run ABORTED\n ")
            return 0
        
        self._log.info('\n## Create a L3 Policy needed for NAT Testing ##')
        self.l3p_uuid = self.gbp_crud.create_gbp_l3policy(self.l3p_name, self.def_ip_pool, subnet_prefix_length=24, shared=True)
        if self.l3p_uuid == 0:
            self._log.info(
                "\n## Reqd L3Policy Create Failed, hence GBP "
                "NAT Functional Test Suite Run ABORTED\n")
            return 0
        

    def cleanup(self):
        # cleanup the resources created by a testcase
        self.gbp_crud.delete_gbp_l3policy(self.l3p_uuid, 'uuid')
        self.gbp_crud.delete_gbp_policy_rule_set(self.prs_uuid, 'uuids')
        self.gbp_crud.delete_gbp_policy_rules(self.rule_uuid_icmp, 'uuid')
        self.gbp_crud.delete_gbp_policy_rules(self.rule_uuid_tcp, 'uuid')
        self.gbp_crud.delete_gbp_policy_classifier(self.cls_name_tcp, 'uuid')
        self.gbp_crud.delete_gbp_policy_classifier(self.cls_name_icmp, 'uuid')
        self.gbp_crud.delete_gbp_policy_action(self.act_uuid, 'uuid')

    
if __name__ == '__main__':
    main()

