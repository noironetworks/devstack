#!/usr/bin/env bash

# Prior to running this script check the following:
#  Set the name and path of the keystone_admin file in external-connectivity.conf OPENSTACK_ENV_FILE var

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

# Create Neutron External Networks (as Admin tenant)

SM_NET1_ID=$(neutron net-create --provider:physical_network=physnet1 --provider:network_type=vlan --provider:segmentation_id=$SM_vlan --router:external=true --shared $INFRA_EXTERNAL_NETWORK_NAME | grep ' id ' | awk '{print $4}')

SM_SUBNET1_ID=$(neutron subnet-create --ip_version 4 --gateway $SM_gateway --name services-mgmt-subnet1 --allocation-pool start=$SM_pool_start,end=$SM_pool_end $SM_NET1_ID $SM_subnet | grep ' id ' | awk '{print $4}')

#Create GBP Resources for service management (as admin Tenant)

gbp external-segment-create --ip-version 4 --external-route destination=0.0.0.0/0,nexthop=$SM_gateway --shared True --subnet_id=$SM_SUBNET1_ID --cidr $SM_subnet service-mgmt

gbp policy-action-create --action-type allow allowmanagement_action
gbp policy-classifier-create --protocol tcp --port-range 22 --direction in sshinclassifier
gbp policy-classifier-create --protocol tcp --direction bi tcpbiclassifier
gbp policy-classifier-create --protocol icmp --direction bi icmpbiclassifier
gbp policy-rule-create --classifier icmpbiclassifier --actions allowmanagement_action allowicmprule
gbp policy-rule-create --classifier sshinclassifier --actions allowmanagement_action allow_ssh_in_rule
gbp policy-rule-create --classifier tcpbiclassifier --actions allowmanagement_action allow_tcp_bi_rule
gbp policy-rule-set-create --policy-rules "allow_tcp_bi_rule allowicmprule" ALLOW-ALL-INBOUND
gbp policy-rule-set-create --policy-rules "allow_tcp_bi_rule allowicmprule" ALLOW-ALL-OUTBOUND

gbp external-policy-create --external-segments service-mgmt --consumed-policy-rule-sets ALLOW-ALL-INBOUND=None --provided-policy-rule-sets ALLOW-ALL-OUTBOUND=None service_management_external_policy
gbp l3policy-create --external-segment "service-mgmt=" service_management_l3policy
gbp l2policy-create --l3-policy service_management_l3policy service_management_l2p
gbp group-create --provided-policy-rule-sets ALLOW-ALL-INBOUND=None --consumed-policy-rule-sets ALLOW-ALL-OUTBOUND=None --l2-policy service_management_l2p svc_management_ptg

echo "*********************************************************************"
echo "SUCCESS: End $0"
echo "*********************************************************************"
