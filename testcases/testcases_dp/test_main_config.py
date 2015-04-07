#!/usr/bin/python

import sys
import logging
import os
import datetime
import yaml
from libs.gbp_conf_libs import Gbp_Config
from libs.gbp_verify_libs import Gbp_Verify
from libs.gbp_heat_libs import Gbp_Heat
from libs.gbp_nova_libs import Gbp_Nova

class gbp_main_config(object):
    """
    The intent of this class is to setup the complete GBP config 
    needed for running all DP testcases
    """
    # Initialize logging
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=logging.WARNING)
    _log = logging.getLogger( __name__ )
    hdlr = logging.FileHandler('/tmp/test_gbp_dp_main_config.log')
    _log.setLevel(logging.INFO)
    _log.setLevel(logging.DEBUG)

    def __init__(self,cfg_file):
      """
      Iniatizing the test-cfg variables & classes
      """
      with open(cfg_file,'rt') as f:
           conf = yaml.load(f)
      self.nova_agg = conf['nova_agg_name']
      self.nova_az = conf['nova_az_name']
      self.comp_node = conf['az_comp_node']
      self.cntlr_ip = conf['controller_ip']
      #self.setup_file = conf['main_setup_heat_temp']
      self.heat_temp_test = conf['main_setup_heat_temp']
      self.num_hosts = conf['num_comp_nodes']
      self.heat_stack_name = conf['heat_stack_name']
      self.gbpcfg = Gbp_Config()
      self.gbpverify = Gbp_Verify()
      self.gbpnova = Gbp_Nova(self.cntlr_ip)
      self.gbpheat = Gbp_Heat(self.cntlr_ip)
      # Assumption the heat temp is co-located with the testcase, although find path of template file is implemented below:
      #for root,dirs,files in os.walk("/root"):
      #    for name in files:
      #        if name == self.setup_file:
      #           self.heat_temp_test = os.path.abspath(os.path.join(root, name))
    
    def setup(self):
      """
      Availability Zone creation
      SSH Key creation
      Heat Stack Creates All Test Config
      """
      if self.num_hosts > 1:
         agg_id = self.gbpnova.avail_zone('api','create',self.nova_agg,avail_zone_name=self.nova_az)
         if agg_id == 0:
            self._log.info("\n ABORTING THE TESTSUITE RUN,nova host aggregate creation Failed")
            sys.exit(1)
         self._log.info(" Agg %s" %(agg_id))
         if self.gbpnova.avail_zone('api','addhost',agg_id,hostname=self.comp_node) == 0:
            self._log.info("\n ABORTING THE TESTSUITE RUN, availability zone creation Failed")
            sys.exit(1)

      #if self.gbpnova.sshkey_for_vm() == 0:
      #   self._log.info("\n ABORTING THE TESTSUITE RUN, ssh key creation Failed")
      #   sys.exit(1)

      if self.gbpheat.cfg_all_cli(1,self.heat_stack_name,heat_temp=self.heat_temp_test) == 0:
         self._log.info("\n ABORTING THE TESTSUITE RUN, HEAT STACK CREATE of %s Failed" %(self.heat_stack_name))
         self.gbpheat.cfg_all_cli(0,self.heat_stack_name) ## Stack delete will cause cleanup
         sys.exit(1)

    def cleanup(self):
        ##Need to call for instance delete if there is an instance
        self.gbpheat.cfg_all_cli(0,self.heat_stack_name)
        self.gbpnova.avail_zone('cli','removehost',self.nova_agg,hostname=self.comp_node)
        self.gbpnova.avail_zone('cli','delete',self.nova_agg)
        self.gbpnova.sshkey_for_vm(action='delete')
 
