#!/usr/bin/python

import sys
import logging
import os
import datetime
import re
from fabric.api import cd,run,env, hide, get, settings
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
    
    def parse_hping(self,out,pkt_cnt):
        cnt = pkt_cnt
        output = out
        check = re.search('\\b%s\\b packets transmitted, \\b(\d+)\\b packets received' %(cnt),output,re.I)
        if check != None:
           if cnt != int(check.group(1)):
              return 0
        
    def test_icmp(self,src_vm_ip,target_ip,user='noiro',pwd='noiro',pkt_cnt=3):
        env.host = src_vm_ip
        env.user = user
        env.pwd = pwd
        with settings(warn_only=True):
          result = run("sudo hping3 %s --icmp -c %s" %(target_ip,pkt_cnt))
          if result.return_code == 0:
             if self.parse_hping(result,pkt_cnt) != 0:
               return 1
             else:
               return 0
          else:
              print result
              return 0

    def test_tcp(self,src_vm_ip,target_ip,port,user='noiro',pwd='noiro',pkt_cnt=3):
        env.host = src_vm_ip
        env.user = user
        env.pwd = pwd
        print "Sending TCP SYN,SYN ACK,SYN-ACK-FIN to %s" %(target_ip)
        cmd_s = "sudo hping3 %s -S -p %s -c %s" %(target_ip,port,pkt_cnt)
        cmd_sa = "sudo hping3 %s -S -A -p %s -c %s" %(target_ip,port,pkt_cnt)
        cmd_saf = "sudo hping3 %s -S -A -F -p %s -c %s" %(target_ip,port,pkt_cnt)
        with settings(warn_only=True):
           for cmd in [cmd_s,cmd_sa,cmd_saf]:
              result = run(cmd)
              if result.return_code != 0:
                 print result
                 return 0
              else:
                 if self.parse_hping(result,pkt_cnt) == 0:
                    return 0
        return 1
    
    def test_udp(self,src_vm_ip,target_ip,port,user='noiro',pwd='noiro',pkt_cnt=3):
        env.host = src_vm_ip
        env.user = user
        env.pwd = pwd
        print "Sending UDP to %s" %(target_ip)
        with settings(warn_only=True):
          result = run("sudo hping3 %s --udp -p %s -c %s" %(target_ip,port,pkt_cnt))
          if result.return_code == 0:
             if self.parse_hping(result,pkt_cnt) != 0:
               return 1
             else:
               return 0
          else:
              print result
              return 0

    def test_arp(self,src_vm_ip,target_ip,user='noiro',pwd='noiro'):
        env.host = src_vm_ip
        env.user = user
        env.pwd = pwd
        cmd_del_arp = "arp -d %s" %(target_ip)
        cmd_ping = "ping %s -c 3" %(target_ip)
        cmd_get_arp = "arp -n %s" %(target_ip)
        for cmd in [cmd_del_arp,cmd_ping,cmd_get_arp]:
          if cmd == cmd_get_arp:
             result = run(cmd)
             if re.findall("no entry" %(result)) == -1:
                return 0
          run(cmd)
          return 1
    
    def test_dns(self):
        env.host = src_vm_ip
        env.user = user
        env.pwd = pwd
        with settings(warn_only=True):
           result = run("sudo nslookup google.com")
           if result.return_code != 0:
              return 0
        return 1

    def test_dhcp(self):
        return 1

    def test_uu(self):
        return 1
    
    def test_l3bcast(self):
        return 1
    
    def test_mcast(self):
        return 1

    def test_run(self,protocols=[]):
        """
        Run the traffic tests
        """
        results = {}
        results['arp']=self.test_arp()
        results['dhcp']=self.test_arp()
        results['dns']=self.test_dns() 
        for protocol in protocols:
         if protocol=='icmp':
            results['icmp']=self.test_icmp()
         if protocol=='tcp':
            results['tcp']=self.test_tcp()
         if protocol=='udp':
            results['udp']=self.test_udp()
         if protocol =='uu':
            results['uu']=self.test_uu()
         if protocol == 'l3bcast':
            results['l3bcast']=self.test_l3bcast()
        return results
