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
        test_list = [self.test_nat_func_1,
                     self.test_nat_func_2,
                     self.test_nat_func_3,
		     self.test_nat_func_4,
		     self.test_nat_func_5,
		     self.test_nat_func_6,
		     self.test_nat_func_7,
		     self.test_nat_func_8,
		     self.test_nat_func_9,
		     self.test_nat_func_10,
		     self.test_nat_func_11,
		     self.test_nat_func_12,
		     self.test_nat_func_13,
		     self.test_nat_func_14,
		     self.test_nat_func_15,
		     self.test_nat_func_16,
                     self.test_nat_func_17
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

    def test_nat_func_1(self):
        """
        Testcase-1 in NAT Functionality
        """
        self.steps._log.info(
              "\nExecution of Testcase TEST_NAT_FUNC_1 starts")
        if self.steps.testCreateExtSegWithDefault() == 0:
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
        if self.steps.testLaunchVmsForEachPt() == 0:
           return 0
        print "Sleeping for VM to come up ..."
        sleep(10)
        if self.steps.testAssociateFipToVMs() == 0:
           return 0
        sleep(10)
        self.forextrtr.add_route_in_extrtr(
                                          self.extrtr,
                                          self.fipsubnet1,
                                          self.gwip1_extrtr,
                                          action='update'
                                          )
        if self.steps.testTrafficFromExtRtrToVmFip(self.extrtr) == 0:
           return 0
        if self.steps.testDisassociateFipFromVMs() == 0:
           return 0
        self.steps.DeleteOrCleanup('cleanup')

       
    def test_nat_func_2(self):
        """
        Testcase-2 in NAT Functionality
        """
        self.steps._log.info(
              "\nExecution of Testcase TEST_NAT_FUNC_2 starts")
        if self.steps.testCreateExtSegWithDefault() == 0:
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
        if self.steps.testLaunchVmsForEachPt() == 0:
           return 0
        print "Sleeping for VM to come up ..."
        sleep(10)
        if self.steps.testCreateNatPoolAssociateExtSeg() == 0:
           return 0
        if self.steps.testAssociateFipToVMs() == 0:
           return 0
        sleep(10)
        self.forextrtr.add_route_in_extrtr(
                                          self.extrtr,
                                          self.fipsubnet1,
                                          self.gwip1_extrtr,
                                          action='update'
                                          )
        if self.steps.testTrafficFromExtRtrToVmFip(self.extrtr) == 0:
           return 0
        if self.steps.testDisassociateFipFromVMs() == 0:
           return 0
        self.steps.DeleteOrCleanup('cleanup')

    def test_nat_func_3(self):
        """
        Testcase-3 in NAT Functionality
        """
        self.steps._log.info(
              "\nExecution of Testcase TEST_NAT_FUNC_3 starts")
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
        if self.steps.testCreateExtSegWithDefault() == 0:
           return 0
        if self.steps.testAssociateExtSegToBothL3ps() == 0:
           return 0
        if self.steps.testCreateNatPoolAssociateExtSeg() == 0:
           return 0
        if self.steps.testAssociateFipToVMs() == 0:
           return 0
        sleep(10)
        self.forextrtr.add_route_in_extrtr(
                                          self.extrtr,
                                          self.fipsubnet1,
                                          self.gwip1_extrtr,
                                          action='update'
                                          )
        if self.steps.testTrafficFromExtRtrToVmFip(self.extrtr) == 0:
           return 0
        if self.steps.testDisassociateFipFromVMs() == 0:
           return 0
        self.steps.DeleteOrCleanup('cleanup')


    def test_nat_func_4(self):
        """
        Testcase-4 in NAT Functionality
        """
        self.steps._log.info(
              "\nExecution of Testcase TEST_NAT_FUNC_4 starts")
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
        if self.steps.testCreateExtSegWithDefault() == 0:
           return 0
        if self.steps.testCreateNatPoolAssociateExtSeg() == 0:
           return 0
        if self.steps.testAssociateFipToVMs() == 0:
           return 0
        if self.steps.testAssociateExtSegToBothL3ps() == 0:
           return 0
        sleep(10)
        self.forextrtr.add_route_in_extrtr(
                                          self.extrtr,
                                          self.fipsubnet1,
                                          self.gwip1_extrtr,
                                          action='update'
                                          )
        if self.steps.testTrafficFromExtRtrToVmFip(self.extrtr) == 0:
           return 0
        if self.steps.testDisassociateFipFromVMs() == 0:
           return 0
        self.steps.DeleteOrCleanup('cleanup')

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
        sleep(10)
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
        sleep(10)
        if self.steps.testCreateUpdateExternalPolicy(update=1,updextseg=DcExtsegid) == 0:
           return 0
        self.forextrtr.add_route_in_extrtr(
                                          self.extrtr,
                                          self.fipsubnet1,
                                          self.gwip2_extrtr,
                                          action='update'
                                          )
        if self.steps.testTrafficFromExtRtrToVmFip(self.extrtr) == 0:
           return 0
        if self.steps.testDisassociateFipFromVMs() == 0:
           return 0
        self.steps.DeleteOrCleanup('cleanup')

    def test_nat_func_6(self):
        """
        Testcase in NAT Functionality
        """
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
        sleep(10)
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
        if self.steps.testCreateNatPoolAssociateExtSeg(
                                   poolname=self.natpoolname,
                                   natpool=self.fipsubnet2
                                   ) == 0:
           return 0
        if self.steps.testAssociateFipToVMs() == 0:
           return 0
        sleep(10)
        self.forextrtr.add_route_in_extrtr(
                                          self.extrtr,
                                          self.fipsubnet2,
                                          self.gwip1_extrtr,
                                          action='update'
                                          )
        if self.steps.testDisassociateFipFromVMs() == 0:
           return 0
        self.steps.DeleteOrCleanup('cleanup')

    def test_nat_func_7(self):
        """
        Testcase in NAT Functionality
        """
        self.steps.DeleteOrCleanup('cleanup')
        if self.steps.testCreateExtSegWithDefault() == 0:
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
        if testVerifyCfgdObjects == 0:
           return 0
        if testLaunchVmsForEachPt() == 0:
           return 0
        sleep(60)
        if testAssociateFipToVMs() == 0:
           return 0
        if testTrafficFromExtRtrToVmFip == 0:
           return 0

    def test_nat_func_8(self):
        """
        Testcase in NAT Functionality
        """
        self.steps.DeleteOrCleanup('cleanup')
        if self.steps.testCreateExtSegWithDefault() == 0:
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
        if testVerifyCfgdObjects == 0:
           return 0
        if testLaunchVmsForEachPt() == 0:
           return 0
        sleep(60)
        if testAssociateFipToVMs() == 0:
           return 0
        if testTrafficFromExtRtrToVmFip == 0:
           return 0

    def test_nat_func_9(self):
        """
        Testcase in NAT Functionality
        """
        self.steps.DeleteOrCleanup('cleanup')
        if self.steps.testCreateExtSegWithDefault() == 0:
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
        if testVerifyCfgdObjects == 0:
           return 0
        if testLaunchVmsForEachPt() == 0:
           return 0
        sleep(60)
        if testAssociateFipToVMs() == 0:
           return 0
        if testTrafficFromExtRtrToVmFip == 0:
           return 0

    def test_nat_func_10(self):
        """
        Testcase in NAT Functionality
        """
        self.steps.DeleteOrCleanup('cleanup')
        if self.steps.testCreateExtSegWithDefault() == 0:
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
        if testVerifyCfgdObjects == 0:
           return 0
        if testLaunchVmsForEachPt() == 0:
           return 0
        sleep(60)
        if testAssociateFipToVMs() == 0:
           return 0
        if testTrafficFromExtRtrToVmFip == 0:
           return 0

    def test_nat_func_11(self):
        """
        Testcase in NAT Functionality
        """
        self.steps.DeleteOrCleanup('cleanup')
        if self.steps.testCreateExtSegWithDefault() == 0:
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
        if testVerifyCfgdObjects == 0:
           return 0
        if testLaunchVmsForEachPt() == 0:
           return 0
        sleep(60)
        if testAssociateFipToVMs() == 0:
           return 0
        if testTrafficFromExtRtrToVmFip == 0:
           return 0

    def test_nat_func_12(self):
        """
        Testcase in NAT Functionality
        """
        self.steps.DeleteOrCleanup('cleanup')
        if self.steps.testCreateExtSegWithDefault() == 0:
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
        if testVerifyCfgdObjects == 0:
           return 0
        if testLaunchVmsForEachPt() == 0:
           return 0
        sleep(60)
        if testAssociateFipToVMs() == 0:
           return 0
        if testTrafficFromExtRtrToVmFip == 0:
           return 0

    def test_nat_func_13(self):
        """
        Testcase in NAT Functionality
        """
        self.steps.DeleteOrCleanup('cleanup')
        if self.steps.testCreateExtSegWithDefault() == 0:
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
        if testVerifyCfgdObjects == 0:
           return 0
        if testLaunchVmsForEachPt() == 0:
           return 0
        sleep(60)
        if testAssociateFipToVMs() == 0:
           return 0
        if testTrafficFromExtRtrToVmFip == 0:
           return 0

    def test_nat_func_14(self):
        """
        Testcase in NAT Functionality
        """
        self.steps.DeleteOrCleanup('cleanup')
        if self.steps.testCreateExtSegWithDefault() == 0:
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
        if testVerifyCfgdObjects == 0:
           return 0
        if testLaunchVmsForEachPt() == 0:
           return 0
        sleep(60)
        if testAssociateFipToVMs() == 0:
           return 0
        if testTrafficFromExtRtrToVmFip == 0:
           return 0

    def test_nat_func_15(self):
        """
        Testcase in NAT Functionality
        """
        self.steps.DeleteOrCleanup('cleanup')
        if self.steps.testCreateExtSegWithDefault() == 0:
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
        if testVerifyCfgdObjects == 0:
           return 0
        if testLaunchVmsForEachPt() == 0:
           return 0
        sleep(60)
        if testAssociateFipToVMs() == 0:
           return 0
        if testTrafficFromExtRtrToVmFip == 0:
           return 0

    def test_nat_func_16(self):
        """
        Testcase in NAT Functionality
        """
        self.steps.DeleteOrCleanup('cleanup')
        if self.steps.testCreateExtSegWithDefault() == 0:
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
        if testVerifyCfgdObjects == 0:
           return 0
        if testLaunchVmsForEachPt() == 0:
           return 0
        sleep(60)
        if testAssociateFipToVMs() == 0:
           return 0
        if testTrafficFromExtRtrToVmFip == 0:
           return 0

    def test_nat_func_17(self):
        """
        Testcase in NAT Functionality
        """
        self.steps.DeleteOrCleanup('cleanup')
        if self.steps.testCreateExtSegWithDefault() == 0:
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
        if testVerifyCfgdObjects == 0:
           return 0
        if testLaunchVmsForEachPt() == 0:
           return 0
        sleep(60)
        if testAssociateFipToVMs() == 0:
           return 0
        if testTrafficFromExtRtrToVmFip == 0:
           return 0

         
if __name__ == "__main__":
    main()
