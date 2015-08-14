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
       """
       Read Config from Config File
       """
       self.all_class_init_params = {
                                     'cntlr_ip' : config_file['controller_ip'],
                                     'nova_agg' : config_file['nova_agg_name'],
                                     'nova_az' : config_file['nova_az_name'],
                                     'az_comp_node' : config_file['az_comp_node'],
                                     'heat_temp_file' : config_file['main_setup_heat_temp'],
                                     'ntk_node' : config_file['compnode1_ip'],
                                     'comp_node_ips' : config_file['comp_nodes'],
                                     'compnode1_ip' : config_file['compnode1_ip'],
                                     'compnode2_ip' : config_file['compnode2_ip'],
                                     'apic_ip' : config_file['apic_ip'],
                                     'leaf1_node_id' : config_file['leaf1_node_id'],
                                     'leaf2_node_id' : config_file['leaf2_node_id'],
                                     'leaf1_ip' : config_file['leaf1_ip'],
                                     'leaf2_ip' : config_file['leaf2_ip'],
                                     'leaf1_port1' : config_file['leaf1_to_compnode1_conn'],
                                     'leaf1_port2' : config_file['leaf1_to_compnode2_conn'],
                                     'leaf2_port1' : config_file['leaf2_to_compnode1_conn'],
                                     'leaf2_port2' : config_file['leaf2_to_compnode2_conn'],
                                     'leaf1_spine_conn' : config_file['leaf1_to_spine_conn'],
                                     'leaf2_spine_conn' : config_file['leaf2_to_spine_conn']
                                    }


    def run(self):
       #Reason: Any new testcase added to the directory will be automatically run
       #provided i's name string starts with testcase_gbp_aci_intg
       for class_name in [filename.strip('.py') for filename in glob.glob('testcase_gbp_aci_intg*.py')]:
           imp_class = importlib.import_module(class_name)
           class_obj = getattr(imp_class,class_name)
           if callable(class_obj):
              cls = class_obj(self.all_class_init_params)
              cls.test_runner()

if __name__ == '__main__':
   main()
