#!/usr/bin/python

import sys
import logging
import os
import datetime
import string
import re
from libs.gbp_conf_libs import Gbp_Config
from libs.gbp_verify_libs import Gbp_Verify
from libs.gbp_nova_libs import Gbp_Nova
from libs.gbp_fab_traff_libs import Gbp_def_traff
from libs.gbp_pexp_traff_libs import Gbp_pexp_traff
from libs.raise_exceptions import *


gbpcfg = Gbp_Config()
gbpnova = Gbp_Nova('172.28.184.45')
ntk_node = '172.28.184.46'
vm_list = ['Web-Server','Web-Client-1','Web-Client-2','App-Server']
vm_to_ip_ns = {}
for vm in vm_list:
    vm_to_ip_list = gbpnova.get_any_vm_property(vm)['networks'][0]
    vm_to_ip_list = [ip.encode('ascii') for ip in vm_to_ip_list]
    src_vm_pvt_ip_subnet = re.search('(\d+.\d+.\d+).\d+',vm_to_ip_list[0].encode('ascii'),re.I).group(1)
    src_vm_dhcp_ns = gbpcfg.get_netns(ntk_node,src_vm_pvt_ip_subnet)
    vm_to_ip_ns[vm] = [vm_to_ip_list,src_vm_dhcp_ns]

print 'VM-to-IP-NS == %s' %(vm_to_ip_ns)

def verify_traff(results,target_vm_ip,proto):
    """
    Verifies the expected traffic result per testcase
    :: proto - 'all'/'icmp'/'tcp', all = both icmp & tcp
    """
    print 'Results from the Testcase == ', results
    failed ={}
    for key,val in results.iteritems():
            failed[key]={'icmp':'NA','tcp':'NA'}
            if proto == 'icmp' or proto == 'all':
               if val['icmp'] != 1:
                  failed[key]={'icmp': 'FAIL'}
               if val['tcp'] != 0:
                  failed[key]={'tcp':'FAIL'}
            if proto == 'tcp' or proto == 'all':
               if val['icmp'] != 0:
                  failed[key]={'icmp': 'FAIL'}
               if val['tcp'] != 1:
                  failed[key]={'tcp':'FAIL'}    
    if len(failed) > 1:
           for key in failed.keys():
               for k,v in target_vm_ip.iteritems(): #target_vm_ip is expected to be a dict
                   if key in v:
                      failed[k]=failed.pop(key) #Replacing the FIP by its VM Name
           #print failed
           return 0,failed
    else:
            return 1

def test_traff_from_vm_to_allvms(vm_name,proto='all'):
    """
    Test Full Mesh Traffic from bw VMs' FIPs
    """
    global vm_to_ip_ns
    global vm_list
    global ntk_node
    dest_vm_fips = {}
    dest_vms = vm_list
    dest_vms.remove(vm_name)

    for vm in dest_vms:
       dest_vm_fips[vm] = vm_to_ip_ns[vm][0][1:3]
    print dest_vm_fips
    flattended_dest_vm_fips = [fip for x in dest_vm_fips.values() for fip in x]
    print flattended_dest_vm_fips
    dhcp_ns_vm = vm_to_ip_ns[vm_name][1]
    vm_pvt_ip = vm_to_ip_ns[vm_name][0][0]
    gbppexptraff = Gbp_pexp_traff(ntk_node,dhcp_ns_vm,vm_pvt_ip,flattended_dest_vm_fips)
    results=gbppexptraff.test_run(protocols=['icmp','tcp'],tcp_syn_only=1) #Run for all protocols irrespective of the contract type
    #print 'RESULTS == \n', results
    return verify_traff(results,dest_vm_fips,proto)

def test_traff_anyvm_to_extgw(vm_name,extgw,proto=all):
    """
    Test Traffic from each VM to ExtGW
    """
    dhcp_ns_vm = vm_to_ip_ns[vm_name][1]
    vm_pvt_ip = vm_to_ip_ns[vm_name][0][0]
    gbppexptraff = Gbp_pexp_traff(ntk_node,dhcp_ns_vm,vm_pvt_ip,extgw)
    results=gbppexptraff.test_run(protocols=['icmp','tcp'],tcp_syn_only=1) #Run for all protocols irrespective of the contract type
    return verify_traff(results,extgw,proto)
