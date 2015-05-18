#!/usr/bin/python

import sys
import logging
import os
import datetime
import string
from libs.gbp_conf_libs import Gbp_Config
from libs.gbp_verify_libs import Gbp_Verify
from libs.gbp_fab_traff_libs import Gbp_def_traff
from libs.gbp_pexp_traff_libs import Gbp_pexp_traff
from libs.raise_exceptions import *

def verify_traff(proto=['all']):
        """
        Verifies the expected traffic result per testcase
        """
        #Incase of Diff PTG Same L2 & L3P all traffic is dis-allowed by default unless Policy-Ruleset is applied
        # Hence verify_traff will check for all protocols including the implicit ones
        gbpcfg = Gbp_Config()
        vm4_ip = gbpcfg.get_vm_subnet('VM4')[0]
        vm4_subn = gbpcfg.get_vm_subnet('VM4')[1]
        dhcp_ns = gbpcfg.get_netns(self.ntk_node,vm4_subn)
        if self.vm_loc == 'diff_host_same_leaf':
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

