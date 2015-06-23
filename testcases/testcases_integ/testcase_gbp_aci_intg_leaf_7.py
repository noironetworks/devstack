#!/usr/bin/python

import sys
import logging
import os
import datetime
import yaml
import string
from time import sleep
from libs.gbp_conf_libs import Gbp_Config
from libs.gbp_verify_libs import Gbp_Verify
from libs.gbp_heat_libs import Gbp_Heat
from libs.raise_exceptions import *
from libs.gbp_aci_libs import Gbp_Aci
from test_utils import *


class  testcase_gbp_aci_intg_leaf_7(object):
    """
    This is a GBP_ACI Integration TestCase
    """
    # Initialize logging
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=logging.WARNING)
    _log = logging.getLogger( __name__ )
    hdlr = logging.FileHandler('/tmp/ testcase_gbp_aci_intg_leaf_7.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    _log.addHandler(hdlr)
    _log.setLevel(logging.INFO)
    _log.setLevel(logging.DEBUG)

    def __init__(self,params):

      self.gbpcfg = Gbp_Config()
      self.gbpverify = Gbp_Verify()
      self.gbpaci = Gbp_Aci()
      self.heat_stack_name = 'gbpleaf7'
      cntlr_ip = params['cntlr_ip']
      self.heat_temp_test = params['heat_temp_file']
      self.gbpheat = Gbp_Heat(cntlr_ip)
      self.gbpnova = Gbp_Nova(cntlr_ip)
      self.apic_ip = params['apic_ip']
      self.az_comp_node = params['az_comp_node']
      self.nova_agg = params['nova_agg']
      self.nova_az = params['nova_az']
      self.ntk_node = params['ntk_node']
      self.leaf_port1 = params['leaf1_port1']
      self.leaf_port2 = params['leaf1_port2']
      self.node_id = params['leaf1_node_id']
      objs_uuid = self.gbpverify.get_uuid_from_stack(self.heat_temp_test,self.heat_stack_name)
      self.ptg_1 = objs_uuid['server_ptg_1']
      self.ptg_2 = objs_uuid['client_ptg_1']
      self.test_1_prs = objs_uuid['demo_ruleset_icmp_id']
      self.test_2_prs = objs_uuid['demo_ruleset_tcp_id']
      self.test_3_prs = objs_uuid['demo_ruleset_udp_id']
      self.test_4_prs = objs_uuid['demo_ruleset_icmp_tcp_id']
      self.test_5_prs = objs_uuid['demo_ruleset_icmp_udp_id']
      self.test_6_prs = objs_uuid['demo_ruleset_tcp_udp_id']
      self.prs_proto = {self.test_1_prs:['icmp'],self.test_2_prs:['tcp'],self.test_3_prs:['udp'],\
                   self.test_4_prs:['icmp','tcp'],self.test_5_prs:['icmp','udp'],self.test_6_prs:['tcp','udp']}

    def test_runner(self):
        """
        Method to run the Testcase in Ordered Steps
        """
        test_name = 'DISCONN_LEAF_UPDATECFG_RECONN_LEAF'
        self._log.info("\nSteps of the TESTCASE_GBP_INTG_LEAF_7_DISCONN_LEAF_UPDATECFG_RECONN_LEAF to be executed\n")
        if self.test_step_SetUpConfig()!=1:
           self._log.info("Test Failed at Step_1 == SetUpConfig")
           self.test_CleanUp()
        if self.test_step_VerifyTraffic() != 1:
           self._log.info("Test Failed at Step_2 == TestVerifyTraffic")
           self.test_CleanUp()
        testcase_steps = [self.test_step_DisconnectLeaf,
                              self.test_step_UpdatePtg,
                              self.test_step_ReconnectLeaf,
                              self.test_step_VerifyTraffic
                         ]
        for prs,proto in self.prs_proto.iteritems():
            for step in testcase_steps:  ##TODO: Needs FIX
              try:
                if step == 'self.test_step_VerifyTraffic':
                   if step(proto) != 1:
                      self._log.info("Test Failed at Step == VerifyTraffic for Protocol = %s" %(proto))
                      raise TestFailed("%s_%s@_%s == FAILED" %(self.__class__.__name__.upper(),test_name,step.__name__.lstrip('self.')))
                   elif step()!=1:
                     self._log.info("Test Failed at Step == %s" %(step.__name__.lstrip('self')))
                     raise TestFailed("%s_%s@_%s == FAILED" %(self.__class__.__name__.upper(),test_name,step.__name__.lstrip('self.')))
              except TestFailed as err:
               print 'Noiro ==',err
               self.test_CleanUp()
        self._log.info("%s_%s == PASSED" %(self.__class__.__name__.upper(),test_name)) ## TODO: Needs FIX
        self.test_CleanUp()

    def test_step_SetUpConfig(self):
        """
        Test Step using Heat, setup the Test Config
        """
        self._log.info("\nSetupCfg: Create Aggregate & Availability Zone to be executed\n")
        self.agg_id = self.gbpnova.avail_zone('api','create',self.nova_agg,avail_zone_name=self.nova_az)
        if self.agg_id == 0:
            self._log.info("\n ABORTING THE TESTSUITE RUN,nova host aggregate creation Failed")
            sys.exit(1)
        self._log.info(" Agg %s" %(self.agg_id))
        if self.gbpnova.avail_zone('api','addhost',self.agg_id,hostname=self.az_comp_node) == 0:
            self._log.info("\n ABORTING THE TESTSUITE RUN, availability zone creation Failed")
            self.gbpnova.avail_zone('api','delete',self.nova_agg,avail_zone_name=self.nova_az) # Cleaning up
            sys.exit(1)
        sleep(3)
        if self.gbpheat.cfg_all_cli(1,self.heat_stack_name,heat_temp=self.heat_temp_test) == 0:
           self._log.info("\n ABORTING THE TESTSUITE RUN, HEAT STACK CREATE of %s Failed" %(self.heat_stack_name))
           self.test_CleanUp()
           sys.exit(1)
        return 1

    def test_step_UpdatePtg(self,prs):
        """
        Update the PTG with new PRS & Restart the Neutron-Server
        """
        self._log.info("\nStep to Update the PTG with new PRS & Restart the Neutron-Server\n")
        if self.gbpcfg.gbp_policy_cfg_all(2,'group',self.ptg_1,provided_policy_rule_sets="%s=scope" %(prs))\
           and self.gbpcfg.gbp_policy_cfg_all(2,'group',self.ptg_2,consumed_policy_rule_sets="%s=scope" %(prs))==0:
           self._log.info("Updating PTG = Failed")
           return 0
        return 1

    def test_step_DisconnectLeaf(self):
        """
        Test Step to Disconnect Leaf Port from two Comp-nodes
        """
        self._log.info("\nStep to Disconnect Leaf Port from two Comp-nodes\n")
        for port in [self.leaf_port1,self.leaf_port2]:
          if self.gbpaci.enable_disable_switch_port(self.apic_ip,self.node_id,'disable',port) == 0:
             return 0
        return 1

    def test_step_ReconnectLeaf(self):
        """
        Test Step to Reconnect Leaf Port to two Comp-nodes
        """
        self._log.info("\nStep to RE-connect Leaf Port to two Comp-nodes\n")
        for port in [self.leaf_port1,self.leaf_port2]:
          if self.gbpaci.enable_disable_switch_port(self.apic_ip,self.node_id,'enable',port) == 0:
           return 0
        return 1
  
    def test_step_VerifyTraffic(self):
        """
        Send and Verify traffic
        """
        self._log.info("\nSend and Verify traffic for Intra & Inter Host\n")
        return verify_traff(self.ntk_node)

    def test_CleanUp(self):
        """
        Cleanup the Testcase setup
        """
        self._log.info("\nCleanUp to be executed\n")
        for port in [self.leaf_port1,self.leaf_port2]:
          self.gbpaci.enable_disable_switch_port(self.apic_ip,self.node_id,'enable',port)
        self.gbpnova.avail_zone('api','removehost',self.agg_id,hostname=self.az_comp_node)
        self.gbpnova.avail_zone('api','delete',self.agg_id)
        self.gbpheat.cfg_all_cli(0,self.heat_stack_name)
        sys.exit(1)

