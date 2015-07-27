#!/usr/bin/env python
import sys
import sys
import logging
import os
import datetime
import string
import pdb
from time import sleep
from libs.raise_exceptions import *
from libs.gbp_crud_libs import GBPCrud
from libs.gbp_nova_libs import Gbp_Nova
from libs.gbp_conf_libs import Gbp_Config
from okeystone import Keystone

for j in range(1, 101):

    tenantName = 'scale_tenant_%s' %(j)	
#    key_stone = Keystone(ostack_controller=sys.argv[1])
    print "tenant name = " + tenantName

    for i in range(1, 36):

        # launch the VMs
        gbp_nova = Gbp_Nova(ostack_controller=sys.argv[1], os_tenant=tenantName)
        vm_name = '%s_scale_vm_%s' % (j, i)
        gbp_nova.vm_delete(vm_name, 'api')

gbp_conf = Gbp_Config()
gbp_conf.del_netns('172.28.184.84')

gdb_crud = GBPCrud(ostack_controller=sys.argv[1])
    
""" 
action_ids = gdb_crud.get_gbp_policy_action_list(getlist=True)
classifier_ids = gdb_crud.get_gbp_policy_classifier_list(getlist=True)	
policy_rule_ids = gdb_crud.get_gbp_policy_rule_list(getlist=True)
policy_ruleset_ids = gdb_crud.get_gbp_policy_rule_set_list(getlist=True)
"""

l3p_list_ids = gdb_crud.get_gbp_l3policy_list(getlist=True)    
l2p_list_ids = gdb_crud.get_gbp_l2policy_list(getlist=True)
ptg_list = gdb_crud.get_gbp_policy_target_group_list(getlist=True)
pt_dict = gdb_crud.get_gbp_policy_target_list()

"""
print '\nAction IDs == \n', action_ids
print '\nClassifier IDs == \n', classifier_ids
print '\nPolicy Rule IDs == \n', policy_rule_ids
print '\nPolicy Rule Set IDs == \n', policy_ruleset_ids
"""
print '\nL3POLICY LIST IDs ==\n', l3p_list_ids
print '\nL2POLICY LIST IDs ==\n', l2p_list_ids
print '\nPTG LIST == \n', ptg_list
print '\nPT Dict == \n\n', pt_dict

for pt in pt_dict.iterkeys():
    gdb_crud.delete_gbp_policy_target(pt, 'uuid')

for ptg in ptg_list.itervalues():
    gdb_crud.delete_gbp_policy_target_group(ptg, 'uuid')

for l2p in l2p_list_ids.itervalues():
    gdb_crud.delete_gbp_l2policy(l2p, 'uuid')

"""
for ruleset in policy_ruleset_ids.itervalues():
    gdb_crud.delete_gbp_policy_rule_set(ruleset, 'uuid')

for rule in policy_rule_ids.itervalues():
    gdb_crud.delete_gbp_policy_rules(rule, 'uuid')

for action in action_ids.itervalues():
    gdb_crud.delete_gbp_policy_action(action, 'uuid')

for classifier in classifier_ids.itervalues():
    gdb_crud.delete_gbp_policy_classifier(classifier, 'uuid')
"""

for l3p in l3p_list_ids.itervalues():
    gdb_crud.delete_gbp_l3policy(l3p, 'uuid')

