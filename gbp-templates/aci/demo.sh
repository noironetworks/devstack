#!/usr/bin/env bash

# **demo.sh**
# Prior to running this script check the following:
# 1. Set the name and path of the keystone_admin file in demo.conf OPENSTACK_ENV_FILE var
# 2. The script assumes two users with the names: admin and demo
# 3. The script requires three tenants to be present, their names are set in
#    demo.conf as the following variables:
#    ADMIN_TENANT_NAME, HR_TENANT_NAME, FINANCE_TENANT_NAME
# Usage:
# ./demo aci or ./demo acix or ./demo neutron
# Use the "acix" mode for the inserting the transparent "FW + IDS" chain

EXT_POLICY_NAME="Outside"

ACI_RENDERING="aci"
NEUTRON_RENDERING="neutron"

PORT_ADDRESS_TRANSLATION=False

ACTIVE_TIMEOUT=120

CONTRACTS_YAML="contracts.yaml"
CONTRACTS_STACK="Contracts"
ADMIN_YAML="admin.yaml"
ADMIN_STACK="Admin"
APP_YAML="app.yaml"
HR_STACK="HR_Three_Tier"
FINANCE_STACK="Finance_Three_Tier"

USAGE="$0 <aci|acix|neutron>"

function set_user_password_tenant {
    local xtrace=$(set +o | grep xtrace)
    set +o xtrace
    export OS_USERNAME=$1
    export OS_PASSWORD=$2
    export OS_TENANT_NAME=$3
    export PS1='[\u@\h \W(keystone_$1)]\$ '
    $xtrace
}

function confirm_resource_created {
    local xtrace=$(set +o | grep xtrace)
    set +o xtrace
    if ! timeout $ACTIVE_TIMEOUT sh -c "while ! $1 \"$2\" | grep \"$3\"; do sleep 1; done"; then
        set -o xtrace
        echo "resource '$1 $2' did not become active!"
        false
    fi
    $xtrace
}

# Process args
RENDERING_MODE=$1
if [ "${RENDERING_MODE}"x = ""x ] ; then
    echo "USAGE: $USAGE" 2>&1
    echo "  >  No rendering mode specified." 1>&2
    exit 1
fi

if [ "$1" = "$NEUTRON_RENDERING" ] ; then
    PORT_ADDRESS_TRANSLATION=True
fi

source demo.conf

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

heat stack-create -f "$CONTRACTS_YAML" "$CONTRACTS_STACK" -P "monitoring_rule_set_name=$MONITORING_RULE_SET_NAME;monitoring_to_outside_rule_set_name=$MONITORING_TO_OUTSIDE_RULE_SET_NAME;app_to_outside_rule_set_name=$APP_TO_OUTSIDE_RULE_SET_NAME;mysql_rule_set_name=$MYSQL_RULE_SET_NAME;mysql_via_fw_ids_rule_set_name=$MYSQL_VIA_FW_IDS_RULE_SET_NAME;app_rule_set_name=$APP_RULE_SET_NAME;web_tier_consumed_prs_name=$WEB_TIER_CONSUMED_PRS_NAME;web_tier_provided_prs_name=$WEB_TIER_PROVIDED_PRS_NAME"

confirm_resource_created "heat stack-show" "$CONTRACTS_STACK" "CREATE_COMPLETE"
VIP_IP_POLICY_ID=`heat output-show "$CONTRACTS_STACK" "vip_ip_policy_id" | sed "s/\"//g"`
HTTP_WITH_LB_REDIRECT_RULE_SET_ID=`heat output-show "$CONTRACTS_STACK" "http_with_lb_redirect_rule_set_id" | sed "s/\"//g"`
APP_RULE_SET_ID=`heat output-show "$CONTRACTS_STACK" "app_rule_set_id" | sed "s/\"//g"`
MYSQL_RULE_SET_ID=`heat output-show "$CONTRACTS_STACK" "mysql_rule_set_id" | sed "s/\"//g"`
MYSQL_VIA_FW_IDS_RULE_SET_ID=`heat output-show "$CONTRACTS_STACK" "mysql_via_fw_ids_rule_set_id" | sed "s/\"//g"`
APP_TO_OUTSIDE_RULE_SET_ID=`heat output-show "$CONTRACTS_STACK" "app_to_outside_rule_set_id" | sed "s/\"//g"`
MONITORING_RULE_SET_ID=`heat output-show "$CONTRACTS_STACK" "monitoring_rule_set_id" | sed "s/\"//g"`
MONITORING_TO_OUTSIDE_RULE_SET_ID=`heat output-show "$CONTRACTS_STACK" "monitoring_to_outside_rule_set_id" | sed "s/\"//g"`

