#!/usr/bin/python

import sys
import logging
import os
import datetime
from gbp_conf_libs import *
from gbp_verify_libs import *

def main():

    #Run the Testcase:
    test = test_gbp_icmp_dp_1()
    test.run()

class test_gbp_icmp_dp_1(object):

    # Initialize logging
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=logging.WARNING)
    _log = logging.getLogger( __name__ )
    hdlr = logging.FileHandler('/tmp/test_gbp_1.log')
    _log.setLevel(logging.INFO)
    _log.setLevel(logging.DEBUG)

    def __init__(self):
      """
      Init def 
      """
      self.gbpcfg = Gbp_Config()
      self.gbpverify = Gbp_Verify()
      self.act_name = 'allow_all'
      self.class_name = 'pc_icmp'
      self.rule_name = 'pr_icmp'
      self.ruleset_name = 'prs_icmp'
      self.ptg_name = 'pg_icmp'	
      self.tg_name= 'tg_icmp'

    def cleanup(self,cfgobj,uuid_name,fail=0):
        if fail == 1:
           self._log.info('Testcase test_gbp_1 FAILED, hence called Cleanup')
        if isinstance(cfgobj,str):
           cfgobj=[cfgobj]
        if isinstance(uuid_name,str):
           uuid_name=[uuid_name]
        for obj,_id in zip(cfgobj,uuid_name):
          if self.gbpcfg.gbp_policy_cfg_all(0,obj,_id):
             self._log.info('Success in Clean-up/Delete of Policy Object %s\n' %(obj))
          else:
             self._log.info('Failed to Clean-up/Delete of Policy Object %s\n' %(obj))
	os._exit(1)

    def run(self):
        ###### Testcase work-flow starts 
        ####### ============ ALL POLICY OBJECTS ARE TO BE CREATED AND VERIFIED ============ #######
	self._log.info('\n#########################################\n'
                       '#######   Step 1: Create Action    ######\n'
                       '#########################################\n')
        act_uuid = self.gbpcfg.gbp_action_config(1,self.act_name)
        if act_uuid != 0:
	    self._log.info('Step 1: Create Action Passed, UUID == %s\n' %(act_uuid))
	else:
	    self._log.info("# Step 1: Create Action == Failed")
            self.cleanup('action',act_uuid)
        self._log.info('\n##########################################\n'
                       '# Step 2A: Verify Action using -list cmd #\n'
                       '#########################################\n')
        if self.gbpverify.gbp_action_verify(0,self.act_name,act_uuid):
           self._log.info('Action Verify using -list cmd == Passed')
        else:
            self._log.info("# Step 2A: Verify Action using -list option == Failed")
            self.cleanup('action',act_uuid)
        self._log.info('\n##########################################\n'
                       '# Step 2B: Verify Action using -show cmd #\n'
                       '#########################################\n')
        if self.gbpverify.gbp_action_verify(1,self.act_name,id=act_uuid,action_type='allow'):
           self._log.info('Action Verify using -show cmd == Passed')
        else:
            self._log.info("# Step 2B: Verify Action using -show option == Failed")
            self.cleanup('action',act_uuid)
        ###### 
        self._log.info('\n##########################################\n'
                       '#####   Step 3: Create Classifier  ######\n'
                       '#########################################\n')
        cls_uuid = self.gbpcfg.gbp_policy_cfg_all(1,'classifier',self.class_name,protocol='icmp',direction='bi')
        objs,names=['classifier','action'],[cls_uuid,act_uuid] ## this is needed for cleanup,can append and sort for the sake of order.. but it kept it simple
	if cls_uuid !=0:
            self._log.info('Step 3: Create Classifier Passed,UUID == %s\n' %(cls_uuid))
        else:
            self._log.info("# Step 3: Create Classifier == Failed")
            self.cleanup(objs,names,fail=1)
        self._log.info('\n#########################################\n'
                       '# Step 4A: Verify Classifer using -list cmd #\n'
                       '#########################################\n')
        self._log.info('# Step 4A: Verify Classifier using -list cmd')
        if self.gbpverify.gbp_classif_verify(0,self.class_name,cls_uuid):
           self._log.info('Classifier Verify using -list cmd == Passed')
        else:
            self._log.info("# Step 4A: Verify Classifier using -list option == Failed")
            self.cleanup(objs,names,fail=1)
            
        self._log.info('\n##########################################\n'
                       '# Step 4B: Verify Classifier using -show cmd #\n'
                       '#########################################\n')
        self._log.info('# Step 4B: Verify Classifier using -show cmd')
        if self.gbpverify.gbp_classif_verify(1,self.class_name,id=cls_uuid,protocol='icmp',direction='bi'):
           self._log.info('Classifier Verify using -show cmd == Passed')
        else:
            self._log.info("# Step 4B: Verify Classifier using -show option == Failed")
            self.cleanup(objs,names,fail=1)
            
        ######
        self._log.info('\n#########################################\n'
                       '#####   Step 5: Create Policy Rule  ######\n'
                       '#########################################\n')
        rule_uuid = self.gbpcfg.gbp_policy_cfg_all(1,'rule',self.rule_name,classifier=self.class_name,action=self.act_name)
        objs,names=['rule','classifier','action'],[rule_uuid,cls_uuid,act_uuid]
        if rule_uuid !=0:
            self._log.info('Step 5: Create Policy Rule Passed, UUID == %s\n' %(rule_uuid))
        else:
            self._log.info("# Step 5: Create Policy Rule == Failed")
            self.cleanup(objs,names,fail=1)
            
        self._log.info('\n##########################################\n'
                       '# Step 6A: Verify Policy Rule using -list cmd #\n'
                       '#########################################\n')
        if self.gbpverify.gbp_policy_verify_all(0,'rule',self.rule_name,rule_uuid):
           self._log.info('Verify Policy Rule using -list cmd == Passed')
        else:
            self._log.info("# Step 6A: Verify Policy Rule using -list option == Failed")
            self.cleanup(objs,names,fail=1)
            
        self._log.info('\n###########################################\n'
                       '# Step 6B: Verify Policy Rule using -show cmd #\n'
                       '#########################################\n')
        self._log.info('# Step 6B: Verify Policy Rule using -show cmd')
        if self.gbpverify.gbp_policy_verify_all(1,'rule',self.rule_name,id=rule_uuid,policy_classifier_id=cls_uuid,policy_actions=act_uuid):
           self._log.info('Verify Policy Rule using -show cmd == Passed')
        else:
            self._log.info("# Step 6B: Verify Policy Rule using -show option == Failed")
            self.cleanup(objs,names,fail=1)
            
        ######
        self._log.info('\n###########################################\n'
                       '##### Step 7: Create Policy Rule-Set ####\n'
                       '#########################################\n')
        ruleset_uuid = self.gbpcfg.gbp_policy_cfg_all(1,'ruleset',self.ruleset_name,policy_rules=self.rule_name)
        objs,names=['ruleset','rule','classifier','action'],\
                   [ruleset_uuid,rule_uuid,cls_uuid,act_uuid]
        if ruleset_uuid !=0:
            self._log.info('Step 7: Created Policy Rule-Set Passed, UUID == %s\n' %(ruleset_uuid))
        else:
            self._log.info("# Step 7: Create Policy Rule-Set == Failed")
            self.cleanup(objs,names,fail=1)
            
        self._log.info('\n###########################################\n'
                       '# Step 8A: Verify Policy Rule-Set using -list cmd #\n'
                       '#########################################\n')
        if self.gbpverify.gbp_policy_verify_all(0,'ruleset',self.ruleset_name,ruleset_uuid):
           self._log.info('Verify Policy Rule-Set using -list cmd == Passed')
        else:
            self._log.info("# Step 8A: Verify Policy Rule-Set using -list option == Failed")
            self.cleanup(objs,names,fail=1)
            
        self._log.info('\n###########################################\n'
                       '# Step 8B: Verify Policy Rule-Set using -show cmd #\n'
                       '#########################################\n')
        self._log.info('# Step 8B: Verify Policy Rule-Set using -show cmd')
        if self.gbpverify.gbp_policy_verify_all(1,'ruleset',self.ruleset_name,id=ruleset_uuid,policy_rules=rule_uuid):
           self._log.info('Verify Policy Rule-Set using -show cmd == Passed')
        else:
            self._log.info("# Step 8B: Verify Policy Rule-Set using -show option == Failed")
            self.cleanup(objs,names,fail=1)
            
        self._log.info('\n###########################################\n'
                       '# Step 8B: Verify Implicit-creation of Neutron Security-Group-Obj using -show cmd #\n'
                       '#########################################\n')
        names=['provided_%s' %(self.ruleset_name),'consumed_%s' %(self.ruleset_name)]
        sec_grp_uuid=[]
        for nm in names:
          sgid=self.gbpverify.neut_ver_all('security-group',nm,ret='id')
          if sgid.rstrip() != 0:
            self._log.info('### Step 8C: Implicit-creation of Neutron Security-Group-Obj %s during PRS creation == Passed\n' %(nm))
            sec_grp_uuid.append(sgid)
          else:
           self._log.info('### Step 8C: Implicit-creation of Neutron Security-Group-Obj %s during PRS creation == Failed\n' %(nm)) 
           self.cleanup(objs,names,fail=1)
           

        ####### ====== PROJECT OPERATION ====== 
        self._log.info('\n###########################################\n'
                       '##### Step 9: Create Policy Target-Grp ####\n'
                       '#########################################\n')
        uuids = self.gbpcfg.gbp_policy_cfg_all(1,'group',self.ptg_name,consumed_policy_rule_sets='%s=scope' %(self.ruleset_name))
        if uuids !=0:
            ptg_uuid = uuids[0].rstrip()
            l2pid = uuids[1].rstrip()
            subnetid = uuids[2].rstrip()
            self._log.info('Step 9: Create Policy Target-Grp Passed, UUID == %s\n' %(ptg_uuid))
            objs,names=['group','ruleset','rule','classifier','action'],\
                    [ptg_uuid,ruleset_uuid,rule_uuid,cls_uuid,act_uuid]
        else:
            self._log.info("# Step 9: Create Policy Target-Grp == Failed")
            self.cleanup(objs,names,fail=1)
            
        self._log.info('\n###########################################\n'
                       '# Step 10A: Verify Policy Target-Grp using -list cmd #\n'
                       '#########################################\n')
        if self.gbpverify.gbp_policy_verify_all(0,'group',self.ptg_name,ptg_uuid):
           self._log.info('# Step 10A: Verify Policy Target-Grp using -list cmd == Passed')
        else:
            self._log.info("# Step 10A: Verify Policy Target-Grp using -list option == Failed")
            self.cleanup(objs,names,fail=1)
            
        self._log.info('# Step 10B: Verify Policy Target-Grp using -show cmd')
        if self.gbpverify.gbp_policy_verify_all(1,'group',self.ptg_name,id=ptg_uuid,subnets=subnetid,consumed_policy_rule_sets=ruleset_uuid):
           self._log.info('Verify Policy Target-Grp using -show cmd == Passed')
        else:
            self._log.info("# Step 10B: Verify Policy Target-Grp using -show option == Failed")
            self.cleanup(objs,names,fail=1)
            
        ##### VErifying L2 & L3policies created by default due to above PTG creation.
        ##### L2Policy name is same as PTG_name, when former is created by default
        self._log.info('\n##########################################\n'
                       '# Step 11A: Verify By-Default L2Policy using -show cmd #\n'
                       '#########################################\n')
        ret_uuid=self.gbpverify.gbp_l2l3ntk_pol_ver_all(1,'l2p',self.ptg_name,ret='default',\
                                                        id=l2pid,policy_target_groups=ptg_uuid)
	print "### RETURNED UUIDs == ",ret_uuid
        if ret_uuid!=0 and len(ret_uuid)==2:
            l3pid=ret_uuid[0].rstrip()
            ntkid=ret_uuid[1].rstrip()
            self._log.info("# Step 11A: Verify By-Default L2Policy -show option == Passed")
        else:
            self._log.info("# Step 11A: Verify By-Default L2Policy -show option == Failed")
            self.cleanup(objs,names,fail=1)
            
        self._log.info('# Step 11B: Verify By-Default L3Policy using -show cmd #\n')
        rtr_uuid=self.gbpverify.gbp_l2l3ntk_pol_ver_all(1,'l3p',l3pid,ret='default',\
                                                         id=l3pid,name='default',ip_pool='10.0.0.0/8',\
                                                         l2_policies=l2pid,subnet_prefix_length='26',ip_version='4')
        if rtr_uuid!=0 and isinstance(rtr_uuid,str):
            self._log.info("# Step 11B: Verify By-Default L3Policy -show option == Passed")
        else:
            self._log.info("# Step 11B: Verify By-Default L3Policy -show option == Failed")
            self.cleanup(objs,names,fail=1)
            

        ###### ======== NEUTRON OBJECTS VERIFICATION-- which are created implicitly so far due to PTG creation ======= ######
        self._log.info('\n###########################################\n'
                       '# Step 12A: Verify Implicit Neutron Network-Obj using -show cmd #\n'
                       '#########################################\n')
        net_name='l2p_%s' %(self.ptg_name)
        if self.gbpverify.neut_ver_all('net',ntkid,name=net_name,admin_state_up='True',subnets=subnetid):
           self._log.info("# Step 12A: Implicit-creation of Neutron Network-Obj -show option == Passed")
        else:
           self._log.info("# Step 12A: Implicit-creation of Neutron Network-Obj -show option == Failed")
           self.cleanup(objs,names,fail=1)
           
        self._log.info('\n##########################################\n'
                       '# Step 12B: Verify Implicit Neutron Subnet-Obj using -show cmd #\n'
                       '#########################################\n')
        subnet_name='ptg_%s' %(self.ptg_name)
        if self.gbpverify.neut_ver_all('subnet',subnetid,name=subnet_name,cidr='10.0.0.0/26',\
                                        enable_dhcp='True',network_id=ntkid):
           self._log.info("### Step 12B: Implicit-creation of Neutron SubNet-Obj -show option == Passed")
        else:
           self._log.info("# Step 12B: Implicit-creation of Neutron SubNet-Obj -show option == Failed")
           self.cleanup(objs,names,fail=1)
           
        self._log.info('\n##########################################\n'
                       '# Step 12C: Verify Implicit-creation Neutron Router-Obj using -show cmd #\n'
                       '#########################################\n')
        rtr_name='l3p_default'
        if self.gbpverify.neut_ver_all('router',rtr_uuid,name=rtr_name,admin_state_up='True',status='ACTIVE'):
           self._log.info("### Step 12C: Implicit-creation of Neutron Router-Obj -show option == Passed")
        else:
           self._log.info("### Step 12C: Implicit-creation of Neutron Router-Obj -show option == Failed")
           self.cleanup(objs,names,fail=1)
           
        self._log.info('\n###########################################\n'
                       '# Step 12C: Verify Implicit-creation of Neutron Security-Obj using -show cmd #\n'
                       '#########################################\n')
        def_secgrp_id = self.gbpverify.neut_ver_all('security-group','gbp_%s' %(ptg_uuid),ret='id',description='default')
        if def_secgrp_id !=0:
           self._log.info('#### Step 12D: Implicit-creation of Neutron Security-Group-Obj during PTG creation == Passed\n')
           chk_secgrp_id = [def_secgrp_id,sec_grp_uuid[1]]  ## index 1 for sec_grp_uuid becoz port-crtd in cons_prs
        else:
           self._log.info('#### Step 12D: Implicit-creation of Neutron Security-Group-Obj during PTG creation == Failed\n')
           self.cleanup(objs,names,fail=1)
           

        self._log.info('\n##################################################\n'
                       '# Step 13: Create Policy Targets and instantiate VM #\n'
                       '######################################################\n')
        ret_uuids=self.gbpcfg.gbp_policy_cfg_all(1,'target',self.tg_name,policy_target_group=self.ptg_name)
        if ret_uuids != 0 and len(ret_uuids) == 2:
           pt_uuid,port_uuid = ret_uuids[0],ret_uuids[1]
           objs,names=['target','group','ruleset','rule','classifier','action'],\
                      [pt_uuid,ptg_uuid,ruleset_uuid,rule_uuid,cls_uuid,act_uuid]
           self._log.info("# Step 13: Creation of Policy Target Passed, UUID == %s\n" %(pt_uuid))
        else:
           self._log.info("# Step 13: Creation of Policy Target == Failed")
           self.cleanup(objs,names,fail=1)
           
        if self.gbpverify.gbp_policy_verify_all(0,'target',self.tg_name,pt_uuid,ptg_uuid):
           self._log.info('Verify Policy Targe using -list cmd == Passed')
        else:
            self._log.info("# Step 14A: Verify Policy Target-Grp using -list option == Failed")
            self.cleanup(objs,names,fail=1)
            
        self._log.info('\n###########################################\n'
                       '# Step 14B: Verify Policy Target-Grp using -show cmd #\n'
                       '#########################################\n')
        self._log.info('# Step 14B: Verify Policy Target-Grp using -show cmd')
        if self.gbpverify.gbp_policy_verify_all(1,'target',self.tg_name,id=pt_uuid,policy_target_group_id=ptg_uuid):
           self._log.info('Verify Policy Target-Grp using -show cmd == Passed')
        else:
            self._log.info("# Step 14B: Verify Policy Target-Grp using -show option == Failed")
            self.cleanup(objs,names,fail=1)
            

        ###### ======== NEUTRON OBJECTS PORTS & SECURITY-GROUP VERIFICATION-- which are created implicitly so far due to PT & PTG creation ======= ######
        self._log.info('#### Step 14A: Verify Implicit Neutron Port-Obj using -show cmd #\n')
        port_name = 'pt_%s' %(self.tg_name)
        ret_id=self.gbpverify.neut_ver_all('port',port_uuid,name=port_name,network_id=ntkid,status='DOWN',security_groups=chk_secgrp_id)
        if ret_id !=0:
           neut_sec_grp_id=ret_id
           self._log.info("# Step 15A: Implicit-creation of Neutron Port-Obj -show option == Passed\n")
        else:
           self._log.info("# Step 15A: Implicit-creation of Neutron Port-Obj -show option == Failed\n")
           self.cleanup(objs,names,fail=1)
        self._log.info('Testcase test_gbp_1 PASSED')
        self.cleanup(objs,names)
        

if __name__ == '__main__':
    main()
