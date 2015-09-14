#!/usr/bin/python

import sys
import logging
import os
import datetime
import string
from libs.gbp_conf_libs import Gbp_Config
from libs.gbp_verify_libs import Gbp_Verify
from libs.gbp_nova_libs import Gbp_Nova
from libs.gbp_fab_traff_libs import Gbp_def_traff
from libs.gbp_pexp_traff_libs import Gbp_pexp_traff
from libs.gbp_crud_libs import GBPCrud
from libs.raise_exceptions import *
from testsuites_setup_cleanup import super_hdr

class test_diff_ptg_same_l2p_l3p(object):
    """
    This is a TestCase Class comprising
    all Datapath testcases for the Test Header:   
    diff_ptg_same_l2p_l3p
    Every new testcases should be added as a new method in this class
    and call the testcase method inside the 'test_runner' method
    """
    # Initialize logging
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=logging.WARNING)
    _log = logging.getLogger( __name__ )
    hdlr = logging.FileHandler('/tmp/testsuite_same_ptg_l2p_l3p.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    _log.addHandler(hdlr)
    _log.setLevel(logging.INFO)
    _log.setLevel(logging.DEBUG)

    def __init__(self,objs_uuid):

      self.ostack_controller = '172.28.184.45'
      self.gbpcfg = Gbp_Config()
      self.gbpverify = Gbp_Verify()
      self.gbpdeftraff = Gbp_def_traff()
      self.gbpnova = Gbp_Nova(self.ostack_controller)
      self.gbp_crud = GBPCrud(self.ostack_controller)
      stack_name = super_hdr.stack_name
      heat_temp = super_hdr.heat_temp
      self.ntk_node = super_hdr.ntk_node 
      self.ptg_1 = objs_uuid['demo_diff_ptg_same_l2p_l3p_ptg1_id']
      self.ptg_2 = objs_uuid['demo_diff_ptg_same_l2p_l3p_ptg2_id']
      self.test_2_prs = objs_uuid['demo_ruleset_norule_id'] 
      self.test_3_prs = objs_uuid['demo_ruleset_icmp_id']
      self.test_4_prs = objs_uuid['demo_ruleset_tcp_id']
      self.test_5_prs = objs_uuid['demo_ruleset_udp_id']
      self.test_6_prs = objs_uuid['demo_ruleset_icmp_tcp_id']
      self.test_7_prs = objs_uuid['demo_ruleset_icmp_udp_id']
      self.test_8_prs = objs_uuid['demo_ruleset_tcp_udp_id']
      self.test_9_prs = objs_uuid['demo_ruleset_all_id']


    def test_runner(self,log_string,location):
        """
        Method to run all testcases
        """
        #Note: Cleanup per testcases is not required,since every testcase updates the PTG, hence over-writing previous attr vals
        self.vm_loc = location
        test_list = [self.test_1_traff_with_no_prs,
                    self.test_2_traff_app_prs_no_rule,
                    self.test_3_traff_apply_prs_icmp,
                    self.test_4_traff_apply_prs_tcp,
                    self.test_5_traff_apply_prs_udp,
                    self.test_6_traff_apply_prs_icmp_tcp,
                    self.test_7_traff_apply_prs_icmp_udp,
                    self.test_8_traff_apply_prs_tcp_udp,
                    self.test_9_traff_apply_prs_all_proto,
                    self.test_10_traff_rem_prs
                    ]
                 
        for test in test_list:
            try:
               if test()!=1:
                  raise TestFailed("%s_%s_%s == FAILED" %(self.__class__.__name__.upper(),log_string.upper(),string.upper(test.__name__.lstrip('self.'))))
               else:
                  if 'test_1' in test.__name__ or 'test_2' in test.__name__:
                     self._log.info("%s_%s_%s 10 subtestcases == PASSED" %(self.__class__.__name__.upper(),log_string.upper(),string.upper(test.__name__.lstrip('self.'))))
                  else:
                     self._log.info("%s_%s_%s == PASSED" %(self.__class__.__name__.upper(),log_string.upper(),string.upper(test.__name__.lstrip('self.'))))
            except TestFailed as err:
               print err


    def verify_traff(self,proto=['all']):
        """
        Verifies the expected traffic result per testcase
        """
        #Incase of Diff PTG Same L2 & L3P all traffic is dis-allowed by default unless Policy-Ruleset is applied
        # Hence verify_traff will check for all protocols including the implicit ones
        gbpcfg = Gbp_Config()
        vm_list = ['Web-Server','Web-Client-1','Web-Client-2','App-Server']
        vm_to_ip = {}
        for vm in vm_list:
            vm_to_ip[vm] = self.gbpnova.get_any_vm_property(vm)['networks'][0]
        print 'VM-to-IP == %s' %(vm_to_ip)
        src_vm_pvt_ip_subnet = re.search('(\d+.\d+.\d+).\d+',vm_to_ip['Web-Server'][0].encode('ascii'),re.I).group(1)
        print 'Subnet == %s' %(src_vm_pvt_ip_subnet)
        src_vm_dhcp_ns = gbpcfg.get_netns(self.ntk_node,src_vm_pvt_ip_subnet)
        print 'DHCP NtkNameSpace for Source VM == %s' %(src_vm_dhcp_ns) #Source VM = 'Web-Server'
        ### TBD : JISHNU BELOW THIS
        if self.vm_loc == 'diff_host_same_leaf' or self.vm_loc == 'diff_host_diff_leaf': 
           vm6_ip = gbpcfg.get_vm_subnet('VM6',ret='ip')
           print vm4_ip, vm4_subn, vm6_ip, dhcp_ns
           gbppexptraff = Gbp_pexp_traff(self.ntk_node,dhcp_ns,vm4_ip,vm6_ip)
        if self.vm_loc == 'same_host':
           vm5_ip = gbpcfg.get_vm_subnet('VM5',ret='ip')
           print vm4_ip, vm4_subn, vm5_ip, dhcp_ns
           gbppexptraff = Gbp_pexp_traff(self.ntk_node,dhcp_ns,vm4_ip,vm5_ip)
        results=gbppexptraff.test_run()
        print 'Results from the Testcase == ', results
        failed={}
        if proto[0] == 'all': # In 'all' proto is verified for PTGs with NO_PRS, PRS_NO_RULE, REM_PRS, hence below val ==1, then Fail, because pkts were not dropped
           failed = {key: val for key,val in results.iteritems() if val == 1} 
           if len(failed) > 0:
              print 'Following traffic_types %s = Failed' %(failed)
              return 0
           else:
              return 1
        else:
            implicit_allow = ['arp','dhcp','dns']
            allow_list = implicit_allow + proto
            failed = {key: val for key,val in results.iteritems() if val == 0 and key in allow_list}
            failed.update({key: val for key,val in results.iteritems() if val == 1 and key not in allow_list})
            if len(failed) > 0:
               print 'Following traffic_types %s = Failed' %(failed)
               return 0
            else:
               return 1

class DNAT_ExtGw_to_VMs(object):
    
    def __init__(self):
        """
        Traffic Test Class between ExternalGWRtr and Tenant VM
        VMs/Endpoints behind Border and Non-Border Leaf
        In this class we send Traffic b/w ExtGWRtr and end-points Web-Server(compnode-1)
        And App-Server(compnode-2)
        """
        ## TBD JISHNU: WHAT all variables/classes to be instialized

    def test_1_traff_with_no_prs(self):
        """
        Run traff test with NO CONTRACT between External PTG & Tenant PTG
        """
        self._log.info("\nTestcase_DNAT_EXTGWRTR_TO_TENANT_VMs: NO CONTRACT APPLIED and VERIFY TRAFFIC\n")
        return self.verify_traff() <<< ### TBD JISHNU

    def test_2_traff_app_prs_no_rule(self):
        """
        Update the in-use PTG with a PRS which has NO-Rule
        Send traff
        """
        self._log.info("\nTestcase_DNAT_EXTGWRTR_TO_TENANT_VMs: APPLY CONTRACT BUT NO RULE and VERIFY TRAFFIC\n")
        prs = ## TBD: JISHNU .. also ensure to intialize self.external_ptg & self.self.websrvr_ptg
        if self.gbp_crud.update_gbp_policy_target_group(self.external_ptg,consumed_policy_rulesets=prs)\
           and self.gbp_crud.update_gbp_policy_target_group(self.self.websrvr_ptg,provided_policy_rulesets=prs) !=0:
           return self.verify_traff()
        else:
           print 'Updating PTG = Failed'
           return 0
 
    def test_3_traff_apply_prs_icmp(self):
        """
        Apply Policy-RuleSet to the in-use PTG
        Send traffic
        """
        self._log.info("\nTestcase_DIFF_PTG_SAME_L2P_L3P: APPLY ICMP CONTRACT and VERIFY TRAFFIC\n")
        prs = ## TBD: JISHNU
        if self.gbp_crud.update_gbp_policy_target_group(self.external_ptg,consumed_policy_rulesets=prs)\
           and self.gbp_crud.update_gbp_policy_target_group(self.self.websrvr_ptg,provided_policy_rulesets=prs) !=0:
           return self.verify_traff(proto=['icmp'])
        else:
           print 'Updating PTG == Failed'
           return 0

    def test_4_traff_apply_prs_tcp(self):
        """
        Apply Policy-RuleSet to the in-use PTG
        Send traffic
        """
        self._log.info("\nTestcase_DIFF_PTG_SAME_L2P_L3P: APPLY TCP CONTRACT and VERIFY TRAFFIC\n")
        prs = ## TBD: JISHNU
        if self.gbp_crud.update_gbp_policy_target_group(self.external_ptg,consumed_policy_rulesets=prs)\
           and self.gbp_crud.update_gbp_policy_target_group(self.self.websrvr_ptg,provided_policy_rulesets=prs) !=0:
           return self.verify_traff(proto=['tcp'])
        else:
           print 'Updating PTG = Failed'
           return 0

    def test_6_traff_apply_prs_icmp_tcp(self):
        """
        Apply Policy-RuleSet to the in-use PTG
        Send traffic
        """
        self._log.info("\nTestcase_DIFF_PTG_SAME_L2P_L3P: APPLY ICMP-TCP-COMBO CONTRACT and VERIFY TRAFFIC\n")
        prs = ## TBD: JISHNU
        if self.gbp_crud.update_gbp_policy_target_group(self.external_ptg,consumed_policy_rulesets=prs)\
           and self.gbp_crud.update_gbp_policy_target_group(self.self.websrvr_ptg,provided_policy_rulesets=prs) !=0:
           return self.verify_traff(proto=['icmp','tcp'])
        else:
           return 0

    def test_10_traff_rem_prs(self):
        """
        Remove the PRS/Contract from the PTG
        Test all traffic types
        """
        self._log.info("\nTestcase_DIFF_PTG_SAME_L2P_L3P: REMOVING CONTRACT and VERIFY TRAFFIC\n")
        if self.gbp_crud.update_gbp_policy_target_group(self.external_ptg)\
           and self.gbp_crud.update_gbp_policy_target_group(self.self.websrvr_ptg) !=0:
           return self.verify_traff()
        else:
           return 0
