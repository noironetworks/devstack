#!/usr/bin/env python
import pexpect
import sys
import re

class Gbp_pexp_traff(object):
   
    def __init__(self,net_node_ip,netns,src_vm_ip,dst_vm_ip):
      self.net_node = net_node_ip
      self.netns = netns
      self.src_ep = src_vm_ip
      self.dest_ep = dst_vm_ip
      self.pkt_cnt = 5

    def parse_hping(self,out,pkt_cnt):
        cnt = pkt_cnt
        output = out
        check = re.search('\\b%s\\b packets transmitted, \\b(\d+)\\b packets received' %(cnt),output,re.I)
        if check != None:
           if int(cnt) - int(check.group(1)) > 1:
              return 0

    def test_run(self,protocols=['icmp','tcp','udp'],port=443):
      child = pexpect.spawn('ssh root@%s' %(self.net_node))
      child.expect('#')
      child.sendline('ifconfig eth2')
      child.expect('#')
      print child.before
      child.sendline('ip netns exec %s ssh noiro@%s' %(self.netns,self.src_ep))
      child.expect('password:')
      child.sendline('noir0123')
      child.expect('\$')
      child.sendline('sudo -s')
      child.expect('noiro:')
      child.sendline('noir0123')
      child.expect('#')
      child.sendline('ifconfig eth0')
      child.expect('#')
      print child.before
      results = {}
      for protocol in protocols:
        if protocol=='icmp' or protocol=='all':
           child.sendline('hping3 %s --icmp -c %s' %(self.dest_ep,self.pkt_cnt))
           child.expect('#')
           print "Sent ICMP packets"
           result=child.before         
           print result
           if self.parse_hping(result,self.pkt_cnt) !=0:
              results['icmp']=1
           else:
              results['icmp']=0
        if protocol=='tcp'or protocol=='all':
           cmd_s = "sudo hping3 %s -S -p %s -c %s" %(self.dest_ep,port,self.pkt_cnt)
           cmd_sa = "sudo hping3 %s -S -A -p %s -c %s" %(self.dest_ep,port,self.pkt_cnt)
           cmd_saf = "sudo hping3 %s -S -A -F -p %s -c %s" %(self.dest_ep,port,self.pkt_cnt)
           for cmd in [cmd_s,cmd_sa,cmd_saf]:
               child.sendline(cmd)
               child.expect('#')
               print "Sent TCP SYN,SYN ACK,SYN-ACK-FIN to %s" %(self.dest_ep)
               result=child.before
               print result
               if self.parse_hping(result,self.pkt_cnt) !=0:
                  results['tcp']=1
               else:
                  results['tcp']=0
        if protocol=='udp' or protocol=='all':
           cmd = "hping3 %s --udp -p %s -c %s" %(self.dest_ep,port,self.pkt_cnt)
           child.sendline(cmd)
           child.expect('#')
           print 'Sent UDP packets'
           result=child.before
           print result
           if self.parse_hping(result,self.pkt_cnt) !=0:
              results['udp']=1
           else:
              results['udp']=0
      return results 
