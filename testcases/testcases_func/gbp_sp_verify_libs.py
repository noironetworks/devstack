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

class Gbp_Verify(object):

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

    def gbp_action_verify(self,cmd_val,action_name,*args,**kwargs):
        """
        -- cmd_val== 0:list; 1:show
        -- action_name == UUID or name_string
        List/Show Policy Action
        kwargs addresses the need for passing required/optional params
        """
        if cmd_val == '' or action_name == '':
           _log.info('''Function Usage: gbp_action_verify 0 "abc" \n
                      --cmd_val == 0:list; 1:show\n
                       -- action_name == UUID or name_string\n''')
           return 0
        #Build the command with mandatory param 'action_name'
        if cmd_val == 0:
           cmd = 'gbp policy-action-list | grep %s'% str(action_name)
           for arg in args:
             cmd = cmd + ' | grep %s' % arg
        if cmd_val == 1:
           cmd = "gbp policy-action-show "+str(action_name)
        # Execute the policy-action-verify-cmd
        try:
            cmd_out = subprocess.check_output("source openrc && %s" %(cmd), shell=True, stderr=subprocess.STDOUT,executable="/bin/bash")
            _log.debug( "%s\n%s\n" % ( cmd, cmd_out ))
        except subprocess.CalledProcessError as err:
            _log.info( "Cmd execution failed! \nreturncode - '%s'\ncmd - '%s'\noutput - %s" % ( err.returncode, err.cmd, err.output ))
        # Catch for non-exception error strings, even though try clause succeded
        for err in self.err_strings:
            if re.search(r'\b%s\b' %(err), cmd_out, re.I):
               _log.info( "Cmd execution failed! with this Return Error: \n%s" %(output))
               return 0
        # If try clause succeeds for "verify" cmd then parse the cmd_out to match the user-fed expected attributes & their values
        if cmd_val == 1:
         for arg, val in kwargs.items():
           if re.search("\\b%s\\b\s+\| \\b%s\\b.*" %(arg,val),cmd_out,re.I)==None:
             _log.info("The Attribute== %s and its Value== %s DID NOT MATCH for the Action == %s" %(arg,val,action_name))
             return 0
        _log.info("All attributes & values found Valid for the object Policy Action == %s" %(action_name))
	return 1     

    def gbp_classif_verify(self,cmd_val,classifier_name,*args,**kwargs):
        """
        -- cmd_val== 0:list; 1:show
        -- classifier_name == UUID or name_string
        List/Show Policy Action
        kwargs addresses the need for passing required/optional params
        """
        if cmd_val == '' or classifier_name == '':
           _log.info('''Function Usage: gbp_classif_verify 0 "abc" \n
                      --cmd_val == 0:delete; 1:create; 2:update\n
                       -- classifier_name == UUID or name_string\n''')
           return 0
        #Build the command with mandatory param 'classifier_name'
        if cmd_val == 0:
           cmd = 'gbp policy-classifier-list | grep %s'% str(classifier_name)
           for arg in args:
             cmd = cmd + ' | grep %s' % arg
        if cmd_val == 1:
           cmd = "gbp policy-classifier-show "+str(classifier_name)
        # Execute the policy-classifier-verify-cmd
        try:
            cmd_out = subprocess.check_output("source openrc && %s" %(cmd), shell=True, stderr=subprocess.STDOUT,executable="/bin/bash")
            _log.debug( "%s\n%s\n" % ( cmd, cmd_out ))
        except subprocess.CalledProcessError as err:
            _log.info( "Cmd execution failed! \nreturncode - '%s'\ncmd - '%s'\noutput - %s" % ( err.returncode, err.cmd, err.output ))
        # Catch for non-exception error strings, even though try clause succeded
        for err in self.err_strings:
            if re.search(r'\b%s\b' %(err), cmd_out, re.I):
               _log.info( "Cmd execution failed! with this Return Error: \n%s" %(output))
               return 0
        # If try clause succeeds for "verify" cmd then parse the cmd_out to match the user-fed expected attributes & their values
        if cmd_val == 1:
         for arg, val in kwargs.items():
           if re.search("\\b%s\\b\s+\| \\b%s\\b.*" %(arg,val),cmd_out,re.I)==None:
             _log.info("The Attribute== %s and its Value== %s DID NOT MATCH for the Action == %s" %(arg,val,classifier_name))
             return 0
        _log.info("All attributes & values found Valid for the object Policy Action == %s" %(classifier_name))
        return 1

    def gbp_policy_verify_all(self,cmd_val,cfgobj,name,*args,**kwargs):
        """
        --cfgobj== policy-*(where *=action;classifer,rule,rule-set,target-group,target
        --cmd_val== 0:list; 1:show
        kwargs addresses the need for passing required/optional params
        """
        cfgobj_dict={"action":"policy-action","classifier":"policy-classifier","rule":"policy-rule",
                      "ruleset":"policy-rule-set","group":"group","target":"policy-target"}
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
           cmd = 'gbp %s-list | grep ' % cfgobj_dict[cfgobj]+str(name)
           for arg in args:
             cmd = cmd + ' | grep %s' % arg
        if cmd_val == 1:
           cmd = 'gbp %s-show ' % cfgobj_dict[cfgobj]+str(name)
        # Execute the policy-object-verify-cmd
        try:
            cmd_out = subprocess.check_output("source openrc && %s" %(cmd), shell=True, stderr=subprocess.STDOUT,executable="/bin/bash")
            _log.debug( "%s\n%s\n" % ( cmd, cmd_out ))
        except subprocess.CalledProcessError as err:
            _log.info( "Cmd execution failed! \nreturncode - '%s'\ncmd - '%s'\noutput - %s" % ( err.returncode, err.cmd, err.output ))
        # Catch for non-exception error strings, even though try clause succeded
        for err in self.err_strings:
            if re.search(r'\b%s\b' %(err), cmd_out, re.I):
               _log.info( "Cmd execution failed! with this Return Error: \n%s" %(output))
               return 0
        # If try clause succeeds for "verify" cmd then parse the cmd_out to match the user-fed expected attributes & their values
        if cmd_val == 1:
         for arg, val in kwargs.items():
           if re.search("\\b%s\\b\s+\| \\b%s\\b.*" %(arg,val),cmd_out,re.I)==None:
             _log.info("The Attribute== %s and its Value== %s DID NOT MATCH for the PolicyObject == %s" %(arg,val,cfgobj))
             return 0
        _log.info("All attributes & values found Valid for the object Policy %s" %(cfgobj))
        return 1


