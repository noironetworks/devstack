#!/usr/bin/python

import sys
import logging
import os
import datetime
import string
import re
from libs.gbp_conf_libs import Gbp_Config
from libs.gbp_nova_libs import Gbp_Nova
from libs.gbp_fab_traff_libs import Gbp_def_traff
from libs.gbp_pexp_traff_libs import Gbp_pexp_traff
from libs.raise_exceptions import *


class NatTraffic(object):
    """
    NAT Traffic Base Class
    """

    def __init__(self, ostack_controller, vm_list, ntk_node):

        self.ntk_node = ntk_node
        gbpcfg = Gbp_Config()
        gbpnova = Gbp_Nova(ostack_controller)
        self.vm_list = vm_list
        print " List of VMs passed from the testsuite ", vm_list
        self.vm_to_ip_ns = {}
        for vm in self.vm_list:
            vm_to_ip_list = gbpnova.get_any_vm_property(vm)['networks'][0]
            vm_to_ip_list = [ip.encode('ascii') for ip in vm_to_ip_list]
            src_vm_pvt_ip_subnet = re.search(
                '(\d+.\d+.\d+).\d+', vm_to_ip_list[0].encode('ascii'), re.I).group(1)
            src_vm_dhcp_ns = gbpcfg.get_netns(
                self.ntk_node, src_vm_pvt_ip_subnet)
            self.vm_to_ip_ns[vm] = [vm_to_ip_list, src_vm_dhcp_ns]
        print 'VM-to-IP-NS == %s' % (self.vm_to_ip_ns)

    def verify_traff(self, results, target_vm_ip, proto):
        """
        Verifies the expected traffic result per testcase
        :: proto - 'all'/'icmp'/'tcp', all = both icmp & tcp
        """
        print 'Results from the Testcase == ', results
        failed = {}
        for key, val in results.iteritems():
            if proto == 'icmp':
                if val['icmp'] != 1:
                    failed[key] = {'icmp': 'FAIL'}
                if val['tcp'] != 0:
                    failed[key] = {'tcp': 'FAIL'}
            if proto == 'tcp':
                if val['icmp'] != 0:
                    failed[key] = {'icmp': 'FAIL'}
                if val['tcp'] != 1:
                    failed[key] = {'tcp': 'FAIL'}
            if proto == 'all':
                if val['icmp'] != 1:
                    failed[key] = {'icmp': 'FAIL'}
                if val['tcp'] != 1:
                    failed[key] = {'tcp': 'FAIL'}
        if len(failed) > 1:
            for key in failed.keys():
                for k, v in target_vm_ip.iteritems():  # target_vm_ip is expected to be a dict
                    if key in v:
                        # Replacing the FIP by its VM Name
                        failed[k] = failed.pop(key)
            print failed
            return 0, failed
        else:
            return 1

    def test_traff_from_vm_to_allvms(self, vm_name, proto='all'):
        """
        Test Full Mesh Traffic from bw VMs' FIPs
        """
        dest_vm_fips = {}
        dest_vms = self.vm_list
        print 'VM List before Remove', self.vm_list
        dest_vms.remove(vm_name)
        print 'VM List After Remove', self.vm_list
        for vm in dest_vms:
            dest_vm_fips[vm] = self.vm_to_ip_ns[vm][0][1:3]
        print dest_vm_fips
        flattended_dest_vm_fips = [
            fip for x in dest_vm_fips.values() for fip in x]
        print flattended_dest_vm_fips
        dhcp_ns_vm = self.vm_to_ip_ns[vm_name][1]
        vm_pvt_ip = self.vm_to_ip_ns[vm_name][0][0]
        gbppexptraff = Gbp_pexp_traff(
            self.ntk_node, dhcp_ns_vm, vm_pvt_ip, flattended_dest_vm_fips)
        # Run for all protocols irrespective of the contract type
        results = gbppexptraff.test_run(
            protocols=['icmp', 'tcp'], tcp_syn_only=1)
        # Restore the self.vm_list by appending the vm_name which was removed
        # earlier
        self.vm_list.append(vm_name)
        print 'VM List After Restoration', self.vm_list
        return self.verify_traff(results, dest_vm_fips, proto)

    def test_traff_anyvm_to_extgw(self, vm_name, extgw, proto=all):
        """
        Test Traffic from each VM to ExtGW
        """
        dhcp_ns_vm = self.vm_to_ip_ns[vm_name][1]
        vm_pvt_ip = self.vm_to_ip_ns[vm_name][0][0]
        gbppexptraff = Gbp_pexp_traff(
            self.ntk_node, dhcp_ns_vm, vm_pvt_ip, extgw)
        # Run for all protocols irrespective of the contract type
        results = gbppexptraff.test_run(
            protocols=['icmp', 'tcp'], tcp_syn_only=1)
        return self.verify_traff(results, extgw, proto)
