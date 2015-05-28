#!/usr/bin/env python
import sys
import logging
import os
import re
import datetime
import pexpect
from time import sleep
from commands import *
from fabric.api import cd,run,env, hide, get, settings, local, lcd
from raise_exceptions import *


# Initialize logging
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=logging.WARNING)
_log = logging.getLogger( __name__ )

_log.setLevel(logging.INFO)
_log.setLevel(logging.DEBUG)

class Gbp_Aci(object):

    def __init__( self ):
      """
      Init def 
      """
      self.err_strings=['Unable','Conflict','Bad Request','Error', 'Unknown','Exception']
      
    def cmd_error_check(self,cmd_output):
        """
        Verifies whether executed cmd has any known error string
        """
        for err in self.err_strings:
            if re.search('\\b%s\\b' %(err), cmd_out, re.I):
               _log.info(cmd_out)
               _log.info("Cmd execution failed! with this Return Error: \n%s" %(cmd_ver))
               return 0

    def exec_admin_cmd(self,ip,cmd='',passwd='noir0123'):
        env.host_string = ip
        env.user = "admin"
        env.password = passwd
        env.disable_known_hosts = True
        r = run(cmd)
        if r.failed:
            raise ErrorRemoteCommand("---ERROR---: Error running %s on %s as user admin, stderr %s" % (cmd, ip, r.stderr))
        return r

    def get_root_password(self,ip,passwd='noir0123'):
        token = self.exec_admin_cmd(ip,cmd="acidiag dbgtoken",passwd=passwd)
        with lcd('/root/gbpauto/libs'):
           password = local("./generate_token.sh %s" % token, capture=True)
        return password

    def exec_root_cmd(self,ip,cmd):
        env.host_string = ip
        env.password = self.get_root_password(ip)
        env.user = "root"
        env.disable_known_hosts = True
        out = run(cmd)
        if out.failed:
            raise ErrorRemoteCommand("---ERROR---: Error running %s on %s as user root, stderr %s" % (cmd,ip,out.stderr))
        return out

    def opflex_proxy_act(self,leaf_ip,act='restart'):
        """
        Function to 'restart', 'stop' & 'start' opflex_proxy
        leaf_ip = IP Address of a Leaf
        act = restart/stop/start
        """
        cmd_ps = 'ps aux | grep svc_ifc_opflexp'
        out = re.search('\\broot\\b\s+(\d+).*/isan/bin/svc_ifc_opflexp',self.exec_root_cmd(leaf_ip,cmd_ps),re.I)
        if out != None:
           pid = int(out.group(1))        
        if act == 'stop':
           cmd_stop = "kill -s SEGV %s" %(pid)
           for i in range(1,8):
               self.exec_root_cmd(leaf_ip,cmd_stop)
               sleep(5)
               out = re.search('\\broot\\b\s+(\d+).*/isan/bin/svc_ifc_opflexp',self.exec_root_cmd(leaf_ip,cmd_ps),re.I)
               if out == None:
                  break
        if act == 'start':
           cmd_start = 'vsh & test reparse 0xf'
           self.exec_root_cmd(leaf_ip,cmd_start)
           sleep(5)
           cmd_chk = 'vsh & show system internal sysmgr service name opflex_proxy'
           if len(re.findall('State: SRV_STATE_HANDSHAKED',self.exec_root_cmd(leaf_ip,cmd_chk))) > 1:
              return 1
        if act == 'restart':
           cmd = "kill -HUP %s" %(pid)
           out = self.exec_root_cmd(leaf_ip,cmd)
        if out.failed:
            raise ErrorRemoteCommand("---ERROR---: Error running %s on %s as user root, stderr %s" % (cmd,leaf_ip,out.stderr))
        return 1 

    def apic_verify_mos(self,apic_ip,objs,tenant='admin'):
        """
        Function to verify MOs in APIC
        """
        #TODO:Once actual implmentation is done , below code will be discarded
        if not isinstance(objs,list):
           objs = [objs]
        env.host_string = apic_ip
        env.user = 'admin'
        env.password = 'noir0123'
        output = run("ls -ltr /mit/uni/tn-%s" %(tenant))
        for obj in objs:
            regex = re.compile(r"\W%s\W" %(obj))
            if bool(regex.search(output)) == False:
                 return 0
        return 1

    def dev_conn_disconn(self,local_ip,rem_ip,action):
        """
        Function to connect/disconnect any device from the local device
        Primarily we are using for disconnecting APIC from Ostack Controller
        local_ip = the ip of the local device from which removte device will be disconn
        rem_ip = the ip of the remote device
        action = 'disconnect' or 'reconnect' are the valid strings
        """
        if action == 'disconnect':
           cmd = "ip route add %s/32 via 127.0.0.1" %(rem_ip)
        elif action == 'reconnect':
           cmd = "ip route del %s/32" %(rem_ip)
        else:
            print "Passing Invalid string for param 'action'"
            return 0
        if local(cmd).succeeded == True:
               return 1
        else:
               return 0

    def enable_disable_switch_port(self,apic_ip,switch_node_id,action,port):
        """
        Using APIC user can Admin DOWN/UP a Leaf/Spine Port
        switch_node_id :: NodeID of Leaf/Spine
        action:: 'enable' or 'disable'
        port:: Port of the Leaf/Spine
        """
        env.host_string = apic_ip
        env.user = 'admin'
        env.password = 'noir0123'
        if action == 'enable':
           cmd = 'switchport %s switch %s interface %s' %(action,switch_node_id,port)
        if action == 'disable':
           cmd = 'switchport %s switch %s interface %s' %(action,switch_node_id,port)
        output = run(cmd)
        print output
        return 1

    def reboot_aci(self,ip):
        """
        Reboot APIC/Leaf/Spine
        ip:: ip of the aci device to be rebooted
        """
        self.exec_admin_cmd(ip,'system-reboot')
        return 1
