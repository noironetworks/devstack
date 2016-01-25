#!/usr/bin/env bash

if [ $# -ne 3 ]
then
   echo "Usage: source setup.sh <apic_ip> <apic_username> <apic_pwd>"
else
apic_ip=$1
apic_uname=$2
apic_pwd=$3

# Install Pexpect & Fabric needed for running GBP Automated TestSuite
pip install pexpect
pip install fabric
pip install mailer

# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/root/gbpauto"

# Change Nova-quotas as needed for running TestSuite
sed -i 's/^#quota_instances=.*/quota_instances=-1/' /etc/nova/nova.conf
sed -i 's/^#quota_cores=.*/quota_cores=-1/' /etc/nova/nova.conf
sed -i 's/^#quota_ram=.*/quota_ram=-1/' /etc/nova/nova.conf
sed -i 's/^#scheduler_max_attempts=.*/scheduler_max_attempts=1/' /etc/nova/nova.conf
systemctl restart openstack-nova-api.service
systemctl restart openstack-nova-scheduler.service
source /root/keystonerc_admin
nova quota-show

# Restart Heat-Engine & Heat-API
systemctl restart openstack-heat-engine.service
systemctl restart openstack-heat-api.service

# APIC Route-Reflector
apic route-reflector-create --ssl --no-secure --apic-ip $1 --apic-username $2 --apic-password $3
fi

