#!/usr/bin/python

import sys
from time import sleep
import fileinput
import subprocess
import math
import logging
import os
import string
import shutil
import sys
import getpass
import socket
import re
import crypt
import getpass
import pwd
import datetime
import getopt

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
      self.err_strings=['Bad Request','Error']
	
    def exe_command(self,command_args):
      """
      Execute system calls
      """
      proc = subprocess.Popen(command_args, shell=False,stdout=subprocess.PIPE)
      #proc.communicate()
      return proc.stdout.read()

    def gbp_action_config(self,cmd_val,action_name,**kwargs):
	"""
        -- cmd_val== 0:delete; 1:create; 2:update
	-- action_name == UUID or name_string
        Create/Update/Delete Policy Action
        Returns assigned UUID on Create
        kwargs addresses the need for passing required/optional params
        """
        if cmd_val == '' or action_name == '':
           _log.info('''Function Usage: gbp_action_config 0 "abc"\n
                      --cmd_val == 0:delete; 1:create; 2:update\n
                       -- action_name == UUID or name_string\n''')
           return 0
        #Build the command with mandatory param 'action_name' 
        if cmd_val == 0:
           cmd = 'gbp policy-action-delete '+str(action_name)
        if cmd_val == 1:
           cmd = 'gbp policy-action-create '+str(action_name)
        if cmd_val == 2:
           cmd = 'gbp policy-action-update '+str(action_name)
        # Build the cmd string for optional/non-default args/values
        for arg, value in kwargs.items():
          cmd = cmd + " --" + "".join( '%s %s' %(arg, value ))
        #_log.info(cmd)
        # Execute the policy-action-config-cmd
        try:
            cmd_out = subprocess.check_output("source openrc && %s" %(cmd), shell=True, stderr=subprocess.STDOUT,executable="/bin/bash")
            _log.info( "%s\n%s\n" % (cmd,cmd_out))
        except subprocess.CalledProcessError as err:
            _log.debug( "Cmd execution failed! \nreturncode - '%s'\ncmd - '%s'\noutput - %s" % ( err.returncode, err.cmd, err.output ))
        # Catch for non-exception error strings, even though try clause succeded
        for err in self.err_strings:
	    if re.search(r'\b%s\b' %(err), cmd_out, re.I):
	       _log.info( "Cmd execution failed! with this Return Error: \n%s" %(cmd_out))
	       return 0
        # If try clause succeeds for "create" cmd then parse the cmd_out to extract the UUID
        if cmd_val==1:
           match=re.search("\\bid\\b\s+\| (.*) \|",cmd_out,re.I)
	   action_uuid = match.group(1)
           #_log.info( "UUID:\n%s " %(action_uuid))
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
        try:
            cmd_out = subprocess.check_output("source openrc && %s" %(cmd), shell=True, stderr=subprocess.STDOUT,executable="/bin/bash" )
            _log.debug( "%s\n%s\n" % ( cmd, cmd_out ))
        except subprocess.CalledProcessError as err:
            _log.info( "Cmd execution failed! \nreturncode - '%s'\ncmd - '%s'\noutput - %s" % ( err.returncode, err.cmd, err.output ))
        # Catch for non-exception error strings, even though try clause succeded
        for err in self.err_strings:
            if re.search(r'\b%s\b' %(err), cmd_out, re.I):
               _log.info( "Cmd execution failed! with this Return Error: \n%s" %(cmd_out))
               return 0
        # If try clause succeeds for "create" cmd then parse the cmd_out to extract the UUID
        if cmd_val==1:
           match=re.search("\\bid\\b\s+\| (.*) \|",cmd_out,re.I)
           classifier_uuid = match.group(1)
           #_log.info( "UUID:\n%s " %(classifier_uuid))
           return classifier_uuid

    def gbp_rule_config(self,cmd_val,rule_name,**kwargs):
        """
        -- cmd_val== 0:delete; 1:create; 2:update
        -- rule_name == UUID or name_string
        Create/Update/Delete Policy Rule
        Returns assigned UUID on Create
        kwargs addresses the need for passing required/optional params
        """
        if cmd_val == '' or rule_name == '':
           _log.info('''Function Usage: gbp_classifier_config 0 "abc"\n
                      --cmd_val == 0:delete; 1:create; 2:update\n
                      -- rule_name == UUID or name_string\n''')
           return 0
        #Build the command with mandatory param 'rule_name'
        if cmd_val == 0:
           cmd = 'gbp policy-rule-delete '+str(rule_name)
        if cmd_val == 1:
           cmd = 'gbp policy-rule-create '+str(rule_name)
        if cmd_val == 2:
           cmd = 'gbp policy-rule-update '+str(rule_name)
        # Build the cmd string for optional/non-default args/values
        for arg, value in kwargs.items():
          cmd = cmd + " --" + "".join( '%s %s' %(arg, value ))
        #_log.info(cmd)
        # Execute the policy-rule-config-cmd
        try:
            cmd_out = subprocess.check_output("source openrc && %s" %(cmd), shell=True, stderr=subprocess.STDOUT,executable="/bin/bash")
            _log.debug( "%s\n%s\n" % ( cmd, cmd_out ))
        except subprocess.CalledProcessError as err:
            _log.info( "Cmd execution failed! \nreturncode - '%s'\ncmd - '%s'\noutput - %s" % ( err.returncode, err.cmd, err.output ))
        # Catch for non-exception error strings, even though try clause succeded
        for err in self.err_strings:
            if re.search(r'\b%s\b' %(err), cmd_out, re.I):
               _log.info( "Cmd execution failed! with this Return Error: \n%s" %(cmd_out))
               return 0
        # If try clause succeeds for "create" cmd then parse the cmd_out to extract the UUID
        if cmd_val==1:
           match=re.search("\\bid\\b\s+\| (.*) \|",cmd_out,re.I)
           classifier_uuid = match.group(1)
           #_log.info( "UUID:\n%s " %(classifier_uuid))
           return classifier_uuid

    def gbp_policy_cfg_all(self,cmd_val,cfgobj,name,**kwargs):
        """
	--cfgobj== policy-*(where *=action;classifer,rule,ruleset,targetgroup,target
        --cmd_val== 0:delete; 1:create; 2:update
        --name == UUID or name_string
        Create/Update/Delete Policy Rule
        Returns assigned UUID on Create
        kwargs addresses the need for passing required/optional params
        """
        cfgobj_dict={"action":"policy-action","classifier":"policy-classifier","rule":"policy-rule",
                      "ruleset":"policy-rule-set","group":"policy-target-group","target":"policy-target"}
        if cfgobj != '':
           if cfgobj not in cfgobj_dict:
              raise KeyError 
        if cmd_val == '' or name == '':
           _log.info('''Function Usage: gbp_policy_cfg_all 'rule' 0 "abc"\n
                      --cmd_val == 0:delete; 1:create; 2:update\n
                      -- name == UUID or name_string\n''')
           return 0

        #Build the command with mandatory params
        if cmd_val == 0:
           cmd = 'gbp %s-delete ' % cfgobj_dict[cfgobj]+str(name)
        if cmd_val == 1:
           cmd = 'gbp %s-create ' % cfgobj_dict[cfgobj]+str(name)
        if cmd_val == 2:
           cmd = 'gbp %s-update ' % cfgobj_dict[cfgobj]+str(name)
        # Build the cmd string for optional/non-default args/values
        for arg, value in kwargs.items():
          if '_' in arg:
             arg=string.replace(arg,'_','-')
          cmd = cmd + " --" + "".join( '%s %s' %(arg, value ))
        #_log.info(cmd)
        # Execute the policy-rule-config-cmd
        try:
            cmd_out = subprocess.check_output("source openrc && %s" %(cmd), shell=True, stderr=subprocess.STDOUT,executable="/bin/bash")
            _log.debug( "%s\n%s\n" % ( cmd, cmd_out ))
        except subprocess.CalledProcessError as err:
            _log.info( "Cmd execution failed! \nreturncode - '%s'\ncmd - '%s'\noutput - %s" % ( err.returncode, err.cmd, err.output ))
        # Catch for non-exception error strings, even though try clause succeded
        for err in self.err_strings:
            if re.search(r'\b%s\b' %(err), cmd_out, re.I):
               _log.info( "Cmd execution failed! with this Return Error: \n%s" %(cmd_out))
               return 0
        # If try clause succeeds for "create" cmd then parse the cmd_out to extract the UUID of the object
        if cmd_val==1:
           match=re.search("\\bid\\b\s+\| (.*) \|",cmd_out,re.I)
           obj_uuid = match.group(1)
           #_log.info( "UUID:\n%s " %(obj_uuid))
           return obj_uuid

