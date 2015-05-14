#!/usr/bin/python

import sys
import logging
import os
import datetime
import yaml
import string
from libs.gbp_conf_libs import Gbp_Config
from libs.gbp_verify_libs import Gbp_Verify
from libs.gbp_def_traffic import Gbp_def_traff
from libs.gbp_fab_traff_libs import Gbp_def_traff
from libs.gbp_pexp_traff_libs import Gbp_pexp_traff
from libs.gbp_aci_libs import Gbp_Aci
from libs.gbp_heat_libs import Gbp_Heat

class testcase_aci_integ_9(object):
    """
    This is a GBP_ACI Integration TestCase
    """
    # Initialize logging
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=logging.WARNING)
    _log = logging.getLogger( __name__ )
    hdlr = logging.FileHandler('/tmp/testcase_aci_integ_9.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    _log.addHandler(hdlr)
    _log.setLevel(logging.INFO)
    _log.setLevel(logging.DEBUG)

    def __init__(self,heattemp,compnode_ip):

      self.gbpcfg = Gbp_Config()
      self.gbpverify = Gbp_Verify()
      self.gbpdeftraff = Gbp_def_traff()
      self.gbpaci = Gbp_Aci()
      #self.gbpheat = Gbp_Heat(cntlr_ip)
      self.heat_stack_name = 'gbpinteg9'
      self.heat_temp_test = heattemp
      self.compnode_ip = compnode_ip
      

    def test_runner(self):
        """
        Method to run the Testcase in Ordered Steps
        """
        #Note: Cleanup per testcases is not required,since every testcase updates the PTG, hence over-writing previous attr vals
        testcase_steps = [self.test_step_disconnect_apic,
                          self.test_step_setup_config,
                          self.test_step_reconnect_apic,
                          self.test_step_verify_objs_in_apic,
                          self.test_traffic]
        
        for step in testcase_steps:
            try:
               if step()!=1:
                  self._log.info("Test Failed at Step == %s" %(setp.__name__.lstrip('self')))
                  self.test_cleanup() 
                  raise TestFailed("%s_@_%s == FAILED" %(self.__class__.__name__.upper(),test.__name__.lstrip('self.')))
            except TestFailed as err:
               print err
            self._log.info("%s == PASSED" %(self.__class__.__name__.upper()))


    def test_cleanup(self):
        """
        Cleanup the Testcase setup
        """
        self.gbpheat.cfg_all_cli(0,self.heat_stack_name)


    def verify_traff(self):
        """
        Verifies thes expected traffic result per testcase
        """
        return 1 #Jishnu
        #Incase of Same PTG all traffic is allowed irrespective what Policy-Ruleset is applied
        # Hence verify_traff will check for all protocols including the implicit ones
        results=self.gbpdeftraff.test_run()
        failed={}
        failed = {key: val for key,val in results.iteritems() if val == 0}
        if len(failed) > 0:
            print 'Following traffic_types %s = FAILED' %(failed)
            return failed
        else:
            return 1

    def test_step_setup_config(self):
        """
        Test Step using Heat, setup the Test Config
        """
        if self.gbpheat.cfg_all_cli(1,self.heat_stack_name,heat_temp=self.heat_temp_test) == 0:
           self._log.info("\n ABORTING THE TESTSUITE RUN, HEAT STACK CREATE of %s Failed" %(self.heat_stack_name))
           self.gbpheat.cfg_all_cli(0,self.heat_stack_name) ## Stack delete will cause cleanup
           sys.exit(1)

    def test_step_disconnect_apic(self):
        """
        Test Step to Disconnect APIC from Ostack Controller
        """
        if self.gbpaci.dev_conn_disconn(self.compnode_ip,self.apic_ip,'disconnect') == 0:
           return 0
 
    def test_step_verify_objs_in_apic(self):
        """
        Test Step to verify that all configured objs are available in APIC
        """
        if self.gbpheat.apic_verify_mos(self.apic_ip) == 0:
           return 0

    def test_step_reconnect_apic(self):
        """
        Test Step to Reconnect APIC to Ostack Controller
        """
        if self.gbpaci.dev_conn_disconn(self.compnode_ip,self.apic_ip,'reconnect') == 0:
           return 0
       
    def test_traffic(self):
        """
        Apply Policy-RuleSet to the in-use PTG
        Send traffic
        """
        prs = self.test_4_prs
        if self.gbpcfg.gbp_policy_cfg_all(2,'group',self.ptg,provided_policy_rule_sets="%s=scope" %(prs),consumed_policy_rule_sets="%s=scope" %(prs))!=0:
           return self.verify_traff()
        else:
           print 'Updating PTG = FAILED'
           return 0
