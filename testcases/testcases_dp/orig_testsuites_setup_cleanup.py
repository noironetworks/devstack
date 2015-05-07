#!/usr/bin/env python

import sys
import logging
import os
import datetime
import yaml
from libs.gbp_conf_libs import Gbp_Config
from libs.gbp_verify_libs import Gbp_Verify
from libs.gbp_heat_libs import Gbp_Heat
from libs.gbp_nova_libs import Gbp_Nova
from libs.raise_exceptions import *


class super_hdr(object):

  with open('test_var_def.yaml','rt') as f:
           conf = yaml.load(f)
  nova_az = conf['nova_az_name']
  cntlr_ip = conf['controller_ip']
  num_host = conf['num_comp_nodes']
  heat_temp = conf['main_setup_heat_temp']
  stack_name = conf ['heat_stack_name']
  vm_image = conf['vm_image']
  sshkeyname = conf ['key_name']
  gbpcfg = Gbp_Config()
  gbpverify = Gbp_Verify()
  gbpnova = Gbp_Nova(cntlr_ip)
  gbpheat = Gbp_Heat(cntlr_ip)

  def vm_create(self,ptgs,vmlist):
    """
    Create VMs
    """
    ## ptg_id should be a dict with keys as 'data' & 'mgmt'
    ## vm_list: list of dicts
    for vm in vmlist:
        for key,val in ptgs.iteritems():
            port=self.gbpcfg.gbp_policy_cfg_all(1,'target','vm_%s' %(key),policy_target_group='%s' %(val))
            if port != 0:
               vm[key] = port[1]
            else:
               raise TestSuiteAbort("Policy Targets creation Failed")
            print vm
        if self.gbpnova.vm_create_cli(vm['name'],self.vm_image,[vm['mgmt'],vm['data']],self.sshkeyname,avail_zone=vm['az']) == 0: ## VM create
           return 0

class header1(super_hdr):
    def __init__(self):
      """
      Initial Heat-based Config setup 
      """
      self.hdr = super_hdr()
      self.gbpcfg = self.hdr.gbpcfg
      self.gbpnova = self.hdr.gbpnova
      self.gbpheat = self.hdr.gbpheat
      self.stack_name = self.hdr.stack_name
      self.heat_temp = self.hdr.heat_temp

    def setup(self):
      """
      Create Four VMs: VM1,VM2,VM9 & VM10
      VM1 & VM2: To be used for Same Host location Testcase
      VM9 & VM10: to be used for Diff host location Testcase
      vm1,vm2 &vm9 locates in the AZ-node
      """
      ptgs = {}
      #ptgs['mgmt']=self.gbpheat.get_output_cli(self.stack_name,self.heat_temp)['demo_mgmt_ptg_id']
      ptgs['data']=self.gbpheat.get_output_cli(self.stack_name,self.heat_temp)['demo_same_ptg_l2p_l3p_ptg_id']
      print ptgs
      vm1 = {'name':'VM1','az':self.nova_az}
      vm2 = {'name':'VM2','az':self.nova_az}
      vm3 = {'name':'VM9','az':self.nova_az}
      vm4 = {'name':'VM10','az':''}
      vm_list = [vm1,vm2,vm3,vm4]
      self.vm_name_list = [vm1['name'],vm2['name'],vm3['name'],vm4['name']]
      try:
        if self.hdr.vm_create(ptgs,vm_list) == 0:
           #Jishnu self.cleanup()
           raise TestSuiteAbort("VM Creation Failed")
      except TestSuiteAbort as err:
           print err
           pass

    def cleanup(self):
        self.gbpnova.sshkey_for_vm('gbpssh',action='delete')
        for vmname in self.vm_name_list: #Blind cleanup
            self.gbpnova.vm_delete(vmname)
        self.gbpcfg.gbp_del_all_anyobj('target')     
    

