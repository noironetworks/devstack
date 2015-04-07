#!/usr/bin/env python

import sys
import os
import logging
import re
import datetime
from time import sleep
from commands import *
from keystoneclient.auth.identity import v2
from keystoneclient import session
from novaclient.v1_1 import client as nvclient
from libs.gbp_utils import gen_ssh_key as gensshkey

# Initialize logging
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=logging.WARNING)
_log = logging.getLogger( __name__ )

_log.setLevel(logging.INFO)
_log.setLevel(logging.DEBUG)

class Gbp_Nova(object):

    key_name = "gbpkey"
    def __init__(self,ostack_controller, username='admin', password='noir0123', tenant='admin'):
          cred = {}
          cred['username'] = username
          cred['api_key'] = password #api_key is the keyword in nova.v1
          cred['project_id'] = tenant
          cred['auth_url'] = "http://%s:5000/v2.0/" % ostack_controller
          self.nova = nvclient.Client(**cred)
          self.err_strings=['Unable','Conflict','Bad Request','Error', 'Unknown','Exception']


    def cmd_error_check(self,cmd_out):
        """
        Verifies whether executed cmd has any known error string
        """
        for err in self.err_strings:
            if re.search('\\b%s\\b' %(err), cmd_out, re.I):
               _log.info("Cmd execution failed! with this Return Error: \n%s" %(cmd_out))
               return 0

    def avail_zone(self,method,action,agg_name_id,avail_zone_name='',hostname=''):
        """
        Call Nova API/CLI to create avail-zone
        method='api' or 'cli' << strings to be passed
        action='create','addhost','removehost','delete' << strings to be passed
        For all action except 'create', 'agg_name_id' arg needs to be passed as an integer(id of the agg)
        """

        if action == 'create':
           if method == 'api':
              agg_str = str(self.nova.aggregates.create(agg_name_id,avail_zone_name)) # By default create() returns a class,to get id converting to str() for regex
              t = re.search('<Aggregate: (\d+)>',agg_str,re.I)
              if t != None:
                 agg_id = t.group(1)
                 return agg_id
           if method == 'cli':
              cmd='nova aggregate-create '+agg_name_id+' '+avail_zone_name
              cmd_out = getoutput(cmd_out)
              if self.cmd_error_check(cmd_out) == 0:
                 return 0
              t = re.search('\\b(\d+)\\b.*\\b%s\\b.*' %(agg-name),cmd_out,re.I)
              if t != None:
                 agg_id = t.group(1)
                 return agg_id
        if action == 'delete':
           if method == 'api':
              self.nova.aggregates.delete(agg_name_id)
              return 1
           if method == 'cli':
              cmd='nova aggregate-delete '+agg_name_id
              cmd_out = getoutput(cmd)
              if self.cmd_error_check(cmd_out) == 0:
                 return 0
              return 1
        if action == 'addhost':
           if method == 'api':
              self.nova.aggregates.add_host(agg_name_id,hostname)
              return 1
           if method == 'cli':
              cmd='nova aggregate-add-host '+agg_name_id+' %s' %(hostname)
              cmd_out = getoutput(cmd_out)
              if self.cmd_error_check(cmd_out) == 0:
                 return 0
              return 1
        if action == 'removehost':
           if method == 'api':
              self.nova.aggregates.remove_host(agg_name_id,hostname)
              return 1
           if method == 'cli':
              cmd='nova aggregate-remove-host '+agg_name_id+' %s' %(hostname)
              cmd_out = getoutput(cmd)
              if self.cmd_error_check(cmd_out) == 0:
                 return 0
              return 1


    def vm_create_api(self,vmname,vm_image,portid_netid,sshkeyname,flavor_name='m1.medium',avail_zone=''):
        """
        Call Nova API to create VM and check for ACTIVE status
        portid_netid = MUST be passed as a dictionary comprising keys: port-id & net-id, for each nic. Eg:
                       [{'port-id':'33f4f198-24ef-4f6e-b40c-93e952e17155','net-id': 'd436c32c-4973-4031-862d-723a65109ae1'},
                        {'port-id':'50336f51-0a3c-4730-80ed-800493225eaa','net-id':'77144ab1-4ff2-4b9c-b809-c70fba4415c9'}]
        """
        ## Create and Upload ssh keypair
        keypath=gensshkey(sshkeyname)
        if not self.nova.keypairs.findall(name=sshkeyname):
           with open(os.path.expanduser(keypath)) as publickey:
             self.nova.keypairs.create(name=sshkeyname, public_key=publickey.read())
        vm_image = self.nova.images.find(name=vm_image)
        vm_flavor = self.nova.flavors.find(name=flavor_name)
        if avail_zone != '':
           instance = self.nova.servers.create(name=vmname, image=vm_image, flavor=vm_flavor, key_name=sshkeyname, nics=ports,availability_zone=avail_zone)
        else:
           instance = self.nova.servers.create(name=vmname, image=vm_image, flavor=vm_flavor, key_name=sshkeyname, nics=ports)
        # Polling at 5 second intervals, until the status is 'ACTIVE'
        vm_status = instance.status
        status_try=1
        while vm_status != 'ACTIVE':
          if status_try < 11:
             sleep(5)
             # Retrieve the instance again so the status field updates
             instance = self.nova.servers.get(instance.id)
             vm_status = instance.status
          else:
              _log.info("\nAfter waiting for 50 seconds, VM status is NOT ACTIVE")
              return 0
          status_try +=1
        return 1


    def vm_create_cli(self,vmname,vm_image,ports,sshkeyname,avail_zone=''):
        """
        Creates VM and checks for ACTIVE status
        """
        ## Create and Upload SSH keypair

        #keypath=gensshkey(sshkeyname) TODO
        #cmd = 'nova keypair-add --pub-key '+'%s ' %(keypath)+ sshkeyname
        #if self.cmd_error_check(getoutput(cmd)) == 0:
        #   return 0 #SSH Key upload failed
        self.sshkey_for_vm(sshkeyname)
        cmd = 'nova boot --image '+vm_image+' --flavor m1.medium --key_name '+sshkeyname
        if isinstance(ports,str):
           ports = [ports]
        for port in ports:
              cmd = cmd +' --nic port-id='+str(port)
        if avail_zone != '':
           cmd = cmd + ' --availability-zone '+avail_zone+' %s' %(vmname)
        else:
           cmd = cmd + ' %s' %(vmname)
        print '\nvmcreate cmd ==', cmd
        out = getoutput(cmd)
        print '\nvmcreate out ==', out
        if self.cmd_error_check(out) == 0:
           return 0
        sleep(5)
        cmd = 'nova show '+vmname
        out = getoutput(cmd)
        status_try = 1
        while True:
            if re.findall('ACTIVE',out) != []:
               break
            else:
               sleep(5)
               out = getoutput(cmd)
               if status_try > 10:
                  _log.info("After waiting for 50 seconds, VM status is NOT ACTIVE")
                  return 0
            status_try +=1
        return 1

    def vm_delete(self,vmname,method='cli'):
        """
        Delete Instance 
        """
        if method=='api':
           instance = self.nova.servers.find(name=vmname)
           instance.delete()
        else:
           cmd = 'nova delete '+vmname
           out = getoutput(cmd)
        status_try = 1
        cmd = 'nova show '+vmname
        out = getoutput(cmd)
        while True:
            if self.cmd_error_check(out) == 0:
               break
            else:
               sleep(5)
               out = getoutput(cmd)
               if status_try > 10:
                  _log.info("After waiting for 50 seconds, VM still NOT Deleted")
                  return 0
            status_try +=1
        return 1


    def sshkey_for_vm(self,sshkeyname,method='cli',action='create'):
        """
        Creates and Upload SSH key for VM
        """
        if action=='create':
         if method != 'cli':
           keypath=gensshkey(sshkeyname)
           if not self.nova.keypairs.findall(name=sshkeyname):
              with open(os.path.expanduser(keypath)) as publickey:
                 try:
                    self.nova.keypairs.create(name=sshkeyname, public_key=publickey.read())
                 except Exception as e:
                     return 0 #SSH Key upload failed
         else:
           #keypath=gensshkey(sshkeyname)
           cmd = 'nova keypair-add '+sshkeyname+' > %s.pem' %(sshkeyname)
           if self.cmd_error_check(getoutput(cmd)) == 0:
              return 0 ##nova generate keypair failed
           cmd = 'chmod 600 %s.pem' %(sshkeyname)
           getoutput(cmd)
        else: #delete
           cmd = 'nova keypair-delete '+sshkeyname
           getoutput(cmd)
        return 1


        