heat stack-create -f "$ADMIN_YAML" "$ADMIN_STACK" -P "infra_external_segment_name=$INFRA_EXTERNAL_SEGMENT_NAME;infra_external_policy_name=$INFRA_EXTERNAL_POLICY_NAME;app_external_segment_name=$APP_EXTERNAL_SEGMENT_NAME;app_external_policy_name=$APP_EXTERNAL_POLICY_NAME;port_address_translation=$PORT_ADDRESS_TRANSLATION;infra_ip_pool=$INFRA_IP_POOL;app_ip_pool=$APP_IP_POOL;monitoring_rule_set_id=$MONITORING_RULE_SET_ID;monitoring_to_outside_rule_set_id=$MONITORING_TO_OUTSIDE_RULE_SET_ID;app_to_outside_rule_set_id=$APP_TO_OUTSIDE_RULE_SET_ID;mysql_rule_set_id=$MYSQL_RULE_SET_ID;app_rule_set_id=$APP_RULE_SET_ID;web_tier_consumed_prs_id=$APP_TO_OUTSIDE_RULE_SET_ID;web_tier_provided_prs_id=$HTTP_WITH_LB_REDIRECT_RULE_SET_ID;monitoring_ptg_name=$MONITORING_PTG_NAME;service_management_ptg_name=$SERVICE_MANAGEMENT_PTG_NAME;management_ptg_name=$MANAGEMENT_PTG_NAME;monitoring_vm_image=$MONITORING_VM_IMAGE_NAME;monitoring_vm_flavor=$MONITORING_VM_FLAVOR;mgmt_vm_image=$MGMT_VM_IMAGE_NAME;mgmt_vm_flavor=$MGMT_VM_FLAVOR;svc_mgmt_vm_image=$SVC_MGMT_VM_IMAGE_NAME;svc_mgmt_vm_flavor=$SVC_MGMT_VM_FLAVOR;infra_l3_policy_name=$INFRA_L3_POLICY_NAME;app_l3_policy_name=$APP_L3_POLICY_NAME"

confirm_resource_created "heat stack-show" "$ADMIN_STACK" "CREATE_COMPLETE"
APP_L3_POLICY_ID=`heat output-show "$ADMIN_STACK" "app_l3_policy_id" | sed "s/\"//g"`
MGMT_PTG_ID=`heat output-show "$ADMIN_STACK" "mgmt_ptg_id" | sed "s/\"//g"`
SVC_MGMT_PTG_ID=`heat output-show "$ADMIN_STACK" "svc_mgmt_ptg_id" | sed "s/\"//g"`
INFRA_EXTERNAL_SEGMENT_ID=`heat output-show "$ADMIN_STACK" "infra_external_segment_id" | sed "s/\"//g"`
INFRA_EXTERNAL_POLICY_ID=`heat output-show "$ADMIN_STACK" "infra_external_policy_id" | sed "s/\"//g"`
APP_EXTERNAL_SEGMENT_ID=`heat output-show "$ADMIN_STACK" "app_external_segment_id" | sed "s/\"//g"`
APP_EXTERNAL_POLICY_ID=`heat output-show "$ADMIN_STACK" "app_external_policy_id" | sed "s/\"//g"`
INFRA_L3_POLICY_ID=`heat output-show "$ADMIN_STACK" "infra_l3_policy_id" | sed "s/\"//g"`
APP_L3_POLICY_ID=`heat output-show "$ADMIN_STACK" "app_l3_policy_id" | sed "s/\"//g"`

gbp external-policy-update $INFRA_EXTERNAL_POLICY_ID --external-segments "$INFRA_EXTERNAL_SEGMENT_ID"
gbp l3policy-update $INFRA_L3_POLICY_ID --external-segment "$INFRA_EXTERNAL_SEGMENT_ID="

gbp external-policy-update $APP_EXTERNAL_POLICY_ID --external-segments "$APP_EXTERNAL_SEGMENT_ID"
gbp l3policy-update $APP_L3_POLICY_ID --external-segment "$APP_EXTERNAL_SEGMENT_ID="

set_user_password_tenant $NON_ADMIN_USERNAME $NON_ADMIN_PASSWORD $HR_TENANT_NAME
 
heat stack-create -f "$APP_YAML" "$HR_STACK" -P "web_vm_image=$WEB_VM_IMAGE_NAME;web_vm_flavor=$WEB_VM_FLAVOR;app_vm_image=$APP_VM_IMAGE_NAME;app_vm_flavor=$APP_VM_FLAVOR;db_vm_image=$DB_VM_IMAGE_NAME;db_vm_flavor=$DB_VM_FLAVOR;mysql_rule_set_id=$MYSQL_RULE_SET_ID;app_rule_set_id=$APP_RULE_SET_ID;web_tier_consumed_prs_id=$APP_TO_OUTSIDE_RULE_SET_ID;web_tier_provided_prs_id=$HTTP_WITH_LB_REDIRECT_RULE_SET_ID;vip_ip_policy_id=$VIP_IP_POLICY_ID;app_l3_policy_id=$APP_L3_POLICY_ID;mgmt_ptg_id=$MGMT_PTG_ID"

if [ "$RENDERING_MODE" == "acix" ]; then
    confirm_resource_created "heat stack-show" "$HR_STACK" "CREATE_COMPLETE"
    DB_PTG_ID=`heat output-show "$HR_STACK" "db_ptg_id" | sed "s/\"//g"`
    APP_PTG_ID=`heat output-show "$HR_STACK" "app_ptg_id" | sed "s/\"//g"`
    gbp policy-rule-set-update $DB_PTG_ID --provided-policy-rule-sets "$MYSQL_VIA_FW_IDS_RULE_SET_ID=true"
    gbp policy-rule-set-update $APP_PTG_ID --consumed-policy-rule-sets "$MYSQL_VIA_FW_IDS_RULE_SET_ID=true"
fi

exit

echo "*********************************************************************"
echo "SUCCESS: End $0"
echo "*********************************************************************"
