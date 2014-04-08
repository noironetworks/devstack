#!/bin/bash
#
# Install icehouse devstack with APIC ML2 driver for neutron
#

# Usage:
set -e
USAGE="$0 <apic-ip-addr>"

# Parameters
HOST_IP_ADDR=`ifconfig eth0 | tr : ' ' | awk '/inet\ / {print $3}'`
APIC_IP_ADDR=$1
APIC_PORT='80'
APIC_CONFIG='/etc/neutron/plugins/ml2/ml2_cisco_conf.ini'
DEVSTACK_REPO='http://github.com/noironetworks/devstack.git'
DEVSTACK_BRANCH='cisco-apic-icehouse'

# Validate args
if [ "${APIC_IP_ADDR}"x = ""x ] ; then
    echo "ERROR: APIC_IP_ADDR not specified." 1>&2
    echo "USAGE: ${USAGE}" 2>&1
    exit 2
fi

# Validate preconditions
if [ ! -f /etc/lsb-release ] ; then
    echo "ERROR: This script is only supported on ubuntu" 1>&2
    exit 1
fi
eval `cat /etc/lsb-release`
if [ "${DISTRIB_RELEASE}"x != "12.04"x ] ; then
    echo "ERROR: This script is only supported on ubuntu 12.04" 1>&2
    exit 1
fi
if [ -d /opt/stack/devstack ] ; then
    echo "ERROR: devstack already exists" 1>&2
    exit 1
fi

# install git
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install python-all-dev python-pip git

# Create user 'stack' if one already does not exist, and
#  - set same ssh privilages as current user
#  - add to sudoers
sudo egrep '^stack:' /etc/group 1>/dev/null || \
    sudo groupadd stack
sudo egrep '^stack:' /etc/passwd 1>/dev/null || (
  sudo useradd -g stack -s /bin/bash -d /opt/stack -m stack
  sudo cp -r ${HOME}/.ssh /opt/stack/.ssh
  sudo chown -R stack.stack /opt/stack/.ssh
)
sudo egrep 'stack\ ALL' /etc/sudoers 1>/dev/null || \
    echo "stack ALL=(ALL) NOPASSWD: ALL" | sudo tee -a /etc/sudoers 1>/dev/null

# Install devstack, always download the repo again
sudo chmod a+w /opt/stack
git clone -b ${DEVSTACK_BRANCH} ${DEVSTACK_REPO} /opt/stack/devstack

# create sample local.conf files
cat >/opt/stack/devstack/local.conf.ctrl-node <<EOF
[[local|localrc]]
ENABLED_SERVICES=g-api,g-reg,key,n-api,n-crt,n-obj,n-cpu,n-cond,n-sch,n-novnc,n-cauth,horizon,rabbit,neutron,q-svc,q-agt,q-dhcp,quantum,mysql,q-meta,q-lbaas

MULTI_HOST=1
HOST_IP=${HOST_IP_ADDR}

ENABLE_TENANT_VLANS=True
PHYSICAL_NETWORK=physnet1
OVS_PHYSICAL_BRIDGE=br-eth1

Q_PLUGIN=ml2
Q_ML2_PLUGIN_MECHANISM_DRIVERS=openvswitch,cisco_apic
Q_PLUGIN_EXTRA_CONF_FILES=( "ml2_conf_cisco.ini" )
Q_PLUGIN_EXTRA_CONF_PATH="etc/neutron/plugins/ml2"
Q_ML2_TENANT_NETWORK_TYPE=vlan
Q_ML2_PLUGIN_TYPE_DRIVERS=local,vlan,vxlan,gre
ML2_VLAN_RANGES=physnet1:100:200

ADMIN_PASSWORD=nova
MYSQL_PASSWORD=supersecret
RABBIT_PASSWORD=supersecret
SERVICE_PASSWORD=supersecret
SERVICE_TOKEN=xyzlazydog

LOGFILE=/opt/stack/logs/stack.sh.log
SCREEN_LOGDIR=/opt/stack/logs
#VERBOSE=True
#DEBUG=True
#OFFLINE=True
EOF

cat >/opt/stack/devstack/local.conf.compute-node <<EOF
[[local|localrc]]
ENABLED_SERVICES=n-cpu,q-agt,rabbit,neutron,nova

MULTI_HOST=1
HOST_IP=${HOST_IP_ADDR}

SERVICE_HOST=10.1.1.1
DATABASE_TYPE=mysql
MYSQL_HOST=$SERVICE_HOST
RABBIT_HOST=$SERVICE_HOST
GLANCE_HOSTPORT=${SERVICE_HOST}:9292
Q_HOST=$SERVICE_HOST

ENABLE_TENANT_VLANS=True
PHYSICAL_NETWORK=physnet1
OVS_PHYSICAL_BRIDGE=br-eth1

ADMIN_PASSWORD=nova
MYSQL_PASSWORD=supersecret
RABBIT_PASSWORD=supersecret
SERVICE_PASSWORD=supersecret
SERVICE_TOKEN=xyzlazydog

LOGFILE=/opt/stack/logs/stack.sh.log
SCREEN_LOGDIR=/opt/stack/logs
#VERBOSE=True
#DEBUG=True
#OFFLINE=True
EOF
cp /opt/stack/devstack/local.conf.ctrl-node /opt/stack/devstack/local.conf
sudo chmod go-w /opt/stack
sudo chown -R stack.stack /opt/stack

# Update config in /etc
sudo mkdir -p /etc/neutron/plugins/ml2
sudo tee /etc/neutron/plugins/ml2/ml2_conf_cisco.ini 1>/dev/null <<EOF
[ml2_cisco_apic]

# Hostname for the APIC controller
apic_host=${APIC_IP_ADDR}

# Username for the APIC controller
apic_username=admin

# Password for the APIC controller
apic_password=password

# Port for the APIC Controller
apic_port=80

# Default names in APIC policies
apic_vmm_provider=VMware
apic_vmm_domain=openstack
apic_vlan_ns_name=openstack_ns
apic_node_profile=openstack_profile
apic_entity_profile=openstack_entity
apic_function_profile=openstack_function
apic_clear_node_profiles=True

[apic_switch:17]
compute01=1/17

[apic_switch:18]
compute02=1/17
EOF
sudo chown -R stack.stack /etc/neutron

# Done
echo "$0 Done."
echo "Login as user 'stack'"
echo "  Based on your config update:"
echo "    ~/devstack/local.conf"
echo "    /etc/neutron/plugins/ml2/ml2_conf_cisco.ini"
echo "  "
echo "  Then run devstack as:"
echo "    cd ~/${DEVSTACK_DIR}; ./stack.sh"
echo "  "
