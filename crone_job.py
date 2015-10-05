#!/usr/bin/env python
import sys
import time
import paramiko
import subprocess
import re
import os
from commands import *
from fabric.api import cd, run, env, hide, get, settings
from fabric.contrib.files import exists
import fabric.network


class CroneJob(object):

    def __init__(self, fab='fab3'):
        self.fab = fab
        print "Going to Start a Crone Job %s" % (self.fab)

    def ReinstallJob(self, nauto='172.28.184.8', username='noiro', pwd='noir0123'):
        """
        Reinstall Fabric & Ostack
        """
        env.host_string = nauto
        env.user = username
        env.password = pwd
        with cd("~/nauto"):
            run("source ~/venv/bin/activate")
            run("python reimage_fabric.py -f %s" % (self.fab))
            run("python ostack_reinstall.py -e sunguard -f %s" % (self.fab))

    def UpdatePkg(self, node_ip, node_type):
        """
        Update the pkgs on Controller & Computes
        ::node_ip -->  IP of Cntlr or Comp-nodes of the Fabric
        ::node_type --> 'controller' or 'compute'
        """
        env.host_string = node_ip
        env.user = 'root'
        env.password = 'noir0123'
        if 'compute' in node_type:
            pkg_list = [
                'neutron-opflex-agent',
                'agent-ovs',
                'libopflex',
                'libmodelgbp',
                'libuv',
                'openvswitch-gbp',
                'openvswitch-gbp-lib',
                'openvswitch-gbp-kmod'
            ]
            restart_services = [
                'neutron-opflex-agent',
                'agent-ovs'
            ]
        if node_type == 'controller':
            pkg_list = [
                'openstack-heat-gbp',
                'python-django-horizon-gbp',
                'openstack-dashboard-gbp',
                'openstack-neutron-gbp',
                'python-gbpclient',
                'neutron-opflex-agent',
                'apicapi',
                'neutron-ml2-driver-apic'
            ]
            restart_services = [
                'openstack-heat-engine.service',
                'openstack-heat-api.service',
                'neutron-server.service'
            ]
        with settings(warn_only=True):
            for pkg in pkg_list:
                print "Yum Update of the Pkg %s on the %s Node %s" % (pkg, node_type, node_ip)
                run("yum update -y %s" % (pkg))
            for service in restart_services:
                print "Restarting the Service %s on the %s Node %s" % (service, node_type, node_ip)
                run("systemctl restart %s" % (service))

    def CloneGitRepo(self, controller):
        """
        Clone the test-repo from the noironetworks
        Run the setup.sh
        """
        env.host_string = controller
        env.user = 'root'
        env.password = 'noir0123'
        with settings(warn_only=True):
            print "Clone the Git repo on the Controller"
            run("git clone https://github.com/noironetworks/devstack -b jishnub/testsuites gbpauto")
            run("source gbpauto/setup.sh")

    def RunRegularDpTests(self, controller):
        """
        Run the DP TestSuite
        """
        env.host_string = controller
        env.user = 'root'
        env.password = 'noir0123'
        cmd_env = 'export PYTHONPATH="${PYTHONPATH}:/root/gbpauto"'
        cmd_src = 'source /root/keystonerc_admin'
        with settings(warn_only=True):
            print 'Export pythonpath'
            run(cmd_env)
            print 'Source Keystone_rc'
            run(cmd_src)
        print "EXECUTING THE REGULAR DATAPATH TESTSUITES"
        with cd("/root/gbpauto/testcases/testcases_dp"):
            run("python test_dp_runner.py testconfig_def.yaml")

    def RunNATDpTests(self, controller):
        """
        Run the NAT DP TestSuite
        """
        env.host_string = controller
        env.user = 'root'
        env.password = 'noir0123'
        cmd_env = 'export PYTHONPATH="${PYTHONPATH}:/root/gbpauto"'
        cmd_src = 'source /root/keystonerc_admin'
        with settings(warn_only=True):
            print 'Export pythonpath'
            run(cmd_env)
            print 'Source Keystone_rc'
            run(cmd_src)
        print "EXECUTING THE NAT DATAPATH TESTSUITES"
        with cd("/root/gbpauto/testcases/testcases_dp_nat/"):
            run("python nat_runner.py natconfigdef.yaml")

    def RunGBPFuncTests(self, controller):
        """
        Run the GBP Functional TestSuites
        """
        env.host_string = controller
        env.user = 'root'
        env.password = 'noir0123'
        cmd_env = 'export PYTHONPATH="${PYTHONPATH}:/root/gbpauto"'
        cmd_src = 'source /root/keystonerc_admin'
        with settings(warn_only=True):
            print 'Export pythonpath'
            run(cmd_env)
            print 'Source Keystone_rc'
            run(cmd_src)
        print "EXECUTING THE GBP FUNCTIONAL TESTSUITES"
        with cd("/root/gbpauto/testcases/testcases_func/"):
            run("python test_func_runner.py")

    def SendTestReportEmail(self):
        """
        Email the TestReport
        """
        env.host_string = controller
        env.user = 'root'
        env.password = 'noir0123'
        cmd_env = 'export PYTHONPATH="${PYTHONPATH}:/root/gbpauto"'
        with settings(warn_only=True):
            run(cmd_env)
            run("python /root/gbpauto/email_report.py")


def main():
    """
    Execute Block 
    """
    job = CroneJob()
    node_ip_type = {
        'controller': '172.28.184.45',
        'compute-1': '172.28.184.46',
        'compute-2': '172.28.184.47'
    }
    # Reinstall the setup
    job.ReinstallJob()

    # Update Pkgs
    for node_type, node_ip in node_ip_type.iteritems():
        job.UpdatePkg(node_ip, node_type)

    # Run the CroneJob to execute Tests in this order
    job.RunGBPFuncTests()
    job.RunRegularDpTests()
    job.RunNATDpTests()

    # Email the TestResport
    job.SendTestReportEmail()

if __name__ == '__main__':
    main()
