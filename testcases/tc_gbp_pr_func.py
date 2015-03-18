#!/usr/bin/python

import sys
import logging
import os
import datetime
from gbp_conf_libs import *
from gbp_verify_libs import *
from gbp_utils import *

def main():

    #Run the Testcases:
    test = test_gbp_pr_func()
    if test.test_gbp_pr_func_1()==0:
       test.cleanup(tc_name='TESTCASE_GBP_PR_FUNC_1') 
    if test.test_gbp_pr_func_2()==0:
       test.cleanup(tc_name='TESTCASE_GBP_PR_FUNC_2')
    if test.test_gbp_pr_func_3()==0:
       test.cleanup(tc_name='TESTCASE_GBP_PR_FUNC_3')
    if test.test_gbp_pr_func_4()==0:
       test.cleanup(tc_name='TESTCASE_GBP_PR_FUNC_4')
    if test.test_gbp_pr_func_5()==0:
       test.cleanup(tc_name='TESTCASE_GBP_PR_FUNC_5')
    test.cleanup()
    report_results('test_gbp_pr_func','test_results.txt')
    sys.exit(1)

class test_gbp_pr_func(object):

    # Initialize logging
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=logging.WARNING)
    _log = logging.getLogger( __name__ )
    cmd = 'rm /tmp/test_gbp_pr_func.log'
    getoutput(cmd)
    hdlr = logging.FileHandler('/tmp/test_gbp_pr_func.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    _log.addHandler(hdlr)
    _log.setLevel(logging.INFO)
    _log.setLevel(logging.DEBUG)

    def __init__(self):
      """
      Init def 
      """
      self.gbpcfg = Gbp_Config()
      self.gbpverify = Gbp_Verify()
      self.act_name = 'demo_pa'
      self.cls_name = 'demo_pc'
      self.rule_name = 'demo_pr'
      self._log.info('\n## Step 1: Create a PC needed for PR Testing ##')
      self.cls_uuid=self.gbpcfg.gbp_policy_cfg_all(1,'classifier',self.cls_name)
      if self.cls_uuid == 0:
         self._log.info("\nReqd Classifier Create Failed, hence GBP Policy Rule Functional Test Suite Run ABORTED\n")
         os._exit(1)
      self._log.info('\n## Step 1: Create a PA needed for PR Testing ##')
      self.act_uuid=self.gbpcfg.gbp_policy_cfg_all(1,'action',self.act_name)
      if self.act_uuid == 0:
         self._log.info("\nReqd Action Create Failed, hence GBP Policy Rule Functional Test Suite Run ABORTED\n")
         os._exit(1)

    def cleanup(self,tc_name=''):
        if tc_name !='':
           self._log.info('Testcase %s: FAILED' %(tc_name))
        for obj in ['rule','classifier','action']:
            self.gbpcfg.gbp_del_all_anyobj(obj)

    def test_gbp_pr_func_1(self,name_uuid='',rule_uuid='',rep_cr=0,rep_del=0):
        """
        Create Policy Rule Object,default params(Classifier is a reqd param)
        Verify the attributes & value, show & list cmds
        Delete Policy Rule using Name
        Verify that PR has got deleted, show & list cmds
        """
        if rep_cr==0 and rep_del==0:
           self._log.info("\n###############################################################\n"
                       "TESTCASE_GBP_PR_FUNC_1: TO CREATE/VERIFY/DELETE/VERIFY a POLICY RULE with DEFAULT ATTRIB VALUE\n"
                       "###############################################################\n")

        if name_uuid=='':
           name_uuid=self.rule_name
        ###### Testcase work-flow starts 
        if rep_cr == 0 or rep_cr == 1:
	 self._log.info('\n## Step 1: Create Rule with default attrib vals##\n')
         rule_uuid = self.gbpcfg.gbp_policy_cfg_all(1,'rule',name_uuid,classifier=self.cls_name)
         if rule_uuid == 0:
	    self._log.info("# Step 1: Create Rule == Failed")
            return 0
         self._log.info('# Step 2A: Verify Rule using -list cmd')
         if self.gbpverify.gbp_policy_verify_all(0,'rule',name_uuid,rule_uuid,'True') == 0: 
            self._log.info("# Step 2A: Verify Rule using -list option == Failed")
            return 0
         self._log.info('# Step 2B: Verify Rule using -show cmd')
         if self.gbpverify.gbp_policy_verify_all(1,'rule',name_uuid,id=rule_uuid,policy_classifier_id=self.cls_uuid,enabled='True') == 0:
            self._log.info("# Step 2B: Verify Rule using -show option == Failed")
            return 0
        ####### 
        if rep_del == 0 or rep_del == 1: 
         self._log.info('\n## Step 3: Delete Rule using name  ##\n')
         if self.gbpcfg.gbp_policy_cfg_all(0,'rule',name_uuid) == 0:
            self._log.info("# Step 3: Delete Rule == Failed")
            return 0
         if self.gbpverify.gbp_policy_verify_all(0,'rule',name_uuid,rule_uuid) != 0:
            self._log.info("# Step 3A: Verify Rule is Deleted using -list option == Failed")
            return 0
         if self.gbpverify.gbp_policy_verify_all(1,'rule',name_uuid,id=rule_uuid,shared='False') != 0:
            self._log.info("# Step 3B: Verify Rule is Deleted using -show option == Failed")
            return 0
        if rep_cr==0 and rep_del==0:
           self._log.info("\n## TESTCASE_GBP_PR_FUNC_1: PASSED")
        return 1 

    def test_gbp_pr_func_2(self):
        """
        Create Policy Rule Object with GBP PA & PC
        Verify the attributes & value, show & list cmds
        Delete Policy Rule using Name
        Verify that PR has got deleted, show & list cmds
        """
        self._log.info("\n###############################################################\n"
                       "TESTCASE_GBP_PR_FUNC_2: TO CREATE/VERIFY/DELETE/VERIFY a POLICY RULE with POLICY ACTION & CLASSIFIER\n"
                       "###############################################################\n")

        ###### Testcase work-flow starts
        self._log.info("\n## Step 1: Create Policy Rule with PC & PA ##")
        rule_uuid = self.gbpcfg.gbp_policy_cfg_all(1,'rule',self.rule_name,classifier=self.cls_name,action=self.act_name)
        if rule_uuid == 0:
           self._log.info("# Step 1: Create Rule == Failed")
           return 0
        self._log.info('# Step 2A: Verify Rule using -list cmd')
        if self.gbpverify.gbp_policy_verify_all(0,'rule',self.rule_name,rule_uuid,'True') == 0:
           self._log.info("# Step 2A: Verify Rule using -list option == Failed")
           return 0
        self._log.info('# Step 2B: Verify Rule using -show cmd')
        if self.gbpverify.gbp_policy_verify_all(1,'rule',self.rule_name,id=rule_uuid,\
                                                policy_classifier_id=self.cls_uuid,enabled='True',\
                                                policy_actions=self.act_uuid) == 0:
           self._log.info("# Step 2B: Verify Rule using -show option == Failed")
           return 0
        self.test_gbp_pr_func_1(rule_uuid=rule_uuid,rep_cr=2)
        self._log.info("\n## TESTCASE_GBP_PR_FUNC_2: PASSED")
        return 1
   
    def test_gbp_pr_func_3(self):
        """
        Create Policy Rule using Default param values
        Update Each the Polciy Rule's editable params one at a time
        Verify the Policy Rule's attributes & values, show & list cmds
        Delete the Policy Rule
        Verify Policy Rule successfully deleted
        """
        self._log.info("\n###############################################################\n"
                         "TESTCASE_GBP_PR_FUNC_3: TO UPDATE/VERIFY/DELETE/VERIFY EACH ATTRIB of a POLICY RULE\n"
                         "###############################################################\n")
        ###### Testcase work-flow starts
        self._log.info('\n## Step 1: Create Policy Rule with PA and PC##\n')
        rule_uuid = self.gbpcfg.gbp_policy_cfg_all(1,'rule',self.rule_name,classifier=self.cls_name,action=self.act_name)
        if rule_uuid != 0:
            self._log.info("Step 1: Create Rule Passed, UUID == %s\n" %(rule_uuid))
        else:
            self._log.info("# Step 1: Create Rule == Failed")
            return 0
        self._log.info('\n## Step 1A: Create new PA and new PC##\n')
        new_cls_uuid=self.gbpcfg.gbp_policy_cfg_all(1,'classifier','noiro_pc1')
        if new_cls_uuid == 0:
          self._log.info("\nNew Classifier Create Failed, hence TESTCASE_GBP_PR_FUNC_3 ABORTED\n")
          return 0
        new_act_uuid=self.gbpcfg.gbp_policy_cfg_all(1,'action','noiro_pa1')
        if new_act_uuid == 0:
          self._log.info("\nNew Action Create Failed, hence TESTCASE_GBP_PR_FUNC_3 ABORTED\n")
          return 0

        attrib_list = [{'name':'noiro_pr'},{'classifier':'noiro_pc1'},{'action':'noiro_pa1'},{'description':"'For devstack demo'"}]
        for attr_val in attrib_list:
          if self.gbpcfg.gbp_policy_cfg_upd_all('rule',rule_uuid,attr_val) ==0:
             self._log.info("\nStep 2: Updating Policy Rule's Attribute %s, Failed" %(attr_val))
             return 0
        ## Verify starts
        if self.gbpverify.gbp_policy_verify_all(0,'rule','noiro_pr',rule_uuid,'True')==0:
             self._log.info("# Step 2A: Verify Policy Rule Updated Attributes using -list option == Failed")
             return 0
        if self.gbpverify.gbp_policy_verify_all(1,'rule',rule_uuid,name='noiro_pr',policy_classifier_id=new_cls_uuid,\
                                             policy_actions=new_act_uuid,description='For devstack demo')==0:
             self._log.info("# Step 2B: Verify Policy Rule Updated Attributes using -show option == Failed")
             return 0
        self._log.info("\n## TESTCASE_GBP_PR_FUNC_3: PASSED")
        return 1
  
    def test_gbp_pr_func_4(self):
        """
        Create Policy Rule using Default param values
        Update All the Policy Rule's editable params at one shot
        Verify the Policy Rule's attributes & values, show & list cmds
        Delete the Policy Rule
        Verify Policy Rule successfully deleted
        """
        self._log.info("\n###############################################################\n"
                          "TESTCASE_GBP_PR_FUNC_4: TO UPDATE/VERIFY/DELETE/VERIFY ALL ATTRIB of a POLICY RULE @ ONCE \n"
                          "###############################################################\n")
        ###### Testcase work-flow starts
        self._log.info('\n## Step 1: Create Policy Rule with PA and PC##\n')
        rule_uuid = self.gbpcfg.gbp_policy_cfg_all(1,'rule',self.rule_name,classifier=self.cls_name,action=self.act_name)
        if rule_uuid != 0:
            self._log.info("Step 1: Create Rule Passed, UUID == %s\n" %(rule_uuid))
        else:
            self._log.info("# Step 1: Create Rule == Failed")
            return 0
        self._log.info('\n## Step 1A: Create new PA and new PC##\n')
        new_cls_uuid=self.gbpcfg.gbp_policy_cfg_all(1,'classifier','noiro_pc2')
        if new_cls_uuid == 0:
          self._log.info("\nNew Classifier Create Failed, hence TESTCASE_GBP_PR_FUNC_3 ABORTED\n")
          os._exit(1)
        new_act_uuid=self.gbpcfg.gbp_policy_cfg_all(1,'action','noiro_pa2')
        if new_act_uuid == 0:
          self._log.info("\nNew Action Create Failed, hence TESTCASE_GBP_PR_FUNC_3 ABORTED\n")
          os._exit(1)
        self._log.info('\n###########################################\n'
                       '## Step 2: Update Policy Rule Attributes ##\n'
                       '## protocol, port-range,name,direction,description ##\n'
                       '#################################################\n')
        if self.gbpcfg.gbp_policy_cfg_all(2,'rule',rule_uuid,name='noiro_pr',classifier=new_cls_uuid,\
                                          action=new_act_uuid,description="'For devstack demo'"):
           self._log.info("\nStep 2: Updating Policy Rule's Attributes name,protocol,port-range,name,direction,description, Passed")
        else:
           self._log.info("\nStep 2: Updating Policy Rule's Attributes name,protocol,port-range,name,direction,description, Failed")    
           return 0
        ## Verify starts
        if self.gbpverify.gbp_policy_verify_all(0,'rule','noiro_pr',rule_uuid,'True')==0:
             self._log.info("# Step 2A: Verify Policy Rule Updated Attributes using -list option == Failed")
             return 0
        if self.gbpverify.gbp_policy_verify_all(1,'rule',rule_uuid,name='noiro_pr',policy_classifier_id=new_cls_uuid,\
                                             policy_actions=new_act_uuid,description='For devstack demo')==0:
             self._log.info("# Step 2B: Verify Policy Rule Updated Attributes using -show option == Failed")
             return 0
        self._log.info("\n## TESTCASE_GBP_PR_FUNC_4: PASSED")
        return 1

    
    def test_gbp_pr_func_5(self):
        """
        Create and Verify Policy Rule with valued attributes(action & classifer)
        Create multiple(n=10) Policy Rule-Set referencing the same Policy Rule
        Verify the Policy Rule is referenced in all configured Policy Rules
        Delete the Policy Rule, verify it's deletion fails until all Policy Rule-Sets are deleted
        Verify Policy Rule successfully deleted
        """
        self._log.info("\n###############################################################\n"
                          "TESTCASE_GBP_PR_FUNC_5: CREATE/SHARE/DELETE/ POLICY RULE among MULTIPLE POLICY RULE-SETs \n"
                          "###############################################################\n")
        ###### Testcase work-flow starts
        self._log.info('\n## Step 1: Create new PA ,new PC, 1 PR using the same PA & PC##\n')
        new_cls_uuid=self.gbpcfg.gbp_policy_cfg_all(1,'classifier','noiro_pc1')
        if new_cls_uuid == 0:
          self._log.info("\nNew Classifier Create Failed, hence TESTCASE_GBP_PS_FUNC_4 ABORTED\n")
          return 0
        new_act_uuid=self.gbpcfg.gbp_policy_cfg_all(1,'action','noiro_pa1')
        if new_act_uuid == 0:
          self._log.info("\nNew Action Create Failed, hence TESTCASE_GBP_PR_FUNC_4 ABORTED\n")
          return 0
        rule_uuid=self.gbpcfg.gbp_policy_cfg_all(1,'rule','noiro_pr',classifier=new_cls_uuid,\
                                          action=new_act_uuid,description="'For devstack demo'")
        if rule_uuid == 0:
               self._log.info("##\n Step 1B: Policy Rule create, failed\n")
               return 0
        self._log.info("\n## Step 2: Create Multiple PRS referencing the same PR")
        for n in range(1,11):
          if self.gbpcfg.gbp_policy_cfg_all(1,'ruleset','noiro_prs_%s' %(n),\
                                         policy_rule=rule_uuid,description="'For devstack demo'") == 0:
             self._log.info("##\n Step 2A: Policy Rule-Set creation referencing same Policy Rule, Failed")
             return 0
          if self.gbpverify.gbp_policy_verify_all(1,'ruleset','noiro_prs_%s' %(n),policy_rules=rule_uuid) == 0:
             self._log.info("##\n Step 2B: Verify Policy Rule-Set noiro_prs_%s referencing same Policy Rule, Failed" %(n))
             return 0
        self._log.info("\n## Step 3: Delete Policy Rule and Policy Rule-Set and verify deletion fails ##")
        for i in range(1,11):
          if self.gbpcfg.gbp_policy_cfg_all(0,'rule',rule_uuid) != 0:
             self._log.info("\n## Step 3A: Referenced Policy Rule's deletion DID NOT fail ##")
             return 0
          if self.gbpcfg.gbp_policy_cfg_all(0,'ruleset','noiro_prs_%s' %(i)) == 0:
             self._log.info("\n## Step 3B: Referencing Policy Rule-Set's deletion, Failed ##")
             return 0
        self._log.info("\n## Step 4: Deletion of Policy Rule, all referencing Policy Rule-Sets has been deleted ##")
        if self.gbpcfg.gbp_policy_cfg_all(0,'rule',rule_uuid) == 0:
           self._log.info("\n## Step 4A: Policy Rule's deletion, Failed ##")
           return 0
        if self.gbpverify.gbp_action_verify(1,'noiro_pr',id=rule_uuid) !=0:
            self._log.info("\n## Step 4B: Verify Policy Rule is Deleted, Failed")
            return 0
        self._log.info("\n## TESTCASE_GBP_PR_FUNC_5: PASSED")

if __name__ == '__main__':
    main()
