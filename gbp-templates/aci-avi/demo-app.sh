#!/usr/bin/env bash

# **demo.sh**
# Prior to running this script check the following:
# 1. Set the name and path of the keystone_admin file in demo.conf OPENSTACK_ENV_FILE var
# 2. The script assumes two users with the names: admin and demo
# 3. The script requires three tenants to be present, their names are set in
#    demo.conf as the following variables:
#    ADMIN_TENANT_NAME, HR_TENANT_NAME, FINANCE_TENANT_NAME
# Usage:
# ./demo aci or ./demo acix
# Use the "acix" mode for inserting the transparent "FW + IDS" chain


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

confirm_resource_created "heat stack-show" "$CONTRACTS_STACK" "CREATE_COMPLETE"
VIP_IP_POLICY_ID=`heat output-show "$CONTRACTS_STACK" "vip_ip_policy_id" | sed "s/\"//g"`
HTTP_RULE_SET_ID=`heat output-show "$CONTRACTS_STACK" "http_rule_set_id" | sed "s/\"//g"`
HTTP_WITH_LB_REDIRECT_RULE_SET_ID=`heat output-show "$CONTRACTS_STACK" "http_with_lb_redirect_rule_set_id" | sed "s/\"//g"`
APP_RULE_SET_ID=`heat output-show "$CONTRACTS_STACK" "app_rule_set_id" | sed "s/\"//g"`
MYSQL_RULE_SET_ID=`heat output-show "$CONTRACTS_STACK" "mysql_rule_set_id" | sed "s/\"//g"`
MYSQL_VIA_FW_IDS_RULE_SET_ID=`heat output-show "$CONTRACTS_STACK" "mysql_via_fw_ids_rule_set_id" | sed "s/\"//g"`
MONITORING_RULE_SET_ID=`heat output-show "$CONTRACTS_STACK" "monitoring_rule_set_id" | sed "s/\"//g"`
MONITORING_TO_OUTSIDE_RULE_SET_ID=`heat output-show "$CONTRACTS_STACK" "monitoring_to_outside_rule_set_id" | sed "s/\"//g"`

confirm_resource_created "heat stack-show" "$ADMIN_STACK" "CREATE_COMPLETE"
APP_L3_POLICY_ID=`heat output-show "$ADMIN_STACK" "app_l3_policy_id" | sed "s/\"//g"`
MGMT_PTG_ID=`heat output-show "$ADMIN_STACK" "mgmt_ptg_id" | sed "s/\"//g"`
SVC_MGMT_PTG_ID=`heat output-show "$ADMIN_STACK" "svc_mgmt_ptg_id" | sed "s/\"//g"`
INFRA_EXTERNAL_SEGMENT_ID=`heat output-show "$ADMIN_STACK" "infra_external_segment_id" | sed "s/\"//g"`
INFRA_EXTERNAL_POLICY_ID=`heat output-show "$ADMIN_STACK" "infra_external_policy_id" | sed "s/\"//g"`
APP_EXTERNAL_SEGMENT_ID=`heat output-show "$ADMIN_STACK" "app_external_segment_id" | sed "s/\"//g"`
APP_EXTERNAL_POLICY_ID=`heat output-show "$ADMIN_STACK" "app_external_policy_id" | sed "s/\"//g"`
INFRA_L3_POLICY_ID=`heat output-show "$ADMIN_STACK" "infra_l3_policy_id" | sed "s/\"//g"`
MONITORING_IP=`heat output-show "$ADMIN_STACK" "monitoring_ip" | sed "s/\"//g"`
APP_L3_POLICY_ID=`heat output-show "$ADMIN_STACK" "app_l3_policy_id" | sed "s/\"//g"`

gbp external-policy-update $INFRA_EXTERNAL_POLICY_ID --external-segments "$INFRA_EXTERNAL_SEGMENT_ID"
gbp l3policy-update $INFRA_L3_POLICY_ID --external-segment "$INFRA_EXTERNAL_SEGMENT_ID="

gbp l3policy-update $APP_L3_POLICY_ID --external-segment "$APP_EXTERNAL_SEGMENT_ID="
gbp external-policy-update $APP_EXTERNAL_POLICY_ID --external-segments "$APP_EXTERNAL_SEGMENT_ID"

# Launch the Eng tenant's stack
set_user_password_tenant $NON_ADMIN_USERNAME $NON_ADMIN_PASSWORD $ENG_TENANT_NAME
 
