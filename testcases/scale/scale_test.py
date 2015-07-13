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

l3p = gdb_crud.create_gbp_l3policy('scale_l3p',ip_pool='1.2.3.0/16',subnet_prefix_length=30)
l3p_id = gdb_crud.verify_gbp_l3policy('scale_l3p')
print 'L3Policy == ', l3p_id

for i in range(1,101):
    l2p_name = 'scale_l2p_%s' %(i)
    gdb_crud.create_gbp_l2policy(l2p_name,l3_policy_id=l3p_id)
    sleep(1)
    l2p_id = gdb_crud.verify_gbp_l2policy(l2p_name)
    print 'L2P ID == ', l2p_id
    ptg_name = 'scale_ptg_%s' %(i)
    gdb_crud.create_gbp_policy_target_group(ptg_name,l2_policy_id=l2p_id)

ptg_list = gdb_crud.get_gbp_policy_target_group_list(getlist=True)
l2p_list_ids = gdb_crud.get_gbp_l2policy_list(getlist=True)

print 'PTG LIST /NAME == \n', ptg_list
print '\n L2POLICY LIST IDs ==\n', l2p_list_ids

for val in ptg_list.itervalues():
    gdb_crud.delete_gbp_policy_target_group(val, 'uuid')

for l2p in l2p_list_ids.itervalues():
    gdb_crud.delete_gbp_l2policy(l2p, 'uuid')

gdb_crud.delete_gbp_l3policy(l3p_id, 'uuid')
