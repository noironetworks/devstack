#!/usr/bin/python

import sys
import logging
import os
import datetime
import yaml
from time import sleep
from libs.gbp_conf_libs import Gbp_Config
from libs.gbp_verify_libs import Gbp_Verify
from libs.gbp_heat_libs import Gbp_Heat
from libs.gbp_nova_libs import Gbp_Nova
from libs.gbp_utils import *

class nat_dp_main_config(object):
    """
    The intent of this class is to setup the complete GBP config 
    needed for running all DP testcases
    """
    # Initialize logging
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=logging.WARNING)
    _log = logging.getLogger( __name__ )
    hdlr = logging.FileHandler('/tmp/test_gbp_natdp_main_config.log')
    _log.setLevel(logging.INFO)
    _log.setLevel(logging.DEBUG)

    def __init__(self,cfg_file):
      """
      Iniatizing the test-cfg variables & classes
      """
      with open(cfg_file,'rt') as f:
           conf = yaml.load(f)
      self.nova_agg = conf['nova_agg_name']
      self.nova_az = conf['nova_az_name']
      self.comp_node = conf['az_comp_node']
      self.ntk_node = conf['ntk_node']
      self.cntlr_ip = conf['controller_ip']
      self.extgw = conf['ext_gw_rtr']
      self.apic_ip = conf['apic_ip']
      self.heat_temp_test = conf['main_setup_heat_temp']
      self.num_hosts = conf['num_comp_nodes']
      self.heat_stack_name = conf['heat_stack_name']
      self.ips_of_extgw = [conf['fip1_of_extgw'],conf['fip2_of_extgw'],self.extgw]
      self.gbpcfg = Gbp_Config()
      self.gbpverify = Gbp_Verify()
      self.gbpnova = Gbp_Nova(self.cntlr_ip)
      self.gbpheat = Gbp_Heat(self.cntlr_ip)
      
    
    def setup(self,getfips=0):
      """
      Availability Zone creation
      Heat Stack Creates All Test Config
      Generate dict comprising VM-name and FIPs
      <getfips> : Added this getfips, just runner to fetch FIPs
                  without having to run the whole setup, assuming
                  that setup was run before and the VMs exist
      """
      if getfips == 0:
       """
       if self.gbpnova.quota_update()==0:
         self._log.info("\n ABORTING THE TESTSUITE RUN, Updating the Nova Quota's Failed")
         sys.exit(1)
       if self.num_hosts > 1:
         self.agg_id = self.gbpnova.avail_zone('api','create',self.nova_agg,avail_zone_name=self.nova_az)
         if self.agg_id == 0:
            self._log.info("\n ABORTING THE TESTSUITE RUN,nova host aggregate creation Failed")
            sys.exit(1)
         self._log.info(" Agg %s" %(self.agg_id))
         if self.gbpnova.avail_zone('api','addhost',self.agg_id,hostname=self.comp_node) == 0:
            self._log.info("\n ABORTING THE TESTSUITE RUN, availability zone creation Failed")
            self.gbpnova.avail_zone('cli','delete',self.agg_id) #Cleanup Agg_ID
            sys.exit(1)
       """
       if self.gbpheat.cfg_all_cli(1,self.heat_stack_name,heat_temp=self.heat_temp_test) == 0:
         self._log.info("\n ABORTING THE TESTSUITE RUN, HEAT STACK CREATE of %s Failed" %(self.heat_stack_name))
         #self.gbpheat.cfg_all_cli(0,self.heat_stack_name) ## Stack delete will cause cleanup
         self.cleanup()
         sys.exit(1)
      
       sleep(5) # Sleep 5s assuming that all objects areated in APIC
       self._log.info("\n ADDING SSH-Filter to Svc_epg created for every dhcp_agent")
       svc_epg_list = [
                      'APPL2P1',\
                      'WEBL2P1',\
                      'WEBL2P2'
                     ]
       create_add_filter(self.apic_ip,svc_epg_list)
      
      if getfips==0 or getfips==1:
         ### <Generate the dict comprising VM-name and its FIPs > ###
         targetvm_list = ['Web-Server','Web-Client-1','Web-Client-2','App-Server']
         fipsOftargetVMs = {}
         for vm in targetvm_list:
           fipsOftargetVMs[vm] = self.gbpnova.get_any_vm_property(vm)['networks'][0][1:3]
         print 'FIPs of Target VMs == %s' %(fipsOftargetVMs)
         return fipsOftargetVMs

    def cleanup(self):
        ##Need to call for instance delete if there is an instance
        self.gbpheat.cfg_all_cli(0,self.heat_stack_name)
        self.gbpnova.avail_zone('cli','removehost',self.nova_agg,hostname=self.comp_node)
        self.gbpnova.avail_zone('cli','delete',self.agg_id)
        #Ntk namespace cleanup in Network-Node.. VM names are static throughout the test-cycle
        self.gbpcfg.del_netns(self.ntk_node)
        sys.exit(1)
