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

def verify_traff(ntk_node,vm_loc='default',proto=['all']):
        """
        Verifies the expected traffic result per testcase
        """
        #Incase of Diff PTG Same L2 & L3P all traffic is dis-allowed by default unless Policy-Ruleset is applied
        # Hence verify_traff will check for all protocols including the implicit ones
        gbpcfg = Gbp_Config()
        vm4_ip = gbpcfg.get_vm_subnet('VM4')[0]
        vm4_subn = gbpcfg.get_vm_subnet('VM4')[1]
        dhcp_ns = gbpcfg.get_netns(ntk_node,vm4_subn)
        vm5_ip = gbpcfg.get_vm_subnet('VM5',ret='ip')
        vm6_ip = gbpcfg.get_vm_subnet('VM6',ret='ip')
        print "VM4_IP = %s, VM4_SUBN = %s, VM5_IP = %s, VM6_IP = %s, DHCP_NS = %s" %(vm4_ip,vm4_subn,vm5_ip,vm6_ip,dhcp_ns)
        if vm_loc == 'diff_host_same_leaf':
           gbppexptraff = Gbp_pexp_traff(ntk_node,dhcp_ns,vm4_ip,vm6_ip)
        if vm_loc == 'same_host':
           gbppexptraff = Gbp_pexp_traff(ntk_node,dhcp_ns,vm4_ip,vm5_ip)
        if vm_loc == 'default':
            samehosttrf = Gbp_pexp_traff(ntk_node,dhcp_ns,vm4_ip,vm5_ip)
            result_samehost = samehosttrf.test_run()
            diffhosttrf = Gbp_pexp_traff(ntk_node,dhcp_ns,vm4_ip,vm6_ip)
            result_diffhost = diffhosttrf.testrun()
            results = {'same_host': result_samehost,\
                       'diff_host_same_leaf': result_diffhost}
        if vm_loc != 'default':
           results=gbppexptraff.test_run()
        print 'Results from the Testcase == ', results
        failed={}
        if proto[0] == 'all' and vm_loc != 'default': 
           failed = {key: val for key,val in results.iteritems() if val == 0}
           if len(failed) > 0:
              print 'Following traffic_types %s = Failed' %(failed)
              return 0
           else:
              return 1
        if proto[0] == 'all' and vm_loc == 'default':
           _fail = 0
           for loc,trf_reslt in results.iteritems():
              failed = {key: val for key,val in trf_reslt.iteritems() if val == 0}
              if len(failed) > 0:
                 print 'Following traffic_types %s = Failed for %s' %(failed,loc.upper())
                 _fail += 1
           if _fail > 0: 
              return 0
           else:
               return 1

