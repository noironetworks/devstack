#!/usr/bin/python

import datetime
import logging
import os
import sys
from time import sleep
from libs.gbp_crud_libs import GBPCrud
from natfuncglobalcfg import GbpNatFuncGlobalCfg
from natfunctestmethod import NatFuncTestMethods

class NatTestSuite(object):
    
    def __init__(self):
        cntlr_ip = '172.28.184.35'
        self.globalcfg = GbpNatFuncGlobalCfg(cntlr_ip)
        self.setps = natfunctestmethod(cntlr_ip)
        
    def test_runner(self):
        """
        Method to run the Testcase in Ordered Steps
        """
        # Initiate Global Configuration 
        self.globalcfg.CfgGlobalObjs()
        self._log.info(
            "\nSteps of the TESTCASE_GBP_NAT_FUNC_1 to be executed\n")
        testcase_steps = []
        for step in testcase_steps:  # TODO: Needs FIX
            try:
                if step() == 0:
                    self._log.error("Test Failed at Step == %s" %
                                   (step.__name__.lstrip('self')))
                    raise TestFailed("%s == FAIL" % (test_name))
            except TestFailed as err:
                self._log.info('\n%s' % (err))
        self._log.info("%s == PASS" % (test_name))

    def test_nat_func_1(self):
        self.setps.testCreateExtSegWithDefault()
        self.setps.testCreateNatPoolAssociateExtSeg()
        self.setps.testCreatePtgDefaultL3p()
        self.setps.testCreateNonDefaultL3pAndL2p()
        self.setps.testCreatePtgWithNonDefaultL3p()
        self.setps.testAssociateExtSegToBothL3ps()
        self.steps.testCreatePolicyTargetForEachPtg()
        self.steps.testCreateExternalPolicy()
        self.steps.
