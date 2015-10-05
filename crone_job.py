#!/usr/bin/env python
import sys, time
import paramiko
import subprocess
import re
import os
from commands import *
from fabric.api import cd,run,env, hide, get, settings
from fabric.contrib.files import exists
import fabric.network


class CroneJob(object):

    def __init__(self,fab='fab3'):
       self.fab = fab
       print "Going to Start a Crone Job %s" %(self.fab)

    def ReinstallJob(self,nauto='172.28.184.8',username='noiro',pwd='noir0123'):
        """
        Reinstall Fabric & Ostack
        """
        env.host_string = nauto
        env.user = username
        env.password = pwd
        with cd ("~/nauto"):
           run("source ~/venv/bin/activate")
           run("python reimage_fabric.py -f %s" %(self.fab))
           run("python ostack_reinstall.py -e sunguard -f %s" %(self.fab))

    def UpdatePkg(self,node_ip,node_type):
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
               print "Yum Update of the Pkg %s on the %s Node %s" %(pkg,node_type,node_ip)
               run("yum update -y %s" %(pkg))
           for service in restart_services:
               print "Restarting the Service %s on the %s Node %s" %(service,node_type,node_ip) 
               run("systemctl restart %s" %(service))
        
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
   for node_type,node_ip in node_ip_type.iteritems():
       job.UpdatePkg(node_ip,node_type)

if __name__ == '__main__':
     main()

