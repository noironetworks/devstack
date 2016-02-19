#!/usr/bin/env python

import datetime
import logging
import pexpect
import re
import sys
from fabric.api import cd,run,env, hide, get, settings

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
    
    def parse_hping(self,out,pkt_cnt,regular=''):
        cnt = pkt_cnt
        output = out
        if regular == '1': #In case of regular ping
           check = re.search('\\b%s\\b packets transmitted, \\b(\d+)\\b received' %(cnt),output,re.I)
        elif regular == 'nc': #In case of netcat
           if output.find('succeeded') > -1:
              return 1
        else:
            check = re.search('\\b%s\\b packets transmitted, \\b(\d+)\\b packets received' %(cnt),output,re.I)
        if check != None:
           if int(cnt) - int(check.group(1)) > 1:
              return 0
        
    def test_icmp(self,src_vm_ip,target_ip,user='noiro',pwd='noir0123',pkt_cnt=3):
        env.host_string = src_vm_ip
        env.user = user
        env.password = pwd
        with settings(warn_only=True):
          result = run("sudo hping3 %s --icmp -c %s --fast -q" %(target_ip,pkt_cnt))
          if result.return_code == 0:
             if self.parse_hping(result,pkt_cnt) != 0:
               return 1
             else:
               return 0
          else:
              print result
              return 0

    def test_tcp(self,src_vm_ip,target_ip,port,user='noiro',pwd='noir0123',pkt_cnt=3):
        env.host_string = src_vm_ip
        env.user = user
        env.password = pwd
        print "Sending TCP SYN,SYN ACK,SYN-ACK-FIN to %s" %(target_ip)
        cmd_s = "sudo hping3 %s -S -V -p %s -c %s --fast -q" %(target_ip,port,pkt_cnt)
        cmd_sa = "sudo hping3 %s -S -A -V -p %s -c %s --fast -q" %(target_ip,port,pkt_cnt)
        cmd_saf = "sudo hping3 %s -S -A -F -V -p %s -c %s --fast -q" %(target_ip,port,pkt_cnt)
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
    
    def test_udp(self,src_vm_ip,target_ip,port,user='noiro',pwd='noir0123',pkt_cnt=3):
        env.host_string = src_vm_ip
        env.user = user
        env.password = pwd
        print "Sending UDP to %s" %(target_ip)
        with settings(warn_only=True):
          result = run("sudo hping3 %s --udp -p %s -c %s --fast -q" %(target_ip,port,pkt_cnt))
          if result.return_code == 0:
             if self.parse_hping(result,pkt_cnt) != 0:
               return 1
             else:
               return 0
          else:
              print result
              return 0

    def test_arp(self,src_vm_ip,target_ip,user='noiro',pwd='noir0123'):
        env.host_string = src_vm_ip
        env.user = user
        env.password = pwd
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
    
    def test_dns(self,src_vm_ip):
        env.host_string = src_vm_ip
        env.user = user
        env.password = pwd
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

    def test_regular_icmp(self,src_vm_ip,target_ip,user='noiro',pwd='noir0123',pkt_cnt=3,pkt_size='1000'):
        env.host_string = src_vm_ip
        env.user = user
        env.password = pwd
        ret_results = {}
        with settings(warn_only=True):
         if not isinstance(target_ip,list):
             target_ip = [target_ip]
         for target in target_ip:
           result = run("ping %s -c %s -i 0.2 -W 1 -s %s" %(target,pkt_cnt,pkt_size))
           if result.return_code == 0:
             if self.parse_hping(result,pkt_cnt,regular=1) == 0:
                ret_results[target]=0
           else: 
             ret_results[target]=0
         if len(ret_results) > 0:
            return ret_results    
         else:
            return 1 

    def test_regular_tcp(self,src_vm_ip,target_ip,port=22,user='noiro',pwd='noir0123',pkt_cnt=3):
        env.host_string = src_vm_ip
        env.user = user
        env.password = pwd
        ret_results = {}
        with settings(warn_only=True):
          if not isinstance(target_ip,list):
             target_ip = [target_ip]
          for target in target_ip:
             result = run("nc -w 1 -v %s -z %s" %(target,port))
             if result.return_code == 0:
                 if self.parse_hping(result,pkt_cnt,regular='nc') == 0:
                    ret_results[target]=0
             else:
                    ret_results[target]=0
          if len(ret_results) > 0:
            return ret_results
          else:
            return 1

    def test_run(self,src_vm_ip,target_ip,protocols=['icmp','tcp','udp']):
        """
        Run the traffic tests
        """
        #By default run tests for implicit rules(arp,dhcp,dns) 
        #and for protocolc:icmp,tcp,udp
        results = {}
        results['arp']=self.test_arp(src_vm_ip,target_ip)
        results['dhcp']=self.test_dhcp(src_vm_ip,target_ip)
        results['dns']=self.test_dns(src_vm_ip) 
        for protocol in protocols:
         if protocol=='icmp':
            results['icmp']=self.test_icmp(src_vm_ip,target_ip)
         if protocol=='tcp':
            results['tcp']=self.test_tcp(src_vm_ip,target_ip)
         if protocol=='udp':
            results['udp']=self.test_udp(src_vm_ip,target_ip)
         if protocol =='uu':
            results['uu']=self.test_uu()
         if protocol == 'l3bcast':
            results['l3bcast']=self.test_l3bcast()
        return results

    def add_route_in_extrtr(self,
                            extrtrip,
                            route,
                            nexthop,
                            user='noiro',
                            pwd='noir0123',
                            action='add'):
      child = pexpect.spawn('ssh %s@%s' %(user,extrtrip))
      child.expect('password:')
      child.sendline(pwd)
      child.expect('\$')
      child.sendline('hostname')
      child.expect('$')
      print child.before
      child.sendline('sudo -s')
      child.expect('noiro:')
      child.sendline('noir0123')
      child.expect('#')
      child.sendline('ip route')
      child.expect('#')
      print child.before
      if action == 'add':
         child.sendline("ip route add %s via %s" %(route,nexthop))
         child.expect('#')
      if action == 'update':
         child.sendline("ip route del %s " %(route))
         child.expect('#')
         child.sendline("ip route add %s via %s" %(route,nexthop))
         child.expect('#')
      child.sendline('ip route')
      child.expect('#')
      print child.before

