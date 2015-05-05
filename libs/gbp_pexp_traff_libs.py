#!/usr/bin/env python
import pexpect
import sys

class gbp_pexp_traff(object):
   
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

    def test_run(self,protocols=['icmp','tcp','udp']):
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
      for protocol in protocols:
        if protocol=='icmp':
           child.sendline('hping3 %s --icmp -c %s' %(self.dest_ep,self.pkt_cnt))
           child.expect('#')
           result=child.before         
           if self.parse_hping(result,self.pkt_cnt) !=0:
              return 1
           else:
              return 0

      