class header2(super_hdr):

    def __init__(self):
      """
      Initial Heat-based Config setup
      """
      self.hdr = super_hdr()
      self.gbpcfg = self.hdr.gbpcfg
      self.gbpnova = self.hdr.gbpnova
      self.gbpheat = self.hdr.gbpheat
      self.stack_name = self.hdr.stack_name
      self.heat_temp = self.hdr.heat_temp

    def setup(self):
      """
      Create Four VMs: vm3,vm4,vm11 & vm12
      VM3 & VM4: To be used for Same Host location Testcase
      VM11 & VM12: to be used for Diff host location Testcase
      VM3,VM4 & VM11 locates in the AZ-node
      """
      ptg_pair_1,ptg_pair_2 = {},{}
      mgmt_ptg_uuid=self.gbpheat.get_output_cli(self.stack_name,self.heat_temp)['demo_mgmt_ptg_id']
      ptg_pair_1['mgmt'],ptg_pair_2['mgmt']=mgmt_ptg_uuid,mgmt_ptg_uuid
      ptg_pair_1['data']=self.gbpheat.get_output_cli(self.stack_name,self.heat_temp)['demo_diff_ptg_same_l2p_l3p_ptg1_id']
      ptg_pair_2['data']=self.gbpheat.get_output_cli(self.stack_name,self.heat_temp)['demo_diff_ptg_same_l2p_l3p_ptg2_id']
      print ptg_pair_1, ptg_pair_2
      vm1 = {'name':'VM3','az':self.nova_az}
      vm2 = {'name':'VM4','az':self.nova_az}
      vm3 = {'name':'VM11','az':self.nova_az}
      vm4 = {'name':'VM12','az':''}
      vm_pair_1 = [vm1,vm2]
      vm_pair_2 = [vm3,vm4]
      self.vm_pair_1_name = [vm1['name'],vm2['name']]
      self.vm_pair_2_name = [vm3['name'],vm4['name']]
      try: 
        if self.hdr.vm_create(ptg_pair_1,vm_pair_1) == 0:
           #Jishnu  self.cleanup()
           raise TestSuiteAbort("VM Creation Failed")
        if self.hdr.vm_create(ptg_pair_2,vm_pair_2) == 0:
           #Jishnu  self.cleanup()
           raise TestSuiteAbort("VM Creation Failed")
      except TestSuiteAbort as err:
           print err
           pass
 
    def cleanup(self):
        self.gbpnova.sshkey_for_vm('gbpssh',action='delete')
        for vmname in self.vm_pair_1_name: #Blind cleanup
            self.gbpnova.vm_delete(vmname)
        for vmname in self.vm_pair_2_name: 
            self.gbpnova.vm_delete(vmname)
        self.gbpcfg.gbp_del_all_anyobj('target')


class header3(super_hdr):

    def __init__(self):
      """
      Initial Heat-based Config setup
      """
      self.hdr = super_hdr()
      self.gbpcfg = self.hdr.gbpcfg
      self.gbpnova = self.hdr.gbpnova
      self.gbpheat = self.hdr.gbpheat
      self.stack_name = self.hdr.stack_name
      self.heat_temp = self.hdr.heat_temp

    def setup(self):
      """
      Create Four VMs: VM5,VM6,VM13 & VM14
      VM5 &VM6: To be used for Same Host location Testcase
      VM13 & VM14: to be used for Diff host location Testcase
      VM5,VM6 &VM13 locates in the AZ-node
      """
      ptg_pair_1,ptg_pair_2 = {},{}
      mgmt_ptg_uuid=self.gbpheat.get_output_cli(self.stack_name,self.heat_temp)['demo_mgmt_ptg_id']
      ptg_pair_1['mgmt'],ptg_pair_2['mgmt']=mgmt_ptg_uuid,mgmt_ptg_uuid
      ptg_pair_1['data']=self.gbpheat.get_output_cli(self.stack_name,self.heat_temp)['demo_diff_ptg_l2p_same_l3p_ptg1_id']
      ptg_pair_2['data']=self.gbpheat.get_output_cli(self.stack_name,self.heat_temp)['demo_diff_ptg_l2p_same_l3p_ptg2_id']
      vm1 = {'name':'VM5','az':self.nova_az}
      vm2 = {'name':'VM6','az':self.nova_az}
      vm3 = {'name':'VM13','az':self.nova_az}
      vm4 = {'name':'VM14','az':''}
      vm_pair_1 = [vm1,vm2]
      vm_pair_2 = [vm3,vm4]
      self.vm_pair_1_name = [vm1['name'],vm2['name']]
      self.vm_pair_2_name = [vm3['name'],vm4['name']]
      try:
        if self.hdr.vm_create(ptg_pair_1,vm_pair_1) == 0:
           #Jishnu  self.cleanup()
           raise TestSuiteAbort("VM Creation Failed")
        if self.hdr.vm_create(ptg_pair_2,vm_pair_2) == 0:
           #Jishnu  self.cleanup()
           raise TestSuiteAbort("VM Creation Failed")
      except TestSuiteAbort as err:
           print err
           pass

    def cleanup(self):
        self.gbpnova.sshkey_for_vm('gbpssh',action='delete')
        for vmname in self.vm_pair_1_name: #Blind cleanup
            self.gbpnova.vm_delete(vmname)
        for vmname in self.vm_pair_2_name:
            self.gbpnova.vm_delete(vmname)
        self.gbpcfg.gbp_del_all_anyobj('target')


