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
    #suite.test_runner()

class NatTestSuite(object):
    
    def __init__(self,cfgfile):
        with open(cfgfile, 'rt') as f:
            conf = yaml.load(f)
        self.cntlr_ip = conf['controller_ip']
        self.extrtr = conf['ext_rtr']
        self.globalcfg = GbpNatFuncGlobalCfg(self.cntlr_ip)
        self.steps = NatFuncTestMethods(self.cntlr_ip)
        self.fipsubnet = self.steps.natippool
        print "FIP Subnet", self.fipsubnet
        forexttraff = Gbp_def_traff()
        print 'When Adding Route'
        forexttraff.add_route_in_extrtr('172.28.184.38','55.55.55.0/24','1.102.1.254',action='update')
        PauseToDebug()
        print 'When Updating Route'
        forexttraff.add_route_in_extrtr('172.28.184.38','55.55.55.0/24','1.102.2.254',action='update')

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
        test_list = [self.test_nat_func_5]
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

    def test_nat_func_5(self):
        """
        Testcase-5 in NAT Functionality
        """
        self.steps._log.info(
              "\nExecution of Testcase TEST_NAT_FUNC_5 starts")
        if self.steps.testCreateExtSegWithDefault('Management-Out') == 0:
           return 0
        if self.steps.testCreatePtgDefaultL3p() == 0:
           return 0
        if self.steps.testCreateNonDefaultL3pAndL2p() == 0:
           return 0
        if self.steps.testCreatePtgWithNonDefaultL3p() == 0:
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
        if self.steps.testLaunchVmsForEachPt() == 0:
           return 0
        print "Sleeping for VM to come up ..."
        sleep(10)
        if self.steps.testAssociateExtSegToBothL3ps() == 0:
           return 0
        if self.steps.testCreateNatPoolAssociateExtSeg() == 0:
           return 0
        if self.steps.testAssociateFipToVMs() == 0:
           return 0
        self.PauseToDebug()
        if self.steps.testTrafficFromExtRtrToVmFip(self.extrtr) == 0:
           return 0
        if self.steps.testDisassociateFipFromVMs(release_fip=1) == 0:
           return 0
        DcExtsegid = self.steps.testCreateExtSegWithDefault(extsegname='Datacenter-Out')
        if DcExtsegid == 0:
           return 0
        print 'DcExtSegID ==',DcExtsegid
        if self.steps.testAssociateExtSegToBothL3ps(extsegid=DcExtsegid) == 0:
           return 0
        if self.steps.testUpdateNatPoolAssociateExtSeg(DcExtsegid) == 0:
           return 0
        if self.steps.testAssociateFipToVMs(ExtSegName='Datacenter-Out') == 0:
           return 0
        print 'Sleeping after new NAT Pool Change'
        if self.steps.testCreateUpdateExternalPolicy(update=1,updextseg=DcExtsegid) == 0:
           return 0
        self.PauseToDebug()
        if self.steps.testTrafficFromExtRtrToVmFip(self.extrtr) == 0:
           return 0
        if self.steps.testDisassociateFipFromVMs() == 0:
           return 0
        self.steps.DeleteOrCleanup('cleanup')

if __name__ == "__main__":
    main()

