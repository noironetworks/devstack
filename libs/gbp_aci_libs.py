#!/usr/bin/env python
import sys
import logging
import os
import re
import datetime
from commands import *
from fabric.api import cd,run,env, hide, get, settings
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

    def opflex_proxy_act(self,ip,act='restart'):
        """
        Function to 'restart', 'stop' & 'start' opflex_proxy
        ip = IP Address of a Leaf
        act = restart/stop/start
        """
        cmd = 'ps aux | grep opflex_proxy' #TODO: get exact process name
        out = re.search('\\broot\\b\s+(\d+).*',exec_root_cmd(ip,cmd),re.I)
        if out != None:
           pid = int(out.group(1))        
        if act == 'stop':
           #TODO
           cmd = "kill -9 %s" %(pid)
           out = exec_root_cmd(ip,cmd)
        if act == 'restart':
           cmd = "kill -HUP %s" %(pid)
           out = exec_root_cmd(ip,cmd)
        if out.failed:
            raise ErrorRemoteCommand("---ERROR---: Error running %s on %s as user root, stderr %s" % (cmd,ip,out.stderr))
        return 1 

    def apic_verify_mos(self):
        """
        Function to verify MOs in APIC
        """
        #TODO
        return 1

    def apic_conn_disconn(self,leaf_cimc_ip):
        """
        Function to connect/disconnect APIC from Ostack Cntlr
        """
        env.host_string = leaf_cimc_ip
        env.user = 'admin'
        env.password = 'password'
        run("scope sol")
        run("set enabled yes")
        run("commit")
        run("connect host")
        token = run("acidiag dbgtoken")
        password = local("./generate_token.sh %s" % token, capture=True)
        
        
