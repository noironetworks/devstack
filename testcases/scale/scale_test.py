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

gdb_crud = GBPCrud(sys.argv[1])

l3p = gdb_crud.create_gbp_l3policy('scale_l3p',ip_pool='1.2.3.0/16',subnet_prefix_length=24)
l3p_id = gdb_crud.verify_gbp_l3policy('scale_l3p')
print 'L3Policy == ', l3p_id

for i in range(1, 101):
    
    action_name = 'scale_action_%s' %(i)
    gdb_crud.create_gbp_policy_action(action_name, action_type='allow')
    action_id = gdb_crud.verify_gbp_policy_action(action_name)
    print '\naction_id ==', action_id

    classifier_name = 'scale_classifier_%s' %(i)
    gdb_crud.create_gbp_policy_classifier(classifier_name, direction='bi', protocol='icmp')
    classifier_id = gdb_crud.verify_gbp_policy_classifier(classifier_name)
    print 'classifier_id ==', classifier_id

    policy_rule_name = 'scale_policy_rule_%s' %(i)
    gdb_crud.create_gbp_policy_rule(policy_rule_name, classifier_id, action_id, 'uuid')
    policy_rule_id = gdb_crud.verify_gbp_policy_rule(policy_rule_name)
    print 'policy_rule_id ==', policy_rule_id

    policy_ruleset_name = 'scale_policy_ruleset_%s' %(i)
    gdb_crud.create_gbp_policy_ruleset(policy_ruleset_name, [policy_rule_id] ,'uuid')
    policy_ruleset_id = gdb_crud.verify_gbp_policy_rule_set(policy_ruleset_name)
    print 'policy_ruleset_id ==', policy_ruleset_id

    l2p_name = 'scale_l2p_%s' %(i)
    gdb_crud.create_gbp_l2policy(l2p_name, l3_policy_id=l3p_id)
    sleep(1)
    l2p_id = gdb_crud.verify_gbp_l2policy(l2p_name)
    print 'L2P ID ==', l2p_id
  
    ruleset_dict = {} 
    ruleset_dict[policy_ruleset_id] = "scope"
 
    ptg_name = 'scale_ptg_%s' %(i)
    gdb_crud.create_gbp_policy_target_group(ptg_name, l2_policy_id=l2p_id)
    #gdb_crud.create_gbp_policy_target_group(ptg_name, l2_policy_id=l2p_id, consumed_policy_rule_sets=ruleset_dict, provided_policy_rule_sets=ruleset_dict)
    ptg_id = gdb_crud.verify_gbp_policy_target_group(ptg_name)
    print 'PTG ID ==', ptg_id

    pt_name = 'scale_pt_%s' %(i)
    gdb_crud.create_gbp_policy_target(pt_name, ptg_name)
    pt_dict = gdb_crud.verify_gbp_policy_target(pt_name)
    print 'PT Dict ==', pt_dict

action_ids = gdb_crud.get_gbp_policy_action_list(getlist=True)
classifier_ids = gdb_crud.get_gbp_policy_classifier_list(getlist=True)	
policy_rule_ids = gdb_crud.get_gbp_policy_rule_list(getlist=True)
policy_ruleset_ids = gdb_crud.get_gbp_policy_rule_set_list(getlist=True)
l2p_list_ids = gdb_crud.get_gbp_l2policy_list(getlist=True)
ptg_list = gdb_crud.get_gbp_policy_target_group_list(getlist=True)
pt_dict = gdb_crud.get_gbp_policy_target_list()

print '\nAction IDs == \n', action_ids
print '\nClassifier IDs == \n', classifier_ids
print '\nPolicy Rule IDs == \n', policy_rule_ids
print '\nPolicy Rule Set IDs == \n', policy_ruleset_ids
print '\nL2POLICY LIST IDs ==\n', l2p_list_ids
print '\nPTG LIST == \n', ptg_list
print '\nPT Dict == \n', pt_dict

#for pt in pt_dict.iterkeys():
#    gdb_crud.delete_gbp_policy_target(pt, 'uuid')

#for ptg in ptg_list.itervalues():
#    gdb_crud.delete_gbp_policy_target_group(ptg, 'uuid')

for l2p in l2p_list_ids.itervalues():
    gdb_crud.delete_gbp_l2policy(l2p, 'uuid')

for ruleset in policy_ruleset_ids.itervalues():
    gdb_crud.delete_gbp_policy_rule_set(ruleset, 'uuid')

for rule in policy_rule_ids.itervalues():
    gdb_crud.delete_gbp_policy_rules(rule, 'uuid')

for action in action_ids.itervalues():
    gdb_crud.delete_gbp_policy_action(action, 'uuid')

for classifier in classifier_ids.itervalues():
    gdb_crud.delete_gbp_policy_classifier(classifier, 'uuid')

gdb_crud.delete_gbp_l3policy(l3p_id, 'uuid')
