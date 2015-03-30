#!/usr/bin/env python
import os,sys,optparse,platform
from commands import *
from testcases.test_main_config import gbp_main_config
from testcases.test_gbp_dp_setup_cleanup import header1,header2,header3,header4

hdr_dict = {'same_ptg_l2_l3p': header1, 'diff_ptg_same_l2p_l3p': header2,
            'diff_ptg_diff_l2p_same_l3p': header3, 'diff_ptg_l2p_l3p': header4}



def main():
    usage = "usage: suite_run.py [options]"
    parser = optparse.OptionParser(usage=usage)
    helpstr = "Valid values are 'func' OR 'aciint' OR 'dp'"
    parser.add_option('-s', '--suite', help='%s' %(helpstr),dest='suite')
    (opts, args) = parser.parse_args()
    if opts.suite == None:
       print 'Suite value needs to be passed'
       parser.print_help()
       sys.exit(1)
    if opts.suite == 'func':
      fname = run_func_neg()
      num_lines = sum(1 for line in open(fname))
      print "\nNumber of Functional Test Scripts to execute = %s" %(num_lines)
      with open(fname) as f:
        for i,l in enumerate(f,1):
            print "Functional Test Script to execute now == %s" %(l)
            # Assumption: test-scripts are executable from any location
            cmd='%s' %(l.strip()) # Reading the line from text file, also reads trailing \n, hence we need to strip
            print cmd
            out=getoutput(cmd)
      f = open("test_results.txt")
      contents = f.read()
      f.close()
      print contents
      print "\n\nTotal Number of TestCases Executed= %s" %(contents.count("TESTCASE_GBP_"))
      print "\n\nNumber of TestCases Passed= %s" %(contents.count("PASSED"))
      print "\n\nNumber of TestCases Failed= %s" %(contents.count("FAILED"))
      
if __name__ == "__main__":
    main()

