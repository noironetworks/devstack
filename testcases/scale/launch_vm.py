#!/usr/bin/env python
import sys
import logging
import os
import datetime
import string
import pdb
from libs.raise_exceptions import *
from libs.gbp_crud_libs import GBPCrud
from libs.gbp_nova_libs import Gbp_Nova

for j in range(1, 6):                                                                                      

    tenantName = 'scale_tenant_%s' % (j)
    gbp_crud = GBPCrud(sys.argv[1], tenant=tenantName)

    pt_dict = gbp_crud.get_gbp_policy_target_list()
    print '\nPT Dict == \n', pt_dict

    gbp_nova = Gbp_Nova(sys.argv[1], os_tenant=tenantName)
    
    i = 1
    for pt in pt_dict.itervalues():
        vm_name = '%s_scale_vm_%s' % (j, i)   
        print vm_name
        gbp_nova.vm_create_api(vm_name, 'cirros', pt, 'm1.tiny', 'nova')
        #gbp_nova.vm_delete(vm_name, 'api')
        i = i + 1
