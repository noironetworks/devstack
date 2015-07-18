#!/usr/bin/env bash

# Prior to running this script check the following:
# Set the name and path of the keystone_admin file in external-connectivity.conf OPENSTACK_ENV_FILE var
# This uses the classifiers, actions, and rules which are created in the management-external-connectivity.sh script.

source external-connectivity.conf
source functions-common

# This script exits on an error so that errors don't compound and you see
# only the first error that occurred.
set -o errexit

# Settings
# ========

set -o xtrace
source $OPENSTACK_ENV_FILE

if [ -z "$ADMIN_PASSWORD" ]; then
    ADMIN_PASSWORD=$OS_PASSWORD
fi

set_user_password_tenant $ADMIN_USERNAME $ADMIN_PASSWORD $ADMIN_TENANT_NAME

# Create Neutron constructs for Data Network  (as Admin tenant)

INET_NET1_ID=$(neutron net-create --provider:physical_network=$inet_physnet --provider:network_type=vlan --provider:segmentation_id=$inet_vlan --router:external=true --shared $APP_EXTERNAL_NETWORK_NAME | grep ' id ' | awk '{print $4}')

INET_SUBNET1_ID=$(neutron subnet-create --ip_version 4 --gateway $inet_gateway --name cust-inet-subnet1 --allocation-pool start=$inet_pool_start,end=$inet_pool_end $INET_NET1_ID $inet_subnet | grep ' id ' | awk '{print $4}')


#Create GBP Resources for Data Network

gbp external-segment-create --ip-version 4 --external-route destination=0.0.0.0/0,nexthop=$inet_gateway --shared True --subnet_id=$INET_SUBNET1_ID --cidr $inet_subnet cust-inet-ext-segment
gbp nat-pool-create --ip-pool $inet_subnet --external-segment cust-inet-ext-segment --shared True cust-inet-nat-pool

#Create GBP contracts to be used for Data Network connectivity

set_user_password_tenant $NON_ADMIN_USERNAME $ADMIN_PASSWORD $ADMIN_TENANT_NAME

gbp policy-rule-set-create --policy-rules "allow_tcp_bi_rule allowicmprule" ALLOW-ALL-CUST-INET-INBOUND
gbp policy-rule-set-create --policy-rules "allow_tcp_bi_rule allowicmprule" ALLOW-ALL-CUST-INET-OUTBOUND

gbp external-policy-create --external-segments cust-inet-ext-segment --consumed-policy-rule-sets ALLOW-ALL-CUST-INET-INBOUND=None --provided-policy-rule-sets ALLOW-ALL-CUST-INET-OUTBOUND=None cust_inet_external_policy
gbp l3policy-create --external-segment "cust-inet-ext-segment=" cust_inet_l3policy
gbp l2policy-create --l3-policy cust_inet_l3policy cust_inet_l2policy
gbp group-create --provided-policy-rule-sets ALLOW-ALL-CUST-INET-INBOUND=None --consumed-policy-rule-sets ALLOW-ALL-CUST-INET-OUTBOUND=None --l2-policy cust_inet_l2policy cust_inet_ptg

echo "*********************************************************************"
echo "SUCCESS: End $0"
echo "*********************************************************************"
