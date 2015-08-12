#!/usr/bin/env python

import sys
import os
import logging
import re
import datetime
from time import sleep
from commands import *
import keystoneclient.v2_0.client as ksclient
from novaclient import client as nvclient

# Initialize logging
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=logging.WARNING)
_log = logging.getLogger( __name__ )

_log.setLevel(logging.INFO)
_log.setLevel(logging.DEBUG)

class Gbp_Nova(object):

    key_name = "gbpkey"
    def __init__(self,ostack_controller, os_username='admin', os_password='noir0123', os_tenant='admin'):
        """ Creating a Nova CLient Instance using keystoneclient API """
        os_auth_url = "http://%s:5000/v2.0/" %(ostack_controller)
        keystone = ksclient.Client(
                                     auth_url = os_auth_url,
                                     username = os_username,
                                     password = os_password,
                                     tenant = os_tenant)
        ksconn = ksclient.Client(auth_url=os_auth_url, username=os_username,password=os_password,tenant=os_tenant)
        print ksconn.authenticate()
        os_token = ksconn.get_token(ksconn.session)
        print os_token
        raw_token = ksconn.get_raw_token_from_identity_service(auth_url=os_auth_url, username=os_username,password=os_password,tenant_name=os_tenant)
        os_tenant_id = raw_token['token']['tenant']['id']
        self.nova = nvclient.Client('2',auth_url=os_auth_url,username=os_username,auth_token=os_token,tenant_id=os_tenant_id)
        self.err_strings=['Unable','Conflict','Bad Request','Error', 'Unknown','Exception']


    def cmd_error_check(self,cmd_out):
        """
        Verifies whether executed cmd has any known error string
        """
        for err in self.err_strings:
            if re.search('\\b%s\\b' %(err), cmd_out, re.I):
               _log.info("Cmd execution failed! with this Return Error: \n%s" %(cmd_out))
               return 0

    def quota_update(self):
        """
        Updates the instances/cores/ram
        """
        cmd_inst = "sed -i 's/quota_instances.*/quota_instances=50/' /etc/nova/nova.conf"
        cmd_core = "sed -i 's/quota_cores.*/quota_cores=200/' /etc/nova/nova.conf"
        cmd_ram = "sed -i 's/quota_ram.*/quota_ram=655360000/' /etc/nova/nova.conf"
        for cmd in [cmd_inst,cmd_core,cmd_ram]:
           getoutput(cmd)
        for service in ['openstack-nova-api.service','openstack-nova-scheduler.service']:
            cmd_restart = 'systemctl restart %s' %(service)
            getoutput(cmd_restart)
            sleep(2)
            cmd_verify = 'systemctl status %s' %(service)
            out = getoutput(cmd_verify)
            if len(re.findall('Active: active \(running\)',out)) > 0:
               return 1
            else:
                _log.info('This service %s did not restart' %(service))
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

    def add_host_avail_zone(self,hostname,availzone_name):
        """
        Add host to avail_zone
        """
        ## keeping avail_zone_name same as agg_name
        agg_id = self.avail_zone('api','create',availzone_name,avail_zone_name=availzone_name)
        self.nova.aggregates.add_host(agg_id,hostname)
        
    def vm_create_api(self,vmname,vm_image,portid,flavor_name='m1.medium',avail_zone=''):
        """
        Call Nova API to create VM and check for ACTIVE status
        """
        vm_image = self.nova.images.find(name=vm_image)
        vm_flavor = self.nova.flavors.find(name=flavor_name)
        port_id = [{'port-id': '%s' %(portid)}]
        if avail_zone != '':
           instance = self.nova.servers.create(name=vmname, image=vm_image, flavor=vm_flavor, nics=port_id,availability_zone=avail_zone)
        else:
           instance = self.nova.servers.create(name=vmname, image=vm_image, flavor=vm_flavor, nics=port_id)
        print instance
        #Polling at 5 second intervals, until the status is ACTIVE
        vm_status = instance.status
        print vm_status
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

    #def vm_create_cli(self,vmname,vm_image,ports,sshkeyname,avail_zone=''): #Jishnu: change on 05/06
    def vm_create_cli(self,vmname,vm_image,ports,avail_zone=''):
        """
        Creates VM and checks for ACTIVE status
        """
        ## Create and Upload SSH keypair

        #keypath=gensshkey(sshkeyname) TODO
        #cmd = 'nova keypair-add --pub-key '+'%s ' %(keypath)+ sshkeyname
        #if self.cmd_error_check(getoutput(cmd)) == 0:
        #   return 0 #SSH Key upload failed
        # << Jishnu .. below changes as 05/06 >> #
        #self.sshkey_for_vm(sshkeyname)
        #cmd = 'nova boot --image '+vm_image+' --flavor m1.medium --key_name '+sshkeyname
        cmd = 'nova boot --image '+vm_image+' --flavor m1.medium'
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
               _log.info("Retrying every 5s .... to check if VM is ACTIVE state")
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

    def get_floating_ip(self,vm_name):
        """
        Returns the Floating IP associated for the vm_name
        """
        instance = self.nova.servers.find(name=vmname)
        try:
           floating_ip = self.nova.floating_ips.find(instance_id=instance.id).ip.encode('ascii')
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            _log.info('Exception Type = %s, Exception Object = %s' %(exc_type,exc_obj))
            return 0
        return floating_ip

    def get_any_vm_property(self,vm_name):
        """
        Returns any VM property
        Pass vm_name string & the property name string
        """
        instance = self.nova.servers.find(name=vmname)
        vm_dict = {}
        try:
           vm_dict['name'] = instance.name.encode('ascii')
           vm_dict['ip'] = instance.ip.encode('ascii')
           vm_dict['id'] = instance.id.encode('ascii')
           vm_dict['networks'] = instance.networks
           vm_dict['hostid'] = instance.hostId.encode('ascii')
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            _log.info('Exception Type = %s, Exception Object = %s' %(exc_type,exc_obj))
            return 0
        return vm_dict
 
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


        
