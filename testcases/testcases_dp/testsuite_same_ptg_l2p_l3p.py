#!/usr/bin/python

import sys
import logging
import os
import datetime
from gbp_conf_libs import *
from gbp_verify_libs import *
from gbp_def_traffic import *

class TestSameptgl2pl3p(object):
    """
    This is a TestCase Class comprising
    all Datapath testcases for the Test Header:   
    same_ptg_same_l2p_same_l3p
    Every new testcases should be added as a new method in this class
    and call the testcase method inside the 'test_runner' method
    """
    # Initialize logging
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=logging.WARNING)
    _log = logging.getLogger( __name__ )
    hdlr = logging.FileHandler('/tmp/testsameptgl2l3p.log')
    _log.setLevel(logging.INFO)
    _log.setLevel(logging.DEBUG)

    def __init__(self):

      self.gbpcfg = Gbp_Config()
      self.gbpverify = Gbp_Verify()
      self.gbpdeftraff = Gbp_def_traff()
    
    def test_runner(self):
        """
        Method to run all testcases
        """
        #TODO: How to cleanup in case of failure of any of the below tests
        test_traff_with_no_prs()
        test_traff_apply_prs(ptg,prs)
        test_traff_upd_pr_new_pc(rule,classifier)
        test_traff_upd_prs_new_pr(ruleset,rule)
        test_traff_upd_ptg_new_prs(ptg,prs)

    def test_traff_with_no_prs(self):
        """
        Run traff test when PTG is with NO Contract
        """
        return self.gbpdeftraff.test_run()  ##TODO:Ensure that test_run() returns 0/1

    def test_traff_apply_prs(self,ptg,prs):
        """
        Apply Policy-RuleSet to the in-use PTG
        Send traffic
        """
        if self.gbpcfg.gbp_policy_cfg_all(2,'group',ptg,provided_policy_rule_sets=prs,consumed_policy_rule_sets=prs)!=0:
           return self.gbpdeftraff.test_run()
        else:
           return 0
    
    def test_traff_upd_pr_new_pc(self,rule,classifier):
        """
        Update the in-use PR with new PC(duplicate of the existing classifier)
        Send traff
        """
        if self.gbpcfg.gbp_policy_cfg_all(2,'rule',rule,classifier=classifier)!=0:
           self.gbpdeftraff.test_run()
        else:
           return 0
   
    def test_traff_upd_prs_new_pr(self,ruleset,rule):
        """
        Update the in-use PRS with new PR(duplicate of the existing policy-rule)
        Send traffic
        """
        if self.gbpcfg.gbp_policy_cfg_all(2,'ruleset',ruleset,policy_rule=rule)!=0:
           self.gbpdeftraff.test_run()
        else:
           return 0

    def test_traff_upd_ptg_new_prs(self,ptg,prs):
        """
        Update the PTG with new Contract(duplicate of the existing ptg)
        Send traffic
        """
        if self.gbpcfg.gbp_policy_cfg_all(2,'group',ptg,provided_policy_rule_sets=prs,consumed_policy_rule_sets=prs)!=0:
           self.gbpdeftraff.test_run() ## TODO
        else:
           return 0
    
    def test_traff_rem_prs(self,ptg):
        """
        Remove the PRS/Contract from the PTG
        Test all traffic types
        """
        if self.gbpcfg.gbp_policy_cfg_all(2,'group',ptg,provided_policy_rule_sets="",consumed_policy_rule_sets="")!=0:
           return self.gbpdeftraff.test_run()
        else:
           return 0
