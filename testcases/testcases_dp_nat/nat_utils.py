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
from libs.raise_exceptions import *


def traff_from_extgwrtr(extgwrtr_ip,fipsOftargetVMs,proto='all'):
    """
    Traffic from ExternalGW Router to Tenant VMs
    """
    traff = Gbp_def_traff()
    targetvm_list = ['Web-Server','Web-Client-1','Web-Client-2','App-Server']
    print 'FIPs of Target VMs == %s' %(fipsOftargetVMs)
    #List of FIPs ExtGWRtr will ping:
    ping_fips = [fip for x in fipsOftargetVMs.values() for fip in x]
    if proto == 'all':
       results_icmp = traff.test_regular_icmp(extgwrtr_ip,ping_fips)
       results_tcp = traff.test_regular_tcp(extgwrtr_ip,ping_fips)
       if results_icmp != 1 and results_tcp != 1:
          return {'ICMP':results_icmp.keys(),'TCP':results_tcp.keys()}
       elif results_icmp != 1:
          return {'ICMP':results_icmp.keys()}
       elif results_tcp != 1:
          return {'TCP':results_tcp.keys()}
       else:
          return 1
    if proto == 'icmp':
       results_icmp = traff.test_regular_icmp(extgwrtr_ip,ping_fips)
       if isinstance(results_icmp,dict):
          return results_icmp.keys()
    if proto == 'tcp':
       results_tcp = traff.test_regular_icmp(extgwrtr_ip,ping_fips)
       if isinstance(results_tcp,dict):
          return results_tcp.keys()

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
            vm_to_ip[vm] = gbpnova.get_any_vm_property(vm)['networks'][0]
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

