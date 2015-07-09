#!/usr/bin/env python

import sys
import logging
import os
import datetime
import re
from commands import *
try:
   import fabric
except Exception as e:
   print 'Exception on Import = ', e
   getoutput('yum -y install fabric \r')
from fabric.api import cd,run,env, hide, get, settings
from fabric.contrib import files

class Bonding(object):

    # Initialize logging
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=logging.WARNING)
    _log = logging.getLogger( __name__ )
    hdlr = logging.FileHandler('/tmp/test_def_traff.log')
    _log.setLevel(logging.INFO)
    _log.setLevel(logging.DEBUG)
    
    def __init__(self,host_ip,host_user='root',host_pwd='noir0123'):
      """
      Verify all traffic b/w End-points using PTG with NO Contract(Policy RuleSet) 
      """
      self.host_ip = host_ip
      self.user = host_user
      self.pwd = host_pwd

    def add_bond_cfg_to_nic(self,nic_name=[]):
        """
        Add Bonding cfg and related cfg params to NIC's ntk-scripts
        nic_name = pass it as a list of nics which are taking part in bonding
        """
        env.host_string = self.host_ip
        env.user = self.user
        env.pwd = self.pwd
        if nic_name == []:
           print 'ERROR: List of NICs is empty'
           sys.exit(1)
        for nic in nic_name:
            path='/etc/sysconfig/network-scripts/ifcfg-%s' %(nic)
            append_new_cfg_lines = ['MASTER=bond0','SLAVE=yes']
            over_write_cfg_lines = [
                                   "sed -i 's/DEVICE.*/DEVICE=%s/' %s" %(nic,path),
                                   "sed -i 's/BOOTPROTO.*/BOOTPROTO=none/' %s" %(path),
                                   "sed -i 's/ONBOOT.*/ONBOOT=yes/' %s" %(path),
                                   "sed -i 's/NM_CONTROLLED.*/NM_CONTROLLED=no/' %s" %(path)
                                   ]
            for cmd in over_write_cfg_lines:
                run(cmd)
            files.append(path,append_new_cfg_lines)
        
    def if_down_up(self,nic_state='up',nic_name=[]):
        """
        IfUp/Down of the interface
        nic_state = up,down
        """
        env.host_string = self.host_ip
        env.user = self.user
        env.pwd = self.pwd
        if nic_name == []:
           print 'ERROR: List of NICs is empty'
           sys.exit(1)
        for nic in nic_name:
            if nic_state == 'down':
               run('ifdown %s' %(nic))
            if nic_state == 'up':
               run('ifup %s' %(nic))

    def create_bond_intf(self):
        """
        Create bond interface(bond0)
        """
        env.host_string = self.host_ip
        env.user = self.user
        env.pwd = self.pwd
        cfg_lines = [
                     'DEVICE=bond0\n',
                     'ONBOOT=yes\n',
                     'NM_CONTROLLED=no\n',
                     'BOOTPROTO=none\n',
                     'USER_CTL=no\n',
                     'BONDING_OPTS="mode=4"\n'
                     ]
        ifcfg_file=open("ifcfg-bond0","w")
        ifcfg_file.writelines(cfg_lines)       
        ifcfg_file.close()
        files.upload_template("ifcfg-bond0","/etc/sysconfig/network-scripts/")
             
    def get_intf_mac(self,intf):
        """
        Fetch the MAC address of the Interface
        """
        env.host_string = self.host_ip
        env.user = self.user
        env.pwd = self.pwd
        with settings(warn_only=True):
             result = run("ip link show %s" %(intf))
             intf_mac = re.search('link/ether (.*) brd',result,re.I).group(1).upper()
        return intf_mac

    def verify_bond(self,member_list):
        """
        Verify the bond mac is associated to member mac
        member_list = pass a list of names of the member interfaces took part in bonding
        """
        env.host_string = self.host_ip
        env.user = self.user
        env.pwd = self.pwd
        if not isinstance(member_list, list):
           print 'ERROR: List of member interface is empty'
           sys.exit(1)
        with settings(warn_only=True):
             result = run("ip link show bond0")
             if result.find('BROADCAST,MULTICAST,MASTER,UP') < 0:
                print "ERROR: State of Bond interface bond0 is NOT UP"
                #sys.exit(1)
             bond_mac = re.search('link/ether (.*) brd',result,re.I).group(1).upper()
             for mem in member_list:
                 result_mem = run("ip link show %s" %(mem))
                 if result_mem.find('BROADCAST,MULTICAST,SLAVE,UP') < 0:
                    print "ERROR: State of Member interface %s is NOT UP" %(mem)
                    #sys.exit(1)
                 mem_mac = re.search('link/ether (.*) brd',result_mem,re.I).group(1).upper()
                 if mem_mac != bond_mac:
                    print "ERROR: Bond Interface MAC is not logically applied on its member interface %s" %(mem)
                    #sys.exit(1)

    def add_virtual_intf_script(self,hostname,infra_vlan='4093',parent_intf='bond0'):
        """
        Add Virtual Interface script on Parent interface
        Add the Multicast Route Script for the Virtual Interface
        Add the dhclient for the Virtual Interface
        """
        env.host_string = self.host_ip
        env.user = self.user
        env.pwd = self.pwd
        ### Adding interface script
        vif_mac = self.get_intf_mac('bond0')
        vif_name = '%s.%s' %(parent_intf,infra_vlan)
        cfg_lines = [
                     'DEVICE=%s\n' %(vif_name),
                     'ONBOOT=yes\n',
                     'NM_CONTROLLED=no\n',
                     'USER_CTL=no\n',
                     'PERSISTENT_DHCLIENT=1\n',
                     'DHCPRELEASE=1\n'
                     'HWADDR=%s\n' %(vif_mac),
                     'TYPE=Ethernet\n'
                     'BOOTPROTO=dhcp\n',
                     'VLAN=yes\n',
                     'ONPARENT=yes\n'
                     'MTU=1600\n'
                     ]
        ifcfg_file = open("ifcfg-%s" %(vif_name),"w")
        ifcfg_file.writelines(cfg_lines)
        ifcfg_file.close()
        files.upload_template("ifcfg-%s" %(vif_name),"/etc/sysconfig/network-scripts/")
        ### Adding route-script
        rt_cfg_lines = [
                        'ADDRESS0=224.0.0.0\n',
                        'NETMASK0=240.0.0.0\n'
                        'GATEWAY0=0.0.0.0\n'
                        'METRIC0=1000\n'
                    ]
        rtcfg_file = open("route-%s" %(vif_name),"w")
        rtcfg_file.writelines(rt_cfg_lines)
        rtcfg_file.close()
        files.upload_template("route-%s" %(vif_name),"/etc/sysconfig/network-scripts/")
        ### Adding the dhclient config for the Virtual Interface
        dhclient_cfg_lines = [
                              'send dhcp-client-identifier %s;\n' %(vif_mac),
                              'request subnet-mask, domain-name, domain-name-servers, host-name;\n',
                              'send host-name %s;\n' %(hostname),
                              'option rfc3442-classless-static-routes code 121 = array of unsigned integer 8;\n',
                              'option ms-classless-static-routes code 249 = array of unsigned integer 8;\n',
                              'option wpad code 252 = string;\n',
                              'also request rfc3442-classless-static-routes;\n',
                              'also request ms-classless-static-routes;\n',
                              'also request static-routes;\n',
                              'also request wpad;\n',
                              'also request ntp-servers;\n'
                         ]
        dhclient_file = open("dhclient-%s.conf" %(vif_name),"w")
        dhclient_file.writelines(dhclient_cfg_lines)
        dhclient_file.close()
        files.upload_template("dhclient-%s.conf" %(vif_name),"/etc/dhcp/")

    def modify_opflex_conf(self):
        """
        Modify the OpflexAgent Conf file to make VIF as Infra-interface
        Restart the OpflexAgent
        """
        env.host_string = self.host_ip
        env.user = self.user
        env.pwd = self.pwd
        path = '/etc/opflex-agent-ovs/opflex-agent-ovs.conf'
        with settings(warn_only=True):
             result = run("sed -i 's/\"uplink-iface\":.*/\"uplink-iface\": \"%s\",/' %s" %(vif_name,path))
             if result.succeeded:
                restart = run("systemctl restart agent-ovs.service")
                if restart.succeeded:
                   if run("systemctl status agent-ovs.service").find("active (running)") < 0:
                      print 'ERROR: OpflexAgent is NOT ACTIVE on Restart after OpflexAgent Conf change == FAILs'
                      sys.exit(1)
             else:
                print 'ERROR: OpflexAgent Conf Change == FAILs'
                sys.exit(1)

