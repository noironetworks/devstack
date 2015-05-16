#!/usr/bin/env bash

# **demo.sh**
# Prior to running this script check the following:
# 1. Set the name and path of the keystone_admin file in demo.conf OPENSTACK_ENV_FILE var
# Usage:
# ./demo neutron


source demo.conf
source functions-common

# Process args
RENDERING_MODE=$1
if [ "${RENDERING_MODE}"x = ""x ] ; then
    echo "USAGE: $USAGE" 2>&1
    echo "  >  No rendering mode specified." 1>&2
    exit 1
fi

echo "*********************************************************************"
echo "GBP demo: $1 rendering"
echo "*********************************************************************"

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
if [ -z "$NON_ADMIN_PASSWORD" ]; then
    NON_ADMIN_PASSWORD=$OS_PASSWORD
fi

set_user_password_tenant $ADMIN_USERNAME $ADMIN_PASSWORD $ADMIN_TENANT_NAME

heat stack-create -f "$CONTRACTS_YAML" "$CONTRACTS_STACK" -P "app_to_outside_rule_set_name=$APP_TO_OUTSIDE_RULE_SET_NAME;app_rule_set_name=$APP_RULE_SET_NAME;http_rule_set_name=$HTTP_RULE_SET_NAME;web_tier_consumed_prs_name=$WEB_TIER_CONSUMED_PRS_NAME;web_tier_provided_prs_name=$WEB_TIER_PROVIDED_PRS_NAME"

confirm_resource_created "heat stack-show" "$CONTRACTS_STACK" "CREATE_COMPLETE"
VIP_IP_POLICY_ID=`heat output-show "$CONTRACTS_STACK" "vip_ip_policy_id" | sed "s/\"//g"`
HTTP_RULE_SET_ID=`heat output-show "$CONTRACTS_STACK" "http_rule_set_id" | sed "s/\"//g"`
HTTP_WITH_LB_REDIRECT_RULE_SET_ID=`heat output-show "$CONTRACTS_STACK" "http_with_lb_redirect_rule_set_id" | sed "s/\"//g"`
APP_RULE_SET_ID=`heat output-show "$CONTRACTS_STACK" "app_rule_set_id" | sed "s/\"//g"`
APP_TO_OUTSIDE_RULE_SET_ID=`heat output-show "$CONTRACTS_STACK" "app_to_outside_rule_set_id" | sed "s/\"//g"`

heat stack-create -f "$ADMIN_YAML" "$ADMIN_STACK" -P "external_network_name=$EXT_NETWORK_NAME;external_subnet_name=$EXT_SUBNET_NAME;external_network_cidr=$EXT_NET_CIDR;external_network_gateway=$EXT_NET_GATEWAY;external_subnet_allocation_pool_start=$EXT_SUBNET_ALLOCATION_POOL_START;external_subnet_allocation_pool_end=$EXT_SUBNET_ALLOCATION_POOL_END;infra_external_policy_name=$INFRA_EXTERNAL_POLICY_NAME;port_address_translation=$PORT_ADDRESS_TRANSLATION;infra_ip_pool=$INFRA_IP_POOL;web_access_prs_id=$HTTP_RULE_SET_ID;app_to_outside_rule_set_id=$APP_TO_OUTSIDE_RULE_SET_ID;app_rule_set_id=$APP_RULE_SET_ID;web_tier_consumed_prs_id=$APP_TO_OUTSIDE_RULE_SET_ID;web_tier_provided_prs_id=$HTTP_WITH_LB_REDIRECT_RULE_SET_ID;service_management_ptg_name=$SERVICE_MANAGEMENT_PTG_NAME;svc_mgmt_vm_image=$SVC_MGMT_VM_IMAGE_NAME;svc_mgmt_vm_flavor=$SVC_MGMT_VM_FLAVOR;infra_l3_policy_name=$INFRA_L3_POLICY_NAME"

confirm_resource_created "heat stack-show" "$ADMIN_STACK" "CREATE_COMPLETE"
SVC_MGMT_PTG_ID=`heat output-show "$ADMIN_STACK" "svc_mgmt_ptg_id" | sed "s/\"//g"`
INFRA_EXTERNAL_SEGMENT_ID=`heat output-show "$ADMIN_STACK" "infra_external_segment_id" | sed "s/\"//g"`
INFRA_EXTERNAL_POLICY_ID=`heat output-show "$ADMIN_STACK" "infra_external_policy_id" | sed "s/\"//g"`
INFRA_L3_POLICY_ID=`heat output-show "$ADMIN_STACK" "infra_l3_policy_id" | sed "s/\"//g"`

gbp external-policy-update $INFRA_EXTERNAL_POLICY_ID --external-segments "$INFRA_EXTERNAL_SEGMENT_ID"
gbp l3policy-update $INFRA_L3_POLICY_ID --external-segment "$INFRA_EXTERNAL_SEGMENT_ID="

heat stack-create -f "$APP_YAML" "$APP_STACK" -P "web_vm_image=$WEB_VM_IMAGE_NAME;web_vm_flavor=$WEB_VM_FLAVOR;app_vm_image=$APP_VM_IMAGE_NAME;app_vm_flavor=$APP_VM_FLAVOR;app_rule_set_id=$APP_RULE_SET_ID;app_l3_policy_id=$INFRA_L3_POLICY_ID"

confirm_resource_created "heat stack-show" "$APP_STACK" "CREATE_COMPLETE"

WEB_PTG_ID=`heat output-show "$APP_STACK" "web_ptg_id" | sed "s/\"//g"`
gbp group-update $WEB_PTG_ID --network-service-policy "$VIP_IP_POLICY_ID"
gbp group-update $WEB_PTG_ID --provided-policy-rule-sets "$HTTP_WITH_LB_REDIRECT_RULE_SET_ID=true"
gbp group-update $WEB_PTG_ID --consumed-policy-rule-sets "$APP_TO_OUTSIDE_RULE_SET_ID=true,$APP_RULE_SET_ID=true"

gbp external-policy-update $INFRA_EXTERNAL_POLICY_ID --consumed-policy-rule-sets "$HTTP_WITH_LB_REDIRECT_RULE_SET_ID=true"

echo "*********************************************************************"
echo "SUCCESS: End $0"
echo "*********************************************************************"
