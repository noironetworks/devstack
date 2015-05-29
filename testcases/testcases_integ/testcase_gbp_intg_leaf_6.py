#!/usr/bin/python

import sys
import logging
import os
import datetime
import string
from time import sleep
from libs.gbp_conf_libs import Gbp_Config
from libs.raise_exceptions import *
from libs.gbp_aci_libs import Gbp_Aci
from libs.gbp_heat_libs import Gbp_Heat
from libs.gbp_nova_libs import Gbp_Nova
from test_utils import *


class testcase_gbp_intg_leaf_6(object):
    """
    This is a GBP_ACI Integration TestCase
    """
    # Initialize logging
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=logging.WARNING)
    _log = logging.getLogger( __name__ )
    hdlr = logging.FileHandler('/tmp/testcase_gbp_intg_leaf_6.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    _log.addHandler(hdlr)
    _log.setLevel(logging.INFO)
    _log.setLevel(logging.DEBUG)

    def __init__(self,heattemp,cntlr_ip,leaf_ip,apic_ip,ntk_node,nova_agg,nova_az,\
                                        az_comp_node,leaf_port1,leaf_port2,comp_nodes):
      self.gbpcfg = Gbp_Config()
      self.gbpaci = Gbp_Aci()
      self.heat_stack_name = 'gbpleaf6'
      self.heat_temp_test = heattemp
      self.gbpheat = Gbp_Heat(cntlr_ip)
      self.gbpnova = Gbp_Nova(cntlr_ip)      
      self.leaf_ip = leaf_ip
      self.apic_ip = apic_ip
      self.ntk_node = ntk_node
      self.nova_agg = nova_agg
      self.nova_az = nova_az
      self.az_comp_node = az_comp_node
      self.comp_nodes = comp_nodes

    def test_runner(self,log_string):
        """
        Method to execute the testcase in Ordered Steps
        """
        test_name = 'RESTART_OPFLEXAGNT'
        testcase_steps = [self.test_step_SetUpConfig,
                          self.test_step_VerifyTraffic,
                          self.test_step_RestartOpflexAgent,
                          self.test_step_VerifyTraffic]      
        for step in testcase_steps:  ##TODO: Needs FIX
            try:
               if step()!=1:
                  self._log.info("Test Failed at Step == %s" %(step.__name__.lstrip('self')))
                  raise TestFailed("%s_%s@_%s == FAILED" %(self.__class__.__name__.upper(),test_name,step.__name__.lstrip('self.')))
            except TestFailed as err:
               print 'Noiro ==',err
               self.test_CleanUp()
        self._log.info("%s_%s == PASSED" %(self.__class__.__name__.upper(),test_name))
        self.test_CleanUp()

    def test_step_SetUpConfig(self):
        """
        Test Step using Heat, setup the Test Config
        """
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

    def test_step_RestartOpflexAgent(self):
        """
        Test Step to Restart OpflexAgent on both comp-nodes
        """
        for node in self.comp_nodes:
          if self.gbpcfg.restart_service(node,'agent-ovs.service') == 0:
             return 0
        return 1

    def test_step_VerifyTraffic(self):
        """
        Send and Verify traffic
        """
        return verify_traff(self.ntk_node)

    def test_CleanUp(self):
        """
        Test Setup Cleanup
        """
        self.gbpnova.avail_zone('api','removehost',self.agg_id,hostname=self.az_comp_node)
        self.gbpnova.avail_zone('api','delete',self.agg_id)
        self.gbpheat.cfg_all_cli(0,self.heat_stack_name)
        sys.exit(1)

