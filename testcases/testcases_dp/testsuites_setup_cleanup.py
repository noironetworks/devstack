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

  with open('testconfig_def.yaml','rt') as f:
           conf = yaml.load(f)
  nova_az = conf['nova_az_name']
  cntlr_ip = conf['controller_ip']
  num_host = conf['num_comp_nodes']
  heat_temp = conf['main_setup_heat_temp']
  stack_name = conf ['heat_stack_name']
  vm_image = conf['vm_image']
  sshkeyname = conf['key_name']
  ntk_node = conf['ntk_node']
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
        if self.gbpnova.vm_create_cli(vm['name'],self.vm_image,vm['data'],avail_zone=vm['az']) == 0: # removed mgmt_nic
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
      Create Three VMs: VM1,VM2,VM3
      VM1 & VM2: To be used for Same Host location Testcase
      VM3: to be used for Diff host location Testcase
      vm1,vm2 locates in the AZ-node
      """
      ptgs = {}
      #ptgs['mgmt']=self.gbpheat.get_output_cli(self.stack_name,self.heat_temp)['demo_mgmt_ptg_id']
      ptgs['data']=self.gbpheat.get_output_cli(self.stack_name,self.heat_temp)['demo_same_ptg_l2p_l3p_ptg_id']
      print ptgs
      vm1 = {'name':'VM1','az':self.nova_az}
      vm2 = {'name':'VM2','az':self.nova_az}
      vm3 = {'name':'VM3','az':''}
      vm_list = [vm1,vm2,vm3]
      self.vm_name_list = [vm1['name'],vm2['name'],vm3['name']]
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
      Create Three VMs: vm4,vm5,vm6
      VM4 & VM5: To be used for Same Host location Testcase
      VM6: to be used for Diff host location Testcase
      VM3,VM4 locates in the AZ-node
      """
      ptg_pair_1,ptg_pair_2 = {},{}
      #mgmt_ptg_uuid=self.gbpheat.get_output_cli(self.stack_name,self.heat_temp)['demo_mgmt_ptg_id']
      #ptg_pair_1['mgmt'],ptg_pair_2['mgmt']=mgmt_ptg_uuid,mgmt_ptg_uuid
      ptg_pair_1['data']=self.gbpheat.get_output_cli(self.stack_name,self.heat_temp)['demo_diff_ptg_same_l2p_l3p_ptg1_id']
      ptg_pair_2['data']=self.gbpheat.get_output_cli(self.stack_name,self.heat_temp)['demo_diff_ptg_same_l2p_l3p_ptg2_id']
      print ptg_pair_1, ptg_pair_2
      vm1 = {'name':'VM4','az':self.nova_az}
      vm2 = {'name':'VM5','az':self.nova_az}
      vm3 = {'name':'VM6','az':''}
      vm_pair_1 = [vm1]
      vm_pair_2 = [vm2,vm3]
      self.vm_pair_1_name = [vm1['name']]
      self.vm_pair_2_name = [vm2['name'],vm3['name']]
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
      Create Four VMs: VM7,VM8,VM9
      VM7 & VM8: To be used for Same Host location Testcase
      VM9: to be used for Diff host location Testcase
      VM7,VM8 locates in the AZ-node
      """
      ptg_pair_1,ptg_pair_2 = {},{}
      #mgmt_ptg_uuid=self.gbpheat.get_output_cli(self.stack_name,self.heat_temp)['demo_mgmt_ptg_id']
      #ptg_pair_1['mgmt'],ptg_pair_2['mgmt']=mgmt_ptg_uuid,mgmt_ptg_uuid
      ptg_pair_1['data']=self.gbpheat.get_output_cli(self.stack_name,self.heat_temp)['demo_diff_ptg_l2p_same_l3p_ptg1_id']
      ptg_pair_2['data']=self.gbpheat.get_output_cli(self.stack_name,self.heat_temp)['demo_diff_ptg_l2p_same_l3p_ptg2_id']
      vm1 = {'name':'VM7','az':self.nova_az}
      vm2 = {'name':'VM8','az':self.nova_az}
      vm3 = {'name':'VM9','az':''}
      vm_pair_1 = [vm1]
      vm_pair_2 = [vm2,vm3]
      self.vm_pair_1_name = [vm1['name']]
      self.vm_pair_2_name = [vm2['name'],vm3['name']]
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
      Create Four VMs: VM10,VM11,VM12
      VM10 &VM11: To be used for Same Host location Testcase
      VM12: to be used for Diff host location Testcase
      VM10,VM11 locates in the AZ-node
      """
      ptg_pair_1,ptg_pair_2 = {},{}
      #mgmt_ptg_uuid=self.gbpheat.get_output_cli(self.stack_name,self.heat_temp)['demo_mgmt_ptg_id']
      #ptg_pair_1['mgmt'],ptg_pair_2['mgmt']=mgmt_ptg_uuid,mgmt_ptg_uuid
      ptg_pair_1['data']=self.gbpheat.get_output_cli(self.stack_name,self.heat_temp)['demo_diff_ptg_l2p_l3p_ptg1_id']
      ptg_pair_2['data']=self.gbpheat.get_output_cli(self.stack_name,self.heat_temp)['demo_diff_ptg_l2p_l3p_ptg2_id']
      print ptg_pair_1,ptg_pair_2
      vm1 = {'name':'VM10','az':self.nova_az}
      vm2 = {'name':'VM11','az':self.nova_az}
      vm3 = {'name':'VM12','az':''}
      vm_pair_1 = [vm1]
      vm_pair_2 = [vm2,vm3]
      self.vm_pair_1_name = [vm1['name']]
      self.vm_pair_2_name = [vm2['name'],vm3['name']]
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