def main():
    """
    Run the complete setup in the below order
    """
    host_ip = sys.argv[1]
    member_intf_list = [sys.argv[2],sys.argv[3]]
    print "User passed == %s, %s" %(host_ip,member_intf_list)

    ##Initialize the BaseClass
    bndg = Bonding(host_ip)

    ## Bringing down Member Interface
    print "Bringing down Member Interface"
    bndg.if_down_up(nic_state='down', nic_name= member_intf_list)
    ## Edit Interface Config Scripts for Member interfaces
    print "Edit Interface Config Scripts for Member interfaces"
    bndg.add_bond_cfg_to_nic(nic_name= member_intf_list)
    ## Add the Bonding Intf Config
    print "Add the Bonding Intf Config"
    bndg.create_bond_intf()
    ## Bring up the interfaces
    print "Bring all three interfaces in order of mem1,mem2, bond0"
    intf_list = [sys.argv[2],sys.argv[3],'bond0']
    print "Interface List for IFUP == %s" %(intf_list)
    #bndg.if_down_up(nic_state='up', nic_name=intf_list)
    ## Verify the Bonding
    print " Verify the LACP Bonding"
    bndg.verify_bond(member_intf_list)
    ## Bring up Virtual Interface on the parent interface bond0
    print "Bring up Virtual Interface on the parent interface bond0"
    bndg.add_virtual_intf_script('f3-compute-1')

if __name__ == "__main__":
   main()
