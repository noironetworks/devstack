#!/usr/bin/python
# This has NO USE of subprocess module
import sys
from time import sleep
import subprocess
import logging
import os
import string
import shutil
import re
import datetime
from commands import *

# Initialize logging
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=logging.WARNING)
_log = logging.getLogger( __name__ )

_log.setLevel(logging.INFO)
_log.setLevel(logging.DEBUG)

class Gbp_Config(object):

    def __init__( self ):
      """
      Init def 
      """
      self.err_strings=['Unable','Conflict','Bad Request','Error', 'Unknown','Exception','Invalid','read-only','not supported','prefix greater than subnet mask']	
    def exe_command(self,command_args):
      """
      Execute system calls
      """
      proc = subprocess.Popen(command_args, shell=False,stdout=subprocess.PIPE)
      #proc.communicate()
      return proc.stdout.read()

    def gbp_uuid_get(self,cmd_out):
        '''
        Extracts UUID of a gbp object
        '''
        match=re.search("\\bid\\b\s+\| (.*) \|",cmd_out,re.I)
        if match != None:
           obj_uuid = match.group(1)
           #_log.info( "UUID:\n%s " %(obj_uuid))
           return obj_uuid.rstrip()
        else:
            return 0

    def gbp_action_config(self,cmd_val,name_uuid,**kwargs):
	"""
        -- cmd_val== 0:delete; 1:create; 2:update
	-- name_uuid == UUID or name_string
        Create/Update/Delete Policy Action
        Returns assigned UUID on Create
        kwargs addresses the need for passing required/optional params
        """
        if cmd_val == '' or name_uuid == '':
           _log.info('''Function Usage: gbp_action_config 0 "abc"\n
                      --cmd_val == 0:delete; 1:create; 2:update\n
                       -- name_uuid == UUID or name_string\n''')
           return 0
        #Build the command with mandatory param 'name_uuid' 
        if cmd_val == 0:
           cmd = 'gbp policy-action-delete '+str(name_uuid)
        if cmd_val == 1:
           cmd = 'gbp policy-action-create '+str(name_uuid)
        if cmd_val == 2:
           cmd = 'gbp policy-action-update '+str(name_uuid)
        # Build the cmd string for optional/non-default args/values
        for arg, value in kwargs.items():
          cmd = cmd + " --" + "".join( '%s %s' %(arg, value ))
        _log.info(cmd)
        # Execute the policy-action-config-cmd
        cmd_out = getoutput(cmd)
        _log.info(cmd_out)
        # Catch for non-exception error strings, even though try clause succeded
        for err in self.err_strings:
	    if re.search(r'\b%s\b' %(err), cmd_out, re.I):
               _log.info(cmd_out)
	       _log.info( "Cmd execution failed! with this Return Error: \n%s" %(cmd_out))
	       return 0
        # If "create" cmd succeeded then parse the cmd_out to extract the UUID
        if cmd_val==1:
           action_uuid = self.gbp_uuid_get(cmd_out)
           return action_uuid

    def gbp_classif_config(self,cmd_val,classifier_name,**kwargs):
        """
        -- cmd_val== 0:delete; 1:create; 2:update
        -- classifier_name == UUID or name_string
        Create/Update/Delete Policy Classifier
        Returns assigned UUID on Create
        kwargs addresses the need for passing required/optional params
        """
        if cmd_val == '' or classifier_name == '':
           _log.info('''Function Usage: gbp_classifier_config 0 "abc"\n
                      --cmd_val == 0:delete; 1:create; 2:update\n
                      -- classifier_name == UUID or name_string\n''')
           return 0
        #Build the command with mandatory param 'classifier_name'
        if cmd_val == 0:
           cmd = 'gbp policy-classifier-delete '+str(classifier_name)
        if cmd_val == 1:
           cmd = 'gbp policy-classifier-create '+str(classifier_name)
        if cmd_val == 2:
           cmd = 'gbp policy-classifier-update '+str(classifier_name)
        # Build the cmd string for optional/non-default args/values
        for arg, value in kwargs.items():
          cmd = cmd + " --" + "".join( '%s %s' %(arg, value ))
        #_log.info(cmd)
        # Execute the policy-classifier-config-cmd
        cmd_out = getoutput(cmd)
        # Catch for non-exception error strings, even though try clause succeded
        for err in self.err_strings:
            if re.search(r'\b%s\b' %(err), cmd_out, re.I):
               _log.info(cmd_out)
               _log.info( "Cmd execution failed! with this Return Error: \n%s" %(cmd_out))
               return 0
        # If try clause succeeds for "create" cmd then parse the cmd_out to extract the UUID
        if cmd_val==1:
           classifier_uuid = self.gbp_uuid_get(cmd_out)
           return classifier_uuid

    def gbp_policy_cfg_all(self,cmd_val,cfgobj,name_uuid,**kwargs):
        """
	--cfgobj== policy-*(where *=action;classifer,rule,ruleset,targetgroup,target
        --cmd_val== 0:delete; 1:create; 2:update
        --name_uuid == UUID or name_string
        Create/Update/Delete Policy Object
        Returns assigned UUID on Create
        kwargs addresses the need for passing required/optional params
        """
        cfgobj_dict={"action":"policy-action","classifier":"policy-classifier","rule":"policy-rule",
                      "ruleset":"policy-rule-set","group":"policy-target-group","target":"policy-target",
                      "l2p":"l2policy","l3p":"l3policy","nsp":"network-service-policy"}
        if cfgobj != '':
           if cfgobj not in cfgobj_dict:
              raise KeyError 
        if cmd_val == '' or name_uuid == '':
           _log.info('''Function Usage: gbp_policy_cfg_all 'rule' 0 "abc"\n
                      --cmd_val == 0:delete; 1:create; 2:update\n
                      -- name_uuid == UUID or name_string\n''')
           return 0

        #Build the command with mandatory params
        if cmd_val == 0:
           cmd = 'gbp %s-delete ' % cfgobj_dict[cfgobj]+str(name_uuid)
        if cmd_val == 1:
           cmd = 'gbp %s-create ' % cfgobj_dict[cfgobj]+str(name_uuid)
        if cmd_val == 2:
           cmd = 'gbp %s-update ' % cfgobj_dict[cfgobj]+str(name_uuid)
        # Build the cmd string for optional/non-default args/values
        for arg, value in kwargs.items():
          if '_' in arg:
             arg=string.replace(arg,'_','-')
          cmd = cmd + " --" + "".join( '%s %s' %(arg, value ))
        _log.info(cmd)
        # Execute the cmd
        cmd_out = getoutput(cmd)
        #_log.info(cmd_out)
        # Catch for non-exception error strings, even though try clause succeded
        for err in self.err_strings:
            if re.search(r'\b%s\b' %(err), cmd_out, re.I):
               _log.info( "Cmd execution failed! with this Return Error: \n%s" %(cmd_out))
               return 0
        # If try clause succeeds for "create" cmd then parse the cmd_out to extract the UUID of the object
        try:
	 if cmd_val==1 and cfgobj=="group":
           obj_uuid = self.gbp_uuid_get(cmd_out)
           match = re.search("\\bl2_policy_id\\b\s+\| (.*) \|",cmd_out,re.I)
           l2pid = match.group(1)
           match = re.search("\\bsubnets\\b\s+\| (.*) \|",cmd_out,re.I)
           subnetid = match.group(1)
           return obj_uuid,l2pid.rstrip(),subnetid.rstrip()
         if cmd_val==1 and cfgobj=="target":
           obj_uuid = self.gbp_uuid_get(cmd_out)
           match = re.search("\\bport_id\\b\s+\| (.*) \|",cmd_out,re.I)
           neutr_port_id = match.group(1)
           return obj_uuid.rstrip(),neutr_port_id.rstrip()
         if cmd_val==1 and cfgobj=="l2p":
            obj_uuid = self.gbp_uuid_get(cmd_out)
            match = re.search("\\l3_policy_id\\b\s+\| (.*) \|",cmd_out,re.I)
            l3p_uuid = match.group(1)
            return obj_uuid.rstrip(),l3p_uuid.rstrip()
         if cmd_val==1:
           obj_uuid = self.gbp_uuid_get(cmd_out)
           return obj_uuid.rstrip()
        except Exception as e:
           exc_type, exc_value, exc_traceback = sys.exc_info()
           _log.info('Exception Type = %s, Exception Object = %s' %(exc_type,exc_value))
           return 0
        return 1

    def gbp_policy_cfg_upd_all(self,cfgobj,name_uuid,attr):
        """
        --cfgobj== policy-*(where *=action;classifer,rule,ruleset,targetgroup,target
        --name_uuid == UUID or name_string
        --attr == MUST be a dict, where key: attribute_name, while val: attribute's value(new value to update)
        Updates Policy Objects' editable attributes
        """
        cfgobj_dict={"action":"policy-action","classifier":"policy-classifier","rule":"policy-rule",
                      "ruleset":"policy-rule-set","group":"policy-target-group","target":"policy-target",
                      "l2p":"l2policy","l3p":"l3policy","nsp":"network-service-policy"}
        if cfgobj != '':
           if cfgobj not in cfgobj_dict:
              raise KeyError
        if name_uuid == '' or not isinstance(attr,dict):
           _log.info('''Function Usage: gbp_policy_cfg_upd_all 'rule' "abc" {attr:attr_val}\n
                      --cmd_val == 0:delete; 1:create; 2:update\n
                      -- name_uuid == UUID or name_string\n''')
           return 0

        #Build the command with mandatory params
        cmd = 'gbp %s-update ' % cfgobj_dict[cfgobj]+str(name_uuid)
        # Build the cmd string for optional/non-default args/values
        for arg, value in attr.iteritems():
          if '_' in arg:
             arg=string.replace(arg,'_','-')
          cmd = cmd + " --" + "".join( '%s %s' %(arg, value ))
        _log.info(cmd)
        # Execute the update cmd
        cmd_out = getoutput(cmd)
        #_log.info(cmd_out)
        # Catch for non-exception error strings, even though try clause succeded
        for err in self.err_strings:
            if re.search(r'\b%s\b' %(err), cmd_out, re.I):
               _log.info(cmd_out)
               _log.info( "Cmd execution failed! with this Return Error: \n%s" %(cmd_out))
               return 0
        return 1

    def gbp_del_all_anyobj(self,cfgobj):
        """
        This function deletes all entries for any policy-object
        """
        cfgobj_dict={"action":"policy-action","classifier":"policy-classifier","rule":"policy-rule",
                      "ruleset":"policy-rule-set","group":"group","target":"policy-target",
                      "l2p":"l2policy","l3p":"l3policy","nsp":"network-service-policy",
                      "node":"servicechain-node","spec":"servicechain-spec"}
        if cfgobj != '':
           if cfgobj not in cfgobj_dict:
              raise KeyError
        #Build the command with mandatory params
        cmd = 'gbp %s-list -c id ' % cfgobj_dict[cfgobj]
        cmd_out = getoutput(cmd)
        uuid_list=[]
        _out=cmd_out.split('\n')
        final_out = _out[3:len(_out)-1]
        _log.info("\nThe Policy Object %s to be deleted = \n%s" %(cfgobj_dict[cfgobj],cmd_out))
        for item in final_out:
            item = item.strip(' |')
            cmd = 'gbp %s-delete ' % cfgobj_dict[cfgobj]+str(item)
            cmd_out = getoutput(cmd)
            _log.info(cmd_out)
        return 1 

    def gbp_sc_cfg_all(self,cmd_val,cfgobj,name_uuid,nodes="",svc_type='lb'):
        """
        ::cmd_val= 0: delete; 1:create
        ::cfgobj = servicechain-*(where *=node;spec)
        ::name_uuid = UUID or name_string
        ::svc_type = LOADBALANCER or FIREWALL, defaulted to LB  
        Create/Update/Delete Policy Object
        Returns assigned UUID on Create
        kwargs addresses the need for passing required/optional params
        """
        cfgobj_dict={"node":"servicechain-node","spec":"servicechain-spec"}
        if cfgobj != '':
           if cfgobj not in cfgobj_dict:
              raise KeyError
        if cmd_val == '' or name_uuid == '':
           _log.info('''Function Usage: gbp_sc_cfg_all(0,"node","name or uuid")\n''')
           return 0

        #Build the command with mandatory params
        if cmd_val == 0:
           cmd = 'gbp %s-delete ' % cfgobj_dict[cfgobj]+str(name_uuid)
        if cmd_val == 1 and cfgobj == 'spec':
           cmd = 'gbp %s-create ' % cfgobj_dict[cfgobj]+str(name_uuid)+' --nodes "%s"' %(nodes)
        if cmd_val == 1 and cfgobj == 'node':
           if svc_type == 'lb':
              service='LOADBALANCER'
           else:
              service='FIREWALL'
           cmd = 'gbp %s-create ' % cfgobj_dict[cfgobj]+str(name_uuid)+' --template-file %s.template' %(svc_type)+' --servicetype '+service
        _log.info(cmd)
        # Execute the policy-rule-config-cmd
        cmd_out = getoutput(cmd)
        #_log.info(cmd_out)
        # Catch for non-exception error strings, even though try clause succeded
        for err in self.err_strings:
            if re.search(r'\b%s\b' %(err), cmd_out, re.I):
               _log.info(cmd_out)
               _log.info( "Cmd execution failed! with this Return Error: \n%s" %(cmd_out))
               return 0
        if cmd_val==1:
           obj_uuid = self.gbp_uuid_get(cmd_out)
           return obj_uuid

