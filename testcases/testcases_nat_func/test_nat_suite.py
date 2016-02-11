#!/usr/bin/python

import datetime
import logging
import os
import sys
from time import sleep
from libs.gbp_crud_libs import GBPCrud
from natfuncglobalcfg import GbpNatFuncGlobalCfg
from natfunctestmethod import NatFuncTestMethods

def main():
    suite=NatTestSuite()
    suite.test_runner()

class NatTestSuite(object):
    
    def __init__(self):
        cntlr_ip = '172.28.184.35'
        self.globalcfg = GbpNatFuncGlobalCfg(cntlr_ip)
        self.steps = NatFuncTestMethods(cntlr_ip)
        
    def test_runner(self):
        """
        Method to run the Testcase in Ordered Steps
        """
        # Initiate Global Configuration 
        self.globalcfg.CfgGlobalObjs()
        """
        self._log.info(
            "\nSteps of the TESTCASE_GBP_NAT_FUNC_1 to be executed\n")
        testcase_steps = []
        for step in testcase_steps:  
            try:
                if step() == 0:
                    self._log.error("Test Failed at Step == %s" %
                                   (step.__name__.lstrip('self')))
                    raise TestFailed("%s == FAIL" % (test_name))
            except TestFailed as err:
                self._log.info('\n%s' % (err))
        """
        self.test_nat_func_1()
        self._log.info("%s == PASS" % (test_name))

    def test_nat_func_1(self):
        self.steps.DeleteOrCleanup('cleanup')
        self.steps.testCreateExtSegWithDefault()
        self.steps.testCreateNatPoolAssociateExtSeg()
        self.steps.testCreatePtgDefaultL3p()
        self.steps.testCreateNonDefaultL3pAndL2p()
        self.steps.testCreatePtgWithNonDefaultL3p()
        self.steps.testAssociateExtSegToBothL3ps()
        self.steps.testCreatePolicyTargetForEachPtg()
        self.steps.testCreateExternalPolicy()
        for ptgtype in ['internal','external']:
            self.steps.testApplyRemPrsToPtg(
                                   ptgtype,
                                   self.globalcfg.prsicmptcp
                                   )
if __name__ == "__main__":
    main()
