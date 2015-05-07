#!/usr/bin/env python

import os
import sys
import logging
import re
import datetime
import yaml
from time import sleep
from keystoneclient import client as ksclient
from keystoneclient.auth.identity import v2
from keystoneclient import session
from heatclient.client import Client
from commands import *

# Initialize logging
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=logging.WARNING)
_log = logging.getLogger( __name__ )

_log.setLevel(logging.INFO)
_log.setLevel(logging.DEBUG)

class Gbp_Heat(object):

    def __init__(self, controller, username='admin', password='noir0123', tenant='admin'):
        kc = ksclient.Client(username=username, password=password, tenant_name=tenant, auth_url='http://%s:5000/v2.0' %(controller))
        auth = v2.Password(auth_url='http://%s:5000/v2.0/' % controller, username=username,
                password=password, tenant_name=tenant)
        sess = session.Session(auth=auth)
        auth_token = auth.get_token(sess)
        #tenant_id =kc.tenant_id(tenant) #TODO
        tenant_id = '23523b6f27454cf0959d4e6f89abae5a'
        heat_url = "http://%s:8004/v1/%s" % (controller,tenant_id)
        self.hc = Client('1',endpoint=heat_url,auth_token=auth_token)
        self.err_strings=['Unable','Conflict','Bad Request','Error', 'Unknown','Exception']

    def cfg_all_api(self,val,heat_temp,name):
        """
        Heat Python API to create/delete stacks
        """
        
    def cmd_error_check(self,cmd_out):
        """
        Verifies whether executed cmd has any known error string
        """
        for err in self.err_strings:
            if re.search('\\b%s\\b' %(err), cmd_out, re.I):
               _log.info("Cmd execution failed! with this Return Error: \n%s" %(cmd_out))
               return 0


    def cfg_all_cli(self,val,name,heat_temp=''):
        """
        Function to create/delete a pre-defined Heat Template
        -parma val : 0 for delete, 1 for create
        """
        cmd_ver = "heat stack-show %s" %(name)
        if val ==1: ## Create & Verify Stack
           cmd_cfg = "heat stack-create -f %s " %(heat_temp)+ name
           cfg_out = getoutput(cmd_cfg)
           if self.cmd_error_check(cfg_out) == 0:
               return 0
           _log.info("Sleeping for 10 secs ... to check if stack create completed")
           sleep(10)
           num_try = 1
           cmd_out = getoutput(cmd_ver)
           if self.cmd_error_check(cmd_out) == 0:
               return 0
           while num_try > 0:
              if cmd_out.find('CREATE_COMPLETE') != -1:
                 return 1
              else:
                 _log.info("Keep Retrying every 5s to check if heat stack-create completed")
                 sleep(5)
                 cmd_out = getoutput(cmd_ver)
              if num_try > 100:
                 _log.info(" After 100 re-tries, the stack create has NOT COMPLETED")
                 return 0
              num_try +=1
        if val == 0:
           cmd_cfg = "heat stack-delete %s" %(name)
           cfg_out = getoutput(cmd_cfg)
           if self.cmd_error_check(cfg_out) == 0:
               return 0
           _log.info("Sleeping for 10 secs ... to check if stack got deleted")
           sleep(10)
           cmd_out = getoutput(cmd_ver)
           if self.cmd_error_check(cmd_out) == 0:
               return 0
           if cmd_out.find('not found') != -1:
              return 1
           else:
              return 0


    def get_output_cli(self,stack_id_name,template_file):
        """
        Get the UUID of the created objects defined heat temp's Output Section
        - stack_id_name : Pass stack name or UUID
        """
        in_file = template_file
        f = open(in_file,'rt')
        heat_conf = yaml.load(f)
        _outputs = heat_conf["outputs"]
        objs_uuid = {}
        for key in _outputs.iterkeys():
            cmd = 'heat output-show %s %s' %(stack_id_name,key)
            cmd_out = getoutput(cmd)
            #print cmd_out
            if self.cmd_error_check(cmd_out) == 0:
               return 0
            objs_uuid[key] = cmd_out
        return objs_uuid

