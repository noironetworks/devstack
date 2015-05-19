#!/usr/bin/env python
import os,sys,optparse,platform
import glob
import importlib
import yaml
from commands import *

def main():
    f = open(sys.argv[1],'rt')
    test_conf = yaml.load(f)
    test_runner = wrapper(test_conf)
    test_runner.run()

class wrapper(object):
   
    def __init__(self,config_file):
       self.cntrl_ip = config_file['controller_ip']
       self.heat_stack_name = config_file['heat_stack_name']
       self.leaf_ip = config_file['leaf_ip']
       self.apic_ip = config_file['apic_ip']
       self.heat_temp_file = config_file['main_setup_heat_temp']        
       self.ntk_node = config_file['compnode1_ip']
       self.nova_agg = config_file['nova_agg_name']
       self.nova_az = config_file['nova_az_name']
       self.az_comp_node = config_file['az_comp_node']
       self.leaf_port1 = config_file['leaf1_to_comp1_conn']
       self.leaf_por2 = config_file['leaf1_to_comp2_conn']
       self.comp_node_ips = config_file['comp_nodes']

    def run(self):
       for class_name in [filename.strip('.py') for filename in glob.glob('testcase_gbp_intg*.py')]:
           imp_class = importlib.import_module(class_name)
           class_obj = getattr(imp_class,class_name)
           if callable(class_obj):
              if class_name.find('leaf') > -1: #Testcase names with 'leaf' substring
                 cls = class_obj(self.heat_temp_file,self.cntrl_ip,self.leaf_ip,\
                                 self.apic_ip,self.ntk_node,self.nova_agg,\
                                 self.nova_az,self.az_comp_node,self.leaf_port1,self.leaf_port2,self.comp_node_ips)
              else:
                 cls = class_obj(self.heat_temp_file,self.cntrl_ip,self.leaf_ip,\
                              self.apic_ip,self.ntk_node,self.nova_agg,\
                              self.nova_az,self.az_comp_node)
              cls.test_runner('TESTCASE_ACI_INTEG')

if __name__ == '__main__':
   main()
