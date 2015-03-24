#!/usr/bin/python

import sys
import logging
import os
import datetime
from libs.gbp_conf_libs import Gbp_Config
from libs.gbp_verify_libs import Gbp_Verify
from libs.gbp_heat_libs import Gbp_Heat
from libs.gbp_nova_libs import Gbp_Nova


def vm_az_create(agg_name,az_name,comp_node_name,num_host,ptgs):
    """
    Creates Avail-zone
    Create two VMs
    """
    ## Create Avail-zone
    gbp_nova = Gbp_Nova()
    gbp_cfg = Gbp_Config
    agg_id = gbp_nova.avail_zone('api','create',agg_name,avail_zone_name=az_name)
    print 'Agg %s' %(agg_id)
    if gbp_nova.avail_zone('api','addhost',agg_id,hostname=comp_node_name) == 0:
         return 0

    ## ptg_id should be a dict with keys as 'data' & 'mgmt'
    vm1 = {'name':'VM1','az':az_name}
    vm2 = {'name':'VM2','az':az_name}
    if num_host > 1:
         vm2['az']=''
    for vm in [vm1,vm2]:
        for key,val in ptgs.iteritems():
            port=gbp_cfg.gbp_policy_cfg_all(1,'target','vm1_%s' %(key),policy_target_group='%s' %(val))
            if port != 0:
               vm[key] = port[1]
            print vm
        if gbp_nova.vm_create_cli(vm['name'],[vm['mgmt'],vm['data']],avail_zone=vm['az']) == 0: ## VM create
           return 0

def cleanup(vms):
    """
    Cleanup for every Setup call
    """
    return 1


class header1(object):

    def __init__(self,num_host):
      """
      Initial Heat-based Config setup 
      """
      self.gbpcfg = Gbp_Config()
      self.gbpverify = Gbp_Verify()
      self.gbpnova = Gbp_Nova('172.28.184.65')
      self.gbpheat = Gbp_Heat('172.28.184.65')
      self.heat_temp_demo = 'same_ptg_L2p_L3p.yaml' # Assumption the temp is co-located with the testcase
      self.heat_temp_com = 'common.yaml' # Assumption as above
      self.nova_agg = 'gbp_agg'
      self.nova_az = 'gbp_zone'
      self.comp_node = 'f5-compute-1.cisco.com'
      self.num_host = num_host
    
    def setup(self):
      """
      Creates Avail-zone
      Create two VMs
      """
      ptgs = {}
      ptgs['mgmt']=self.gbpheat.get_output_cli('common-stack',self.heat_temp_com)['mgmt_ptg_id']
      ptgs['data']=self.gbpheat.get_output_cli('demo-stack',self.heat_temp_demo)['demo_ptg_id']
      print ptgs
      if vm_az_create(self.nova_agg,self.nova_az,self.comp_node,self.num_host,ptgs) == 0:
         print "TEST RUN ABORT" #TODO: raise custom exception
         cleanup()

    def cleanup(self):
        ##Need to call for instance delete if there is an instance
        self.gbpcfg.gbp_heat_cfg_all(0,heat_template,self.heatstack_name) ## Calling stack delete
    
class header2(object):

    def __init__(self,num_host):
      """
      Initial Heat-based Config setup
      """
      self.gbpcfg = Gbp_Config()
      self.gbpverify = Gbp_Verify()
      self.gbpnova = Gbp_Nova('172.28.184.65')
      self.gbpheat = Gbp_Heat('172.28.184.65')
      self.heat_temp_demo = 'same_ptg_L2p_L3p.yaml' # Assumption the temp is co-located with the testcase
      self.heat_temp_com = 'common.yaml' # Assumption as above
      self.nova_agg = 'gbp_agg'
      self.nova_az = 'gbp_zone'
      self.comp_node = 'f5-compute-1.cisco.com'
      self.num_host = num_host

    def setup(self):
      """
      Creates Avail-zone
      Create two VMs
      """
      ptgs = {}
      ptgs['mgmt']=self.gbpheat.get_output_cli('common-stack',self.heat_temp_com)['mgmt_ptg_id']
      ptgs['data']=self.gbpheat.get_output_cli('demo-stack',self.heat_temp_demo)['demo_ptg_id']
      print ptgs
      if vm_az_create(self.nova_agg,self.nova_az,self.comp_node,self.num_host,ptgs) == 0:
         print "TEST RUN ABORT" #TODO: raise custom exception
         cleanup()

    def cleanup(self):
        ##Need to call for instance delete if there is an instance
        self.gbpcfg.gbp_heat_cfg_all(0,heat_template,self.heatstack_name) ## Calling stack delete

class header3(object):

    def __init__(self,num_host):
      """
      Initial Heat-based Config setup
      """
      self.gbpcfg = Gbp_Config()
      self.gbpverify = Gbp_Verify()
      self.gbpnova = Gbp_Nova('172.28.184.65')
      self.gbpheat = Gbp_Heat('172.28.184.65')
      self.heat_temp_demo = 'same_ptg_L2p_L3p.yaml' # Assumption the temp is co-located with the testcase
      self.heat_temp_com = 'common.yaml' # Assumption as above
      self.nova_agg = 'gbp_agg'
      self.nova_az = 'gbp_zone'
      self.comp_node = 'f5-compute-1.cisco.com'
      self.num_host = num_host

    def setup(self):
      """
      Creates Avail-zone
      Create two VMs
      """
      ptgs = {}
      ptgs['mgmt']=self.gbpheat.get_output_cli('common-stack',self.heat_temp_com)['mgmt_ptg_id']
      ptgs['data']=self.gbpheat.get_output_cli('demo-stack',self.heat_temp_demo)['demo_ptg_id']
      print ptgs
      if vm_az_create(self.nova_agg,self.nova_az,self.comp_node,self.num_host,ptgs) == 0:
         print "TEST RUN ABORT" #TODO: raise custom exception
         cleanup()

    def cleanup(self):
        ##Need to call for instance delete if there is an instance
        self.gbpcfg.gbp_heat_cfg_all(0,heat_template,self.heatstack_name) ## Calling stack delete


class header4(object):

    def __init__(self,num_host):
      """
      Initial Heat-based Config setup
      """
      self.gbpcfg = Gbp_Config()
      self.gbpverify = Gbp_Verify()
      self.gbpnova = Gbp_Nova('172.28.184.65')
      self.gbpheat = Gbp_Heat('172.28.184.65')
      self.heat_temp_demo = 'same_ptg_L2p_L3p.yaml' # Assumption the temp is co-located with the testcase
      self.heat_temp_com = 'common.yaml' # Assumption as above
      self.nova_agg = 'gbp_agg'
      self.nova_az = 'gbp_zone'
      self.comp_node = 'f5-compute-1.cisco.com'
      self.num_host = num_host

    def setup(self):
      """
      Creates Avail-zone
      Create two VMs
      """
      ptgs = {}
      ptgs['mgmt']=self.gbpheat.get_output_cli('common-stack',self.heat_temp_com)['mgmt_ptg_id']
      ptgs['data']=self.gbpheat.get_output_cli('demo-stack',self.heat_temp_demo)['demo_ptg_id']
      print ptgs
      if vm_az_create(self.nova_agg,self.nova_az,self.comp_node,self.num_host,ptgs) == 0:
         print "TEST RUN ABORT" #TODO: raise custom exception
         cleanup()

    def cleanup(self):
        ##Need to call for instance delete if there is an instance
        self.gbpcfg.gbp_heat_cfg_all(0,heat_template,self.heatstack_name) ## Calling stack delete




  
if __name__ == '__main__':
    main()
