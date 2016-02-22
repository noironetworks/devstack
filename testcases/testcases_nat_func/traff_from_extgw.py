#!/usr/bin/python

import sys
import logging
import os
import datetime
import string
import re
from libs.gbp_fab_traff_libs import Gbp_def_traff
from libs.gbp_pexp_traff_libs import Gbp_pexp_traff
from libs.raise_exceptions import *


def traff_from_extgwrtr(extgwrtr_ip, fipsOftargetVMs, proto='all', jumbo=0):
    """
    Traffic from ExternalGW Router to Tenant VMs
    """
    traff = Gbp_def_traff()
    targetvm_list = ['TestVM1','TestVM2']
    print 'FIPs of Target VMs == %s' % (fipsOftargetVMs)
    # List of FIPs ExtGWRtr will ping:
    if isinstance(fipsOftargetVMs,dict):
       ping_fips = fipsOftargetVMs.values()
    if isinstance(fipsOftargetVMs,list):
       ping_fips = fipsOftargetVMs
    if proto == 'all':
        if jumbo == 1:
            results_icmp = traff.test_regular_icmp(
                extgwrtr_ip, ping_fips, pkt_size='9000')
        else:
            results_icmp = traff.test_regular_icmp(extgwrtr_ip, ping_fips)
        results_tcp = traff.test_regular_tcp(extgwrtr_ip, ping_fips)
        if results_icmp != 1 and results_tcp != 1:
            return {'ICMP': results_icmp.keys(), 'TCP': results_tcp.keys()}
        elif results_icmp != 1:
            return {'ICMP': results_icmp.keys()}
        elif results_tcp != 1:
            return {'TCP': results_tcp.keys()}
        else:
            return 1
    if proto == 'icmp':
        if jumbo == 1:
            results_icmp = traff.test_regular_icmp(
                extgwrtr_ip, ping_fips, pkt_size='9000')
        else:
            results_icmp = traff.test_regular_icmp(extgwrtr_ip, ping_fips)
        if isinstance(results_icmp, dict):
            return {'ICMP': results_icmp.keys()}
    if proto == 'tcp':
        results_tcp = traff.test_regular_tcp(extgwrtr_ip, ping_fips)
        if isinstance(results_tcp, dict):
            return {'TCP': results_tcp.keys()}
