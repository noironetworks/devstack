#!/usr/bin/python

import sys
import logging
import os
import datetime
from gbp_conf_libs import *
from gbp_verify_libs import *
from gbp_heat_libs import *
from gbp_nova_libs import * 
from gbp_def_traffic import *

def main():

    # Bring up GBP Master Config using Heat
    allgbpcfg = gbp_main_config()
    allgbpcfg.setup()  

class gbp_main_config(object):
    """
    The intent of this class is to setup the complete GBP config 
    needed for running all DP testcases
    """
    # Initialize logging
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=logging.WARNING)
    _log = logging.getLogger( __name__ )
    hdlr = logging.FileHandler('/tmp/test_gbp_1.log')
    _log.setLevel(logging.INFO)
    _log.setLevel(logging.DEBUG)

    def __init__(self):
      """
      Initial Heat-based Config setup 
      """
      self.gbpcfg = Gbp_Config()
      self.gbpverify = Gbp_Verify()
      self.gbpheat = Gbp_Heat('172.28.184.65')
      self.heat_temp_test = 'config_master.yaml' # Assumption the heat temp is co-located with the testcase
      self.heat_temp_shared = 'common.yaml' # Assumption as above
    
    def setup(self):
      """
      Heat Stack Create
      """
      if self.gbpheat.cfg_all_cli(1,'shared_stack',heat_temp=self.heat_temp_shared) == 0:
         self._log.info("\n ABORTING THE TESTSUITE RUN, HEAT STACK CREATE of 'shared_stack' Failed")
         self.gbpheat.cfg_all_cli(0,'shared_stack') ## Stack delete will cause cleanup
      
      if self.gbpheat.cfg_all_cli(1,'test_stack',heat_temp=self.heat_temp_test) == 0:
         self._log.info("\n ABORTING THE TESTSUITE RUN, HEAT STACK CREATE of 'test_stack' Failed")
         self.gbpheat.cfg_all_cli(0,'test_stack')

    def cleanup(self):
        ##Need to call for instance delete if there is an instance
        self.gbpcfg.gbp_heat_cfg_all(0,heat_template,self.heatstack_name) ## Calling stack delete
    
if __name__ == '__main__':
    main()
