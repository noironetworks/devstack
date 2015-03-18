#!/usr/bin/python

import sys
import logging
import os
import datetime
from gbp_conf_libs import *
from gbp_verify_libs import *

def main():

    #Run the Testcases:
    test = test_gbp_ptg_func()
    if test.test_gbp_ptg_func_1()==0:
       test.cleanup(tc_name='TESTCASE_GBP_PTG_FUNC_1') 
    if test.test_gbp_ptg_func_2()==0:
       test.cleanup(tc_name='TESTCASE_GBP_PTG_FUNC_2')
    #if test.test_gbp_ptg_func_3()==0:
    #   test.cleanup(tc_name='TESTCASE_GBP_PTG_FUNC_3')
    #if test.test_gbp_ptg_func_4()==0:
    #   test.cleanup(tc_name='TESTCASE_GBP_PTG_FUNC_4')
    test.cleanup()
    report_results('test_gbp_ptg_func','test_results.txt')
    sys.exit(1)

class test_gbp_ptg_func(object):

    # Initialize logging
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=logging.WARNING)
    _log = logging.getLogger( __name__ )
    hdlr = logging.FileHandler('/tmp/test_gbp_ptg_func.log')
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
        self.act_name = 'test_ptg_pa'
        self.cls_name = 'test_ptg_pc'
        self.rule_name = 'test_ptg_pr'
        self.ruleset_name = 'test_ptg_prs'
        self.ptg_name = 'demo_ptg'
        self.l2p_name = 'test_ptg_l2p'
        self.l3p_name = 'test_ptg_l3p'
        self._log.info('\n## Step 1: Create a PC needed for PTG Testing ##')
        self.cls_uuid=self.gbpcfg.gbp_policy_cfg_all(1,'classifier',self.cls_name)
        if self.cls_uuid == 0:
           self._log.info("\nReqd Policy Classifier Create Failed, hence GBP Policy Target-Group Functional Test Suite Run ABORTED\n")
           return 0
        self._log.info('\n## Step 1: Create a PA needed for PTG Testing ##')
        self.act_uuid=self.gbpcfg.gbp_policy_cfg_all(1,'action',self.act_name)
        if self.act_uuid == 0:
           self._log.info("\n## Reqd Policy Action Create Failed, hence GBP Policy Target-Group Functional Test Suite Run ABORTED\n")
           return 0
        self._log.info('\n## Step 1: Create a PR needed for PTG Testing ##')
        self.rule_uuid = self.gbpcfg.gbp_policy_cfg_all(1,'rule',self.rule_name,classifier=self.cls_name,action=self.act_name)
        if self.rule_uuid == 0:
           self._log.info("\n## Reqd Policy Rule Create Failed, hence GBP Policy Target-Group Functional Test Suite Run ABORTED\n ")
           return 0
        self._log.info('\n## Step 1: Create a PRS needed for PTG Testing ##')
        self.prs_uuid = self.gbpcfg.gbp_policy_cfg_all(1,'ruleset',self.ruleset_name,policy_rules=self.rule_name)
        if self.prs_uuid == 0:
           self._log.info("\n## Reqd Policy Target-Group Create Failed, hence GBP Policy Target-Group Functional Test Suite Run ABORTED\n ")
           return 0
        l3p_uuid = self.gbpcfg.gbp_policy_cfg_all(1,'l3p',self.l3p_name,ip_pool='20.20.0.0/24',subnet_prefix_length='28')
        if l3p_uuid == 0:
           self._log.info("\n## Reqd L3Policy Create Failed, hence GBP Policy Target-Group Functional Test Suite Run ABORTED\n")
           return 0
        l2p_uuid= self.gbpcfg.gbp_policy_cfg_all(1,'l2p',self.l2p_name,l3_policy=l3p_uuid)
    def cleanup(self,tc_name=''):
        if tc_name !='':
           self._log.info('Testcase %s: FAILED' %(tc_name))
        for obj in ['group','l2p','l3p','ruleset','rule','classifier','action']:
            self.gbpcfg.gbp_del_all_anyobj(obj)

    def test_gbp_ptg_func_1(self,name_uuid='',ptg_uuid='',rep_cr=0,rep_del=0):
        """
        Create Policy Target-Group Object
        Verify the attributes & value, show & list cmds
        Verify the implicitly GBP(L2P,L3P) & Neutron(net,subnet,dhcp-port) Objects
        Delete Policy Target-Group using Name
        Verify the PTG has got deleted, show & list cmds
        Verify the implicit GBP & Neutron Objects are deleted
        """
        if rep_cr==0 and rep_del==0:
           self._log.info("\n###############################################################\n"
                       "TESTCASE_GBP_PTG_FUNC_1: TO CREATE/VERIFY/DELETE/VERIFY a POLICY TARGET-GROUP with DEFAULT ATTRIB VALUE\n"
                       "###############################################################\n")

        if name_uuid=='':
           name_uuid=self.ptg_name
        ###### Testcase work-flow starts 
        if rep_cr == 0 or rep_cr == 1:
	 self._log.info('\n## Step 1: Create Target-Group with default attrib vals##\n')
         uuids = self.gbpcfg.gbp_policy_cfg_all(1,'group',name_uuid)
         if uuids !=0:
              ptg_uuid = uuids[0]
              l2pid = uuids[1]
              subnetid = uuids[2]
         else:
	    self._log.info("\n## Step 1: Create Target-Group == Failed")
            return 0
         self._log.info('\n## Step 2A: Verify Target-Group using -list cmd')
         if self.gbpverify.gbp_policy_verify_all(0,'group',name_uuid,ptg_uuid) == 0: 
            self._log.info("\n## Step 2A: Verify Target-Group using -list option == Failed")
            return 0
         self._log.info('\n## Step 2B: Verify Target-Group using -show cmd')
         if self.gbpverify.gbp_policy_verify_all(1,'group',name_uuid,id=ptg_uuid,shared='False') == 0:
            self._log.info("\n## Step 2B: Verify Target-Group using -show option == Failed")
            return 0
         ## Verify the implicit objects(gbp & neutron)
         ret_uuid=self.gbpverify.gbp_l2l3ntk_pol_ver_all(1,'l2p',self.ptg_name,ret='default',\
                                                         id=l2pid,policy_target_groups=ptg_uuid)
         if ret_uuid!=0 and len(ret_uuid)==2:
            l3pid=ret_uuid[0]
            ntkid=ret_uuid[1]
         else:
            self._log.info("\n## Step 2C: Verify By-Default L2Policy == Failed")
            return 0
         rtr_uuid=self.gbpverify.gbp_l2l3ntk_pol_ver_all(1,'l3p',l3pid,ret='default',id=l3pid,\
                                                         name='default',ip_pool='10.0.0.0/8',\
                                                         l2_policies=l2pid,subnet_prefix_length='26',\
                                                         ip_version='4')
         if rtr_uuid!=0 and isinstance(rtr_uuid,str) == 0:
            self._log.info("# Step 2D: Verify By-Default L3Policy == Failed")
            return 0
         net_name='l2p_%s' %(name_uuid)
         if self.gbpverify.neut_ver_all('net',ntkid,name=net_name,admin_state_up='True',subnets=subnetid) == 0:
            self._log.info("# Step 2E: Implicit-creation of Neutron Network-Obj -show option == Failed")
            return 0
         subnet_name='ptg_%s' %(name_uuid)
         if self.gbpverify.neut_ver_all('subnet',subnetid,name=subnet_name,cidr='10.0.0.0/26',\
                                        enable_dhcp='True',network_id=ntkid) == 0:
            self._log.info("\n## Step 2F: Implicit-creation of Neutron SubNet-Obj == Failed")
            return 0
         rtr_name='l3p_default'
         if self.gbpverify.neut_ver_all('router',rtr_uuid,name=rtr_name,admin_state_up='True',status='ACTIVE') == 0:
           self._log.info("\n## Step 2G: Implicit-creation of Neutron Router-Obj == Failed")
           return 0
        ## Delete and Verify 
        if rep_del == 0 or rep_del == 1: 
         self._log.info('\n## Step 3: Delete Target-Group using name  ##\n')
         if self.gbpcfg.gbp_policy_cfg_all(0,'group',name_uuid) == 0:
            self._log.info("\n## Step 3: Delete Target-Group == Failed")
            return 0
         if self.gbpverify.gbp_policy_verify_all(0,'group',name_uuid,ptg_uuid) != 0:
            self._log.info("\n## Step 3A: Verify Target-Group is Deleted using -list option == Failed")
            return 0
         if self.gbpverify.gbp_policy_verify_all(1,'group',ptg_uuid) != 0:
            self._log.info("\n## Step 3B: Verify Target-Group is Deleted using -show option == Failed")
            return 0
         if rep_cr==0 and rep_del==0:
            self._log.info("\n## TESTCASE_GBP_PTG_FUNC_1: PASSED")
        return 1 

    def test_gbp_ptg_func_2(self):
        """
        Create Policy Target-Group Object with ConsumedPRS=A
        Verify the attributes & value, show & list cmds
        Update the PTG's atribute ProvidedPRS=A
        Create a PRS=B
        Update the PTG's attributes Consumed & Provided PRS=B
        Delete Policy Target-Group using Name
        Verify that Target-Group has got deleted, show & list cmds
        """
        self._log.info("\n###############################################################\n"
                       "TESTCASE_GBP_PTG_FUNC_2: TO CREATE/VERIFY/DELETE/VERIFY a POLICY TARGET-GROUP with POLICY RULESET\n"
                       "###############################################################\n")

        ## Testcase work-flow starts
        self._log.info("\n## Step 1: Create Policy Target-Group with PRS ##")
        uuids = self.gbpcfg.gbp_policy_cfg_all(1,'group',self.ptg_name,consumed_policy_rule_sets='%s=scope' %(self.ruleset_name))
        if uuids !=0:
            ptg_uuid = uuids[0].rstrip()
            l2pid = uuids[1].rstrip()
            subnetid = uuids[2].rstrip()
        else:
            self._log.info("\n## Step 1: Create Target-Group == Failed")
            return 0
        self._log.info('\n## Step 2A: Verify Policy Target-Group using -list cmd')
        if self.gbpverify.gbp_policy_verify_all(0,'group',self.ptg_name,ptg_uuid) == 0:
            self._log.info("\n## Step 2A: Verify Target-Group using -list option == Failed")
            return 0
        self._log.info('\n## Step 2B: Verify Policy Target-Group using -show cmd')
        if self.gbpverify.gbp_policy_verify_all(1,'group',self.ptg_name,id=ptg_uuid,shared='False',subnets=subnetid,consumed_policy_rule_sets=self.prs_uuid) == 0:
            self._log.info("\n## Step 2B: Verify Policy Target-Group using -show option == Failed")
            return 0
        ## Update the PTG's Provided PRS
        if self.gbpcfg.gbp_policy_cfg_all(2,'group',ptg_uuid,provided_policy_rule_sets='%s=scope' %(self.ruleset_name),name='ptg_new') == 0:
           self._log.info("\n## Step 3: Updating Policy Target-Group == Failed")
           return 0
        if self.gbpverify.gbp_policy_verify_all(1,'group','ptg_new',id=ptg_uuid,shared='False',subnets=subnetid,consumed_policy_rule_sets=self.prs_uuid,provided_policy_rule_sets=self.prs_uuid) == 0:
           self._log.info("\n## Step 3A: Verify after updating Policy Target-Group == Failed")
           return 0
        ## Create new PRS and update both Provided & Consumed PRS attrs
        new_prs_uuid = self.gbpcfg.gbp_policy_cfg_all(1,'ruleset','demo-new-prs',policy_rules=self.rule_name)
        if new_prs_uuid == 0:
           self._log.info("\n## Step 4: Reqd Policy Target-Group Create Failed, hence TESTCASE_GBP_PTG_FUNC_2 Run ABORTED\n ")
           return 0
        if self.gbpcfg.gbp_policy_cfg_all(2,'group',ptg_uuid,provided_policy_rule_sets='demo-new-prs=scope',consumed_policy_rule_sets='demo-new-prs=scope') == 0:
           self._log.info("\n## Step 5: Updating Policy Target-Group with new PRS == Failed")
           return 0
        if self.gbpverify.gbp_policy_verify_all(1,'group','ptg_new',id=ptg_uuid,shared='False',subnets=subnetid,consumed_policy_rule_sets=new_prs_uuid,provided_policy_rule_sets=new_prs_uuid) == 0:
           self._log.info("\n## Step 5A: Verify after updating Policy Target-Group == Failed")
           return 0
        ## Delete the PTG and verify
        self.test_gbp_ptg_func_1(ptg_uuid=ptg_uuid,rep_cr=2)
        self._log.info("\n## TESTCASE_GBP_PTG_FUNC_2: PASSED")
        return 1
   
    def test_gbp_ptg_func_3(self):
        """
        Create Policy Target-Group using ProvPRS,ConsPRS & L2P
        Update Each the Policy Target-Group's editable params 
        Verify the Policy Target-Group's attributes & values, show & list cmds
        Delete the Policy Target-Group
        Verify Policy Target-Group successfully deleted
        """
        self._log.info("\n###############################################################\n"
                         "TESTCASE_GBP_PTG_FUNC_3: TO UPDATE/VERIFY/DELETE/VERIFY EACH ATTRIB of a POLICY TARGET-GROUP\n"
                         "###############################################################\n")
        ###### Testcase work-flow starts
        self._log.info('\n## Step 1: Create Policy Target-Group with PRS,L2P ##\n')
        uuids = self.gbpcfg.gbp_policy_cfg_all(1,'group',self.ptg_name,consumed_policy_rule_sets='%s=scope' %(self.prs_name),provided_policy_rule_sets='%s=scope' %(self.prs_name),l2_policy=self.l2p_name)
        if uuids != 0:
            ptg_uuid = uuids[0]
            l2pid = uuids[1]
            subnetid = uuids[2]
        else:
            self._log.info("\n## Step 1: Create Target-Group == Failed")
            return 0
        if self.gbpverify.gbp_policy_verify_all(1,'group','ptg_new',id=ptg_uuid,shared='False',subnets=subnetid,consumed_policy_rule_sets=self.prs_uuid,provided_policy_rule_sets=self.prs_uuid) == 0:
           self._log.info("\n## Step 5A: Verify after updating Policy Target-Group == Failed")
           return 0
        return 1
    
    def test_gbp_ptg_func_4(self):
        """
        Create Multiple Policy Rules
        Create Policy Target-Group by associating all the Policy Rules
        Verify that multiple Policy Rules are assiciated to the Policy Target-Group
        Update the Policy Target-Group such that few Policy Rules are unmapped
        Verify the Policy Rule's attributes & values, show & list cmds
        Delete the Policy Rule
        Verify Policy Target-Group successfully deleted
        """
        self._log.info("\n###############################################################\n"
                          "TESTCASE_GBP_PTG_FUNC_4: TO CREATE/UPDATE/VERIFY/DELETE/ ASSOCIATING MULTIPLE PRs to 1 POLICY TARGET-GROUP \n"
                          "###############################################################\n")
        ###### Testcase work-flow starts
        self._log.info('\n## Step 1A: Create new PA ,new PC, 5 PRs using the same PA & PC##\n')
        new_cls_uuid=self.gbpcfg.gbp_policy_cfg_all(1,'classifier','noiro_pc1')
        if new_cls_uuid == 0:
          self._log.info("\nNew Classifier Create Failed, hence TESTCASE_GBP_PTG_FUNC_4 ABORTED\n")
          return 0
        new_act_uuid=self.gbpcfg.gbp_policy_cfg_all(1,'action','noiro_pa1')
        if new_act_uuid == 0:
          self._log.info("\nNew Action Create Failed, hence TESTCASE_GBP_PTG_FUNC_4 ABORTED\n")
          return 0
        rule_uuid_list=[]
        for i in range(3):
            new_rule_uuid=self.gbpcfg.gbp_policy_cfg_all(1,'rule','noiro_pr_%s' %(i),classifier=new_cls_uuid,\
                                          action=new_act_uuid,description="'For devstack demo'")
            if new_rule_uuid == 0:
               self._log.info("\nNew Rule Create Failed, hence TESTCASE_GBP_PTG_FUNC_4 ABORTED\n")
               return 0
            rule_uuid_list.append(new_rule_uuid)
        ptg_uuid=self.gbpcfg.gbp_policy_cfg_all(1,'group','noiro_ptg_many',\
                                         policy_rule='"%s %s %s"' %(rule_uuid_list[0],rule_uuid_list[1],rule_uuid_list[2]),\
                                         description="'For devstack demo'")
        if ptg_uuid == 0:
           self._log.info("\nStep 2: Updating Policy Target-Group's Attributes , Failed" )
           return 0
        ## Verify starts
        if self.gbpverify.gbp_policy_verify_all(0,'group','noiro_ptg_many',ptg_uuid)==0:
           self._log.info("# Step 2A: Verify Policy Target-Group Updated Attributes using -list option == Failed")
           return 0
        if self.gbpverify.gbp_policy_verify_all(1,'group',ptg_uuid,name='noiro_ptg_many',\
                                                description='For devstack demo')==0:
           self._log.info("# Step 2B: Verify Policy Target-Group Updated Attributes using -show option == Failed")
           return 0        
        if self.gbpverify.gbp_obj_ver_attr_all_values('group','noiro_ptg_many','policy_rules',rule_uuid_list) ==0:
           self._log.info("# Step 2C: Verify Policy Target-Group and its Multiple PRs using -show option == Failed")
           return 0
        ## Update the PRS by updating the PRs(removing few existing ones)
        if self.gbpcfg.gbp_policy_cfg_all(2,'group','noiro_ptg_many',\
                                          policy_rule='"%s %s"' %(rule_uuid_list[0],rule_uuid_list[2])) == 0:
           self._log.info("# Step 3: Updating Policy Target-Group's Attributes , Failed" )
        if self.gbpverify.gbp_obj_ver_attr_all_values('group','noiro_ptg_many','policy_rules',rule_uuid_list)!=0:
           self._log.info("# Step 3A: Verify Policy Target-Group and its Multiple PRs using -show option == Failed")
           return 0
        return 1

if __name__ == '__main__':
    main()
