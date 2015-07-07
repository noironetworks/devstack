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

x = GBPCrud('172.28.184.45')

#ptg_list = x.get_gbp_policy_target_group_list(getlist=True)
l2p_list_ids = x.get_gbp_l2policy_list(getlist=True)
print l2p_list_ids

#for val in ptg_list.itervalues():
#    x.delete_gbp_policy_target_group(val,property_type='uuid')

for val in l2p_list_ids.itervalues():
    x.delete_gbp_l2policy(val,property_type='uuid')
