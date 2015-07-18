#!/usr/bin/env bash

# Prior to running this script check the following:
# 1. Set the name and path of the keystone_admin file in external-connectivity.conf OPENSTACK_ENV_FILE var
# 2. The script assumes two users with the names: admin and demo
# 3. The script requires three tenants to be present, their names are set in
#    demo.conf as the following variables:
#    ADMIN_TENANT_NAME, HR_TENANT_NAME, FINANCE_TENANT_NAME

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
if [ -z "$NON_ADMIN_PASSWORD" ]; then
    NON_ADMIN_PASSWORD=$OS_PASSWORD
fi

set_user_password_tenant $ADMIN_USERNAME $ADMIN_PASSWORD $ADMIN_TENANT_NAME

heat stack-create -f "$CONTRACTS_EXTERNAL_YAML" "$CONTRACTS_EXTERNAL_STACK"

confirm_resource_created "heat stack-show" "$CONTRACTS_EXTERNAL_STACK" "CREATE_COMPLETE"
ICMP_TCP_RULE_SET_ID=`heat output-show "$CONTRACTS_EXTERNAL_STACK" "icmp_tcp_rule_set_id" | sed "s/\"//g"`

heat stack-create -f "$ADMIN_EXTERNAL_YAML" "$ADMIN_EXTERNAL_STACK" -P "infra_external_segment_name=$INFRA_EXTERNAL_SEGMENT_NAME;infra_external_policy_name=$INFRA_EXTERNAL_POLICY_NAME;app_external_segment_name=$APP_EXTERNAL_SEGMENT_NAME;app_external_policy_name=$APP_EXTERNAL_POLICY_NAME;infra_ip_pool=$INFRA_IP_POOL;app_ip_pool=$APP_IP_POOL;infra_l3_policy_name=$INFRA_L3_POLICY_NAME;app_l3_policy_name=$APP_L3_POLICY_NAME"

confirm_resource_created "heat stack-show" "$ADMIN_EXTERNAL_STACK" "CREATE_COMPLETE"
INFRA_EXTERNAL_SEGMENT_ID=`heat output-show "$ADMIN_EXTERNAL_STACK" "infra_external_segment_id" | sed "s/\"//g"`
INFRA_EXTERNAL_POLICY_ID=`heat output-show "$ADMIN_EXTERNAL_STACK" "infra_external_policy_id" | sed "s/\"//g"`
INFRA_L3_POLICY_ID=`heat output-show "$ADMIN_EXTERNAL_STACK" "infra_l3_policy_id" | sed "s/\"//g"`
INFRA_L2_POLICY_ID=`heat output-show "$ADMIN_EXTERNAL_STACK" "infra_l2_policy_id" | sed "s/\"//g"`
APP_EXTERNAL_SEGMENT_ID=`heat output-show "$ADMIN_EXTERNAL_STACK" "app_external_segment_id" | sed "s/\"//g"`
APP_EXTERNAL_POLICY_ID=`heat output-show "$ADMIN_EXTERNAL_STACK" "app_external_policy_id" | sed "s/\"//g"`
APP_L3_POLICY_ID=`heat output-show "$ADMIN_EXTERNAL_STACK" "app_l3_policy_id" | sed "s/\"//g"`
APP_L2_POLICY_ID=`heat output-show "$ADMIN_EXTERNAL_STACK" "app_l2_policy_id" | sed "s/\"//g"`

gbp external-policy-update $INFRA_EXTERNAL_POLICY_ID --external-segments "$INFRA_EXTERNAL_SEGMENT_ID"
gbp l3policy-update $INFRA_L3_POLICY_ID --external-segment "$INFRA_EXTERNAL_SEGMENT_ID="
gbp external-policy-update $INFRA_EXTERNAL_POLICY_ID --provided-policy-rule-sets "$ICMP_TCP_RULE_SET_ID=true"
gbp external-policy-update $INFRA_EXTERNAL_POLICY_ID --consumed-policy-rule-sets "$ICMP_TCP_RULE_SET_ID=true"
MGMT_PTG_ID=$(gbp group-create --l2-policy INFRA_L2_POLICY_ID MANAGEMENT-PTG | grep ' id ' | awk '{print $4}' )
gbp group-update $MGMT_PTG_ID --provided-policy-rule-sets "$ICMP_TCP_RULE_SET_ID=true"
gbp group-update $MGMT_PTG_ID --consumed-policy-rule-sets "$ICMP_TCP_RULE_SET_ID=true"

gbp external-policy-update $APP_EXTERNAL_POLICY_ID --external-segments "$APP_EXTERNAL_SEGMENT_ID"
gbp l3policy-update $APP_L3_POLICY_ID --external-segment "$APP_EXTERNAL_SEGMENT_ID="
gbp external-policy-update $APP_EXTERNAL_POLICY_ID --provided-policy-rule-sets "$ICMP_TCP_RULE_SET_ID=true"
gbp external-policy-update $APP_EXTERNAL_POLICY_ID --consumed-policy-rule-sets "$ICMP_TCP_RULE_SET_ID=true"
EXTERNALLY_CONNECTED_PTG_ID=$(gbp group-create --l2-policy APP_L2_POLICY_ID EXTERNALLY-CONNECTED-PTG | grep ' id ' | awk '{print $4}' )
gbp group-update $EXTERNALLY_CONNECTED_PTG_ID --provided-policy-rule-sets "$ICMP_TCP_RULE_SET_ID=true"
gbp group-update $EXTERNALLY_CONNECTED_PTG_ID --consumed-policy-rule-sets "$ICMP_TCP_RULE_SET_ID=true"

echo "*********************************************************************"
echo "SUCCESS: End $0"
echo "*********************************************************************"
