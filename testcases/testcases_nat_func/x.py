#!/usr/bin/python

import datetime
import logging
import pprint
import string
import sys
import yaml
from time import sleep
from libs.gbp_crud_libs import GBPCrud
from libs.gbp_utils import *
from libs.gbp_fab_traff_libs import Gbp_def_traff
from natfuncglobalcfg import GbpNatFuncGlobalCfg
from natfunctestmethod import NatFuncTestMethods

def main():
    cfgfile = sys.argv[1]
    suite=NatTestSuite(cfgfile)
    suite.test_runner()

class NatTestSuite(object):
    
    def __init__(self,cfgfile):
        with open(cfgfile, 'rt') as f:
            conf = yaml.load(f)
        self.cntlr_ip = conf['controller_ip']
        self.extrtr = conf['ext_rtr']
        self.gwip1_extrtr = conf['gwip1_extrtr']
        self.gwip2_extrtr = conf['gwip2_extrtr']
        self.globalcfg = GbpNatFuncGlobalCfg(self.cntlr_ip)
        self.steps = NatFuncTestMethods(self.cntlr_ip)
        self.natpoolname = self.steps.natpoolname2
        self.fipsubnet1 = self.steps.natippool1
        self.fipsubnet2 = self.steps.natippool2
        self.forextrtr = Gbp_def_traff()
        
    def test_runner(self):
        """
        Method to run the Testcase in Ordered Steps
        """
        # Initiate Blind Cleanup of the testbed config
        self.steps.DeleteOrCleanup('cleanup')
        self.globalcfg.cleanup()
        # Initiate Global Configuration 
        self.globalcfg.CfgGlobalObjs() 
        test_results = {}
        test_list = [
		     #self.test_nat_func_6,
		     self.test_nat_func_7
                     ]
        for test in test_list:
                if test() == 0:
                    test_results[string.upper(test.__name__.lstrip('self.'))] = 'FAIL'
                    self.steps._log.error("\n%s_%s == FAIL" % (
                        self.__class__.__name__.upper(), string.upper(test.__name__.lstrip('self.'))))
                else:
                    test_results[string.upper(test.__name__.lstrip('self.'))] = 'PASS'
                    self.steps._log.info("\n%s_%s == PASS" % (
                        self.__class__.__name__.upper(), string.upper(test.__name__.lstrip('self.'))))
        pprint.pprint(test_results)
        self.globalcfg.cleanup()

    def test_nat_func_6(self):
        """
        Testcase in NAT Functionality
        """
        print " Going to Run TESTCASE -6"
        if self.steps.testCreatePtgDefaultL3p() == 0:
           return 0
        if self.steps.testCreateNonDefaultL3pAndL2p() == 0:
           return 0
        if self.steps.testCreatePtgWithNonDefaultL3p() == 0:
           return 0
        if self.steps.testCreatePolicyTargetForEachPtg() == 0:
           return 0
        if self.steps.testLaunchVmsForEachPt() == 0:
           return 0
        print "Sleeping for VM to come up ..."
        sleep(10)
        if self.steps.testCreateExtSegWithDefault('Management-Out') == 0:
           return 0
        if self.steps.testCreateUpdateExternalPolicy() == 0:
           return 0
        for ptgtype in ['internal','external']:
            if self.steps.testApplyUpdatePrsToPtg(
                                   ptgtype,
                                   self.globalcfg.prsicmptcp
                                   ) == 0:
               return 0
        if self.steps.testVerifyCfgdObjects == 0:
           return 0
        if self.steps.testAssociateExtSegToBothL3ps() == 0:
           return 0
        if self.steps.testCreateNatPoolAssociateExtSeg() == 0:
           return 0
        if self.steps.testAssociateFipToVMs() == 0:
           return 0
        sleep(30)
        self.forextrtr.add_route_in_extrtr(
                                          self.extrtr,
                                          self.fipsubnet1,
                                          self.gwip1_extrtr,
                                          action='update'
                                          )
        if self.steps.testTrafficFromExtRtrToVmFip(self.extrtr) == 0:
           return 0
        if self.steps.testDisassociateFipFromVMs(release_fip=1) == 0:
           return 0
        self.steps.testDeleteNatPool()
        if self.steps.testCreateNatPoolAssociateExtSeg(
                                   poolname=self.natpoolname,
                                   natpool=self.fipsubnet2
                                   ) == 0:
           return 0
        if self.steps.testAssociateFipToVMs() == 0:
           return 0
        sleep(40)
        self.forextrtr.add_route_in_extrtr(
                                          self.extrtr,
                                          self.fipsubnet2,
                                          self.gwip1_extrtr,
                                          action='update'
                                          )
        if self.steps.testTrafficFromExtRtrToVmFip(self.extrtr) == 0:
           return 0

        if self.steps.testDisassociateFipFromVMs() == 0:
           return 0
        self.steps.DeleteOrCleanup('cleanup')

    def test_nat_func_7(self):
        """
        Testcase-7 in NAT Functionality
        """
        print " Going to Run TESTCASE -6"
        if self.steps.testCreateExtSegWithDefault('Management-Out') == 0:
           return 0
        if self.steps.testCreateNatPoolAssociateExtSeg() == 0:
           return 0
        if self.steps.testCreatePtgDefaultL3p() == 0:
           return 0
        if self.steps.testCreateNonDefaultL3pAndL2p() == 0:
           return 0
        if self.steps.testCreatePtgWithNonDefaultL3p() == 0:
           return 0
        if self.steps.testAssociateExtSegToBothL3ps() == 0:
           return 0
        if self.steps.testCreatePolicyTargetForEachPtg() == 0:
           return 0
        if self.steps.testCreateUpdateExternalPolicy() == 0:
           return 0
        for ptgtype in ['internal','external']:
            if self.steps.testApplyUpdatePrsToPtg(
                                   ptgtype,
                                   self.globalcfg.prsicmptcp
                                   ) == 0:
               return 0
        if self.steps.testVerifyCfgdObjects == 0:
           return 0
        if self.steps.testCreateNsp() == 0:
           return 0
        if self.steps.testApplyRemoveNSpFromPtg() == 0:
           return 0
        if self.steps.testLaunchVmsForEachPt() == 0:
           return 0
        print "Sleeping for VM to come up ..."
        sleep(40)
        self.forextrtr.add_route_in_extrtr(
                                          self.extrtr,
                                          self.fipsubnet1,
                                          self.gwip1_extrtr,
                                          action='update'
                                          )
        if self.steps.testTrafficFromExtRtrToVmFip(self.extrtr,vmfips=1) == 0:
           return 0
        if self.steps.testApplyRemoveNSpFromPtg(nspuuid=None) == 0:
           return 0
        sleep(5)
        if self.steps.testAssociateFipToVMs() == 0:
           return 0
        sleep(40)
        if self.steps.testTrafficFromExtRtrToVmFip(self.extrtr) == 0:
           return 0
        if self.steps.testDisassociateFipFromVMs(release_fip=1) == 0:
           return 0

if __name__ == "__main__":
    main()

