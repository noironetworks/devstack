#!/usr/bin/python

import sys
import logging
import os
import datetime
from scapy.all import *

class Gbp_def_traff(object):

    # Initialize logging
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=logging.WARNING)
    _log = logging.getLogger( __name__ )
    hdlr = logging.FileHandler('/tmp/test_def_traff.log')
    _log.setLevel(logging.INFO)
    _log.setLevel(logging.DEBUG)

    def __init__(self):
      """
      Verify all traffic b/w End-points using PTG with NO Contract(Policy RuleSet) 
      """
    
    def test_icmp_1(self):
        return 1   
    
    def test_tcp_2(self):
        return 1
    
    def test_udp_3(self):
        return 1 
    
    def test_icmp_udp_4(self):
        return 1
    
    def test_icmp_tcp_5(self):
        return 1
    
    def test_tcp_udp_6(self):
        return 1
    
    def test_run(self):
        """
        Run the traffic tests
        """
        self.test_icmp_1()
        self.test_tcp_2()
        self.test_udp_3()
        self.test_icmp_udp_4()
        self.test_icmp_tcp_5()
        self.test_tcp_udp_6()

