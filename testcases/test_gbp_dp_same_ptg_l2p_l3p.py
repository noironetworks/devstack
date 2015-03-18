#!/usr/bin/python

import sys
import logging
import os
import datetime
from gbp_conf_libs import *
from gbp_verify_libs import *
from gbp_heat_libs import *
from gbp_nova_libs import * 
from gbp_def_traffic import *

def main():

    # Run each testcase:
    test = test_gbp_icmp_dp_1()
    test.run_test()  

class test_gbp_icmp_dp_1(object):

    # Initialize logging
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=logging.WARNING)
    _log = logging.getLogger( __name__ )
    hdlr = logging.FileHandler('/tmp/test_gbp_1.log')
    _log.setLevel(logging.INFO)
    _log.setLevel(logging.DEBUG)

    def __init__(self):
      """
      Initial Heat-based Config setup 
      """
      self.gbpcfg = Gbp_Config()
      self.gbpverify = Gbp_Verify()
      self.gbpnova = Gbp_Nova('172.28.184.65')
      self.gbpheat = Gbp_Heat('172.28.184.65')
      self.gbpdeftraff = Gbp_def_traff()
      self.heat_temp_demo = 'same_ptg_L2p_L3p.yaml' # Assumption the temp is co-located with the testcase
      self.heat_temp_com = 'common.yaml' # Assumption as above
      self.nova_agg1 = 'gbp_agg1'
      self.nova_az1 = 'gbp_zone1'
      self.comp_node = 'f5-compute-1.cisco.com'
    
    def test_heat_create(self):
      ## Heat Stack Create
      if self.gbpheat.cfg_all_cli(1,'common-stack',heat_temp=self.heat_temp_com) == 0:
         self._log.info("\n ABORTING THE TESTSUITE RUN, HEAT STACK CREATE of 'common-stack' Failed")
         self.gbpheat.cfg_all_cli(0,'common-stack') ## Stack delete will cause cleanup
      
      if self.gbpheat.cfg_all_cli(1,'demo-stack',heat_temp=self.heat_temp_demo) == 0:
         self._log.info("\n ABORTING THE TESTSUITE RUN, HEAT STACK CREATE of 'demo-stack' Failed")
         self.gbpheat.cfg_all_cli(0,'demo-stack')

    def test_create_vm(self,ptgs):
      """
      Creates Avail-zone
      Creates VM
      """
      ## Create Avail-zone
      agg_id = self.gbpnova.avail_zone('api','create',self.nova_agg1,avail_zone_name=self.nova_az1)
      print 'Agg %s' %(agg_id)
      if self.gbpnova.avail_zone('api','addhost',agg_id,hostname=self.comp_node) == 0:
         self._log.info("\n ABORTING THE TESTSUITE RUN, AVAIL-ZONE CREATION Failed")
         self.cleanup()
         return 0

      ## ptg_id should be a dict with keys as 'data' & 'mgmt'
      vm1 = {'name':'VM1','ssh_key':'vm1_key','az':self.nova_az1}
      vm2 = {'name':'VM2','ssh_key':'vm2_key','az':''}
      
      for vm in [vm1,vm2]:
        for key,val in ptgs.iteritems():
            port=self.gbpcfg.gbp_policy_cfg_all(1,'target','vm1_%s' %(key),policy_target_group='%s' %(val))
            if port != 0:
               vm[key] = port[1]
            print vm
        if self.gbpnova.vm_create_cli(vm['name'],vm['ssh_key'],[vm['mgmt'],vm['data']],avail_zone=vm['az']) == 0: ## VM create
           self._log.info("\n ABORTING THE TESTSUITE RUN, VM CREATION Failed")
           self.cleanup()
           return 0

    def cleanup(self):
        ##Need to call for instance delete if there is an instance
        self.gbpcfg.gbp_heat_cfg_all(0,heat_template,self.heatstack_name) ## Calling stack delete
    
    def test_traff_with_no_contract(self):
        """
        Run traff test when PTG is with NO Contract
        """
        return self.gbpdeftraff.test_run()  ##TODO:Ensure that test_run() returns 0/1

    def test_traff_apply_contract(self,ptg,prs)
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
        Update the in-use PR with new PC
        Send traff
        """
        if self.gbpcfg.gbp_policy_cfg_all(2,'rule',rule,classifier=classifier)!=0:
           self.gbpdeftraff.test_run()
        else:
           return 0
   
    def test_traff_upd_contract_new_pr(self,ruleset,rule):
        """
        Update the in-use PRS with new PR
        Send traffic
        """
        if self.gbpcfg.gbp_policy_cfg_all(2,'ruleset',ruleset,policy_rule=rule)!=0:
           self.gbpdeftraff.test_run()
        else:
           return 0

    def test_traff_upd_ptg_new_contract(self,ptg,prs):
        """
        Update the PTG with new Contract
        Send traffic
        """
        if self.gbpcfg.gbp_policy_cfg_all(2,'group',ptg,provided_policy_rule_sets=prs,consumed_policy_rule_sets=prs)!=0:
           self.gbpdeftraff.test_run() ## TODO
        else:
           return 0
         
    def run_test(self):
        """
        Setup VMs and Run test
        """
        ## Setup the VMs
        ptgs = {}
        self.test_heat_create()
        ptgs['mgmt']=self.gbpheat.get_output_cli('common-stack',self.heat_temp_com)['mgmt_ptg_id']
        ptgs['data']=self.gbpheat.get_output_cli('demo-stack',self.heat_temp_demo)['demo_ptg_id']
        print ptgs
        self.test_create_vm(ptgs)
        ## Start Test now
        
  
if __name__ == '__main__':
    main()