class header4(super_hdr):

    def __init__(self):
      """
      Initial Heat-based Config setup
      """
      self.hdr = super_hdr()
      self.gbpcfg = self.hdr.gbpcfg
      self.gbpnova = self.hdr.gbpnova
      self.gbpheat = self.hdr.gbpheat
      self.stack_name = self.hdr.stack_name
      self.heat_temp = self.hdr.heat_temp

    def setup(self):
      """
      Create Four VMs: VM7,VM8,VM15 & VM16
      VM7 &VM8: To be used for Same Host location Testcase
      VM15 & VM16: to be used for Diff host location Testcase
      VM7,VM8 &VM15 locates in the AZ-node
      """
      ptg_pair_1,ptg_pair_2 = {},{}
      mgmt_ptg_uuid=self.gbpheat.get_output_cli(self.stack_name,self.heat_temp)['demo_mgmt_ptg_id']
      ptg_pair_1['mgmt'],ptg_pair_2['mgmt']=mgmt_ptg_uuid,mgmt_ptg_uuid
      ptg_pair_1['data']=self.gbpheat.get_output_cli(self.stack_name,self.heat_temp)['demo_diff_ptg_l2p_l3p_ptg1_id']
      ptg_pair_2['data']=self.gbpheat.get_output_cli(self.stack_name,self.heat_temp)['demo_diff_ptg_l2p_l3p_ptg2_id']
      print ptg_pair_1,ptg_pair_2
      vm1 = {'name':'VM7','az':self.nova_az}
      vm2 = {'name':'VM8','az':self.nova_az}
      vm3 = {'name':'VM15','az':self.nova_az}
      vm4 = {'name':'VM16','az':''}
      vm_pair_1 = [vm1,vm2]
      vm_pair_2 = [vm3,vm4]
      self.vm_pair_1_name = [vm1['name'],vm2['name']]
      self.vm_pair_2_name = [vm3['name'],vm4['name']]
      try:
        if self.hdr.vm_create(ptg_pair_1,vm_pair_1) == 0:
           #Jishnu  self.cleanup()
           raise TestSuiteAbort("VM Creation Failed")
        if self.hdr.vm_create(ptg_pair_2,vm_pair_2) == 0:
           #Jishnu  self.cleanup()
           raise TestSuiteAbort("VM Creation Failed")
      except TestSuiteAbort as err:
           print err
           pass

    def cleanup(self):
        self.gbpnova.sshkey_for_vm('gbpssh',action='delete')
        for vmname in self.vm_pair_1_name: #Blind cleanup
            self.gbpnova.vm_delete(vmname)
        for vmname in self.vm_pair_2_name:
            self.gbpnova.vm_delete(vmname)
        self.gbpcfg.gbp_del_all_anyobj('target')