heat stack-create -f "$APP_YAML" "$ENG_STACK" -P "web_vm_image=$WEB_VM_IMAGE_NAME;web_vm_flavor=$WEB_VM_FLAVOR;app_vm_image=$APP_VM_IMAGE_NAME;app_vm_flavor=$APP_VM_FLAVOR;db_vm_image=$DB_VM_IMAGE_NAME;db_vm_flavor=$DB_VM_FLAVOR;mysql_rule_set_id=$MYSQL_RULE_SET_ID;app_rule_set_id=$APP_RULE_SET_ID;app_l3_policy_id=$APP_L3_POLICY_ID;mgmt_ptg_id=$MGMT_PTG_ID;monitoring_ip=$MONITORING_IP"

confirm_resource_created "heat stack-show" "$ENG_STACK" "CREATE_COMPLETE"

WEB_PTG_ID=`heat output-show "$ENG_STACK" "web_ptg_id" | sed "s/\"//g"`
gbp group-update $WEB_PTG_ID --provided-policy-rule-sets "$HTTP_RULE_SET_ID=true"
gbp group-update $WEB_PTG_ID --consumed-policy-rule-sets "$APP_RULE_SET_ID=true"

set_user_password_tenant $ADMIN_USERNAME $ADMIN_PASSWORD $ADMIN_TENANT_NAME
gbp external-policy-update $APP_EXTERNAL_POLICY_ID --consumed-policy-rule-sets "$HTTP_RULE_SET_ID=true"
# Launching the Eng tenant's stack complete

# Launch the HR tenant's stack
set_user_password_tenant $NON_ADMIN_USERNAME $NON_ADMIN_PASSWORD $HR_TENANT_NAME
 
heat stack-create -f "$APP_YAML" "$HR_STACK" -P "web_vm_image=$WEB_VM_IMAGE_NAME;web_vm_flavor=$WEB_VM_FLAVOR;app_vm_image=$APP_VM_IMAGE_NAME;app_vm_flavor=$APP_VM_FLAVOR;db_vm_image=$DB_VM_IMAGE_NAME;db_vm_flavor=$DB_VM_FLAVOR;mysql_rule_set_id=$MYSQL_RULE_SET_ID;app_rule_set_id=$APP_RULE_SET_ID;app_l3_policy_id=$APP_L3_POLICY_ID;mgmt_ptg_id=$MGMT_PTG_ID;monitoring_ip=$MONITORING_IP"

confirm_resource_created "heat stack-show" "$HR_STACK" "CREATE_COMPLETE"

WEB_PTG_ID=`heat output-show "$HR_STACK" "web_ptg_id" | sed "s/\"//g"`
gbp group-update $WEB_PTG_ID --network-service-policy "$VIP_IP_POLICY_ID"
gbp group-update $WEB_PTG_ID --provided-policy-rule-sets "$HTTP_WITH_LB_REDIRECT_RULE_SET_ID=true"
gbp group-update $WEB_PTG_ID --consumed-policy-rule-sets "$APP_RULE_SET_ID=true"

set_user_password_tenant $ADMIN_USERNAME $ADMIN_PASSWORD $ADMIN_TENANT_NAME
gbp external-policy-update $APP_EXTERNAL_POLICY_ID --consumed-policy-rule-sets "$HTTP_WITH_LB_REDIRECT_RULE_SET_ID=true,$HTTP_RULE_SET_ID=true"

set_user_password_tenant $NON_ADMIN_USERNAME $NON_ADMIN_PASSWORD $HR_TENANT_NAME
if [ "$RENDERING_MODE" == "$ACI_TRANSPARENT_SVC_RENDERING" ]; then
    APP_L2_POLICY_ID=`heat output-show "$HR_STACK" "app_l2_policy_id" | sed "s/\"//g"`
    DB_PTG_ID=`heat output-show "$HR_STACK" "db_ptg_id" | sed "s/\"//g"`
    APP_PTG_ID=`heat output-show "$HR_STACK" "app_ptg_id" | sed "s/\"//g"`
    gbp l2policy-update $APP_L2_POLICY_ID --allow-broadcast True
    gbp group-update $DB_PTG_ID --provided-policy-rule-sets "$MYSQL_VIA_FW_IDS_RULE_SET_ID=true"
    gbp group-update $APP_PTG_ID --consumed-policy-rule-sets "$MYSQL_VIA_FW_IDS_RULE_SET_ID=true"
fi
# Launching the HR tenant's stack complete


echo "*********************************************************************"
echo "SUCCESS: End $0"
echo "*********************************************************************"
