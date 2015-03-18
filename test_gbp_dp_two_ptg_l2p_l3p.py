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
    hdlr = logging.FileHandler('/tmp/test_gbp_2.log')
    _log.setLevel(logging.INFO)
    _log.setLevel(logging.DEBUG)

    def __init__(self, heat_template):
      """
      Initial Heat-based Config setup 
      """
      self.gbpcfg = Gbp_Config()
      self.gbpverify = Gbp_Verify()
      ## Heat Stack Create
      self.heatstack_name= stack_two_ptg_l2p_l3p
      if self.gbpcfg.gbp_heat_cfg_all(1,heat_template,self.heatstack_name) == 0:
         _log.info("\n ABORTING THE TESTSUITE RUN")
         self.gbpcfg.gbp_heat_cfg_all(0,heat_template,self.heatstack_name) ## Stack delete will caause cleanup
      ## Port Create  
      self.mgmt_pt_list = ['vm1_mgmt', 'vm2_mgmt']
      self.data_pt_list = ['vm1_data', 'vm2_data']
      self.vm1 = {}
      self.vm2 = {}
      self.ptgs = {} ## such that key names as 'data' & 'mgmt'
      for vm in {self.vm1,self.vm2}:
        for key,val in self.ptgs.iteritems():
           port=self.gbpcfg.gbp_policy_cfg_all(1,'target','vm1_pt',policy_target_group='%s' %(val))
           if port != 0:
              vm[key] = port[1]
      
        self.gbpcfg.gbp_vm_create([self.vm1['mgmt'],self.vm1['data']]) ## VM create
         
    def cleanup(self):
        self.gbpcfg.gbp_heat_cfg_all(0,heat_template,self.heatstack_name) ## Calling stack delete

    def test_icmp_udp_1(self):
        
    def test_icmp_tcp_2(self):

    def test_tcp_udp_3(self):
 
    def test_icmp_udp_4(self):

    def test_icmp_tcp_5(self):

    def test_tcp_udp_6(self):

if __name__ == '__main__':
    main()
