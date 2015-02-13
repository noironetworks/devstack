#!/usr/bin/env bash

# **demo.sh**
# Usage:
# ./demo api
# or
# ./demo neutron

EXT_POLICY_NAME="Outside"

ACI_RENDERING="aci"
NEUTRON_RENDERING="neutron"

PORT_ADDRESS_TRANSLATION=False

ACTIVE_TIMEOUT=120

EXTERNAL_STACK="External"
IT_STACK="IT"
HR_STACK="HR-Three-Tier"
FINANCE_STACK="Finance-Three-Tier"

USAGE="$0 <aci|neutron>"

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

#set_user_password_tenant $ADMIN_USERNAME $ADMIN_PASSWORD $ADMIN_TENANT_NAME

# Print the commands being run so that we can see the command that triggers
# an error.  It is also useful for following allowing as the install occurs.

heat stack-create -f external_connectivity.yaml "$EXTERNAL_STACK" -P "external_network_cidr=$EXT_NET_CIDR;external_network_gateway=$EXT_NET_GATEWAY;external_segment_name=$EXT_SEGMENT_NAME;physical_network_name=$PHYSICAL_NETWORK_NAME;physical_network_type=$PHYSICAL_NETWORK_TYPE;port_address_translation=$PORT_ADDRESS_TRANSLATION;mgmt_ip_pool=$SERVICES_MGMT_IP_POOL;service_management_ptg_name=$SERVICE_MANAGEMENT_PTG_NAME"

confirm_resource_created "heat stack-show" "$EXTERNAL_STACK" "CREATE_COMPLETE"
confirm_resource_created "gbp external-segment-show" "$EXT_SEGMENT_NAME" "id"
EXT_SEGMENT_ID=`gbp external-segment-show "$EXT_SEGMENT_NAME" | grep ' id ' | cut -d"|" -f3 | sed 's/ //g'`

#confirm_resource_created "gbp group-show" "$SERVICE_MANAGEMENT_PTG_NAME" "id"
SERVICE_MANAGEMENT_PTG_ID=`gbp group-show "$SERVICE_MANAGEMENT_PTG_NAME" | grep ' id ' | cut -d"|" -f3 | sed 's/ //g'`

set_user_password_tenant $NON_ADMIN_USERNAME $NON_ADMIN_PASSWORD $IT_TENANT_NAME
 
heat stack-create -f it.yaml "$IT_STACK" -P "monitoring_vm_image=$MONITORING_VM_IMAGE_NAME;monitoring_vm_flavor=$MONITORING_VM_FLAVOR;monitoring_ip_pool=$MONITORING_IP_POOL;monitoring_rule_set_name=$MONITORING_RULE_SET_NAME"

confirm_resource_created "heat stack-show" "$IT_STACK" "CREATE_COMPLETE"
confirm_resource_created "gbp policy-rule-set-show" "$MONITORING_RULE_SET_NAME" "id"
MONTORING_PRS_ID=`gbp policy-rule-set-show "$MONITORING_RULE_SET_NAME" | grep ' id ' | cut -d"|" -f3 | sed 's/ //g'`

set_user_password_tenant $NON_ADMIN_USERNAME $NON_ADMIN_PASSWORD $HR_TENANT_NAME
 
heat stack-create -f three_tier_with_lb.yaml "$HR_STACK" -P "monitoring_rule_set=$MONITORING_PRS_ID;web_vm_image=$WEB_VM_IMAGE_NAME;web_vm_flavor=$WEB_VM_FLAVOR;app_vm_image=$APP_VM_IMAGE_NAME;app_vm_flavor=$APP_VM_FLAVOR;db_vm_image=$DB_VM_IMAGE_NAME;db_vm_flavor=$DB_VM_FLAVOR;app_ip_pool=$APP_IP_POOL;external_policy_name=$EXT_POLICY_NAME;external_segment_id=$EXT_SEGMENT_ID;web_tier_consumed_prs_name=$WEB_TIER_CONSUMED_PRS_NAME;web_tier_provided_prs_name=$WEB_TIER_PROVIDED_PRS_NAME"

confirm_resource_created "heat stack-show" "$HR_STACK" "CREATE_COMPLETE"
confirm_resource_created "gbp policy-rule-set show" "$WEB_TIER_CONSUMED_PRS_NAME"
gbp external-policy-update $EXT_POLICY_NAME --provided-policy-rule-sets "$WEB_TIER_CONSUMED_PRS_NAME=true"

confirm_resource_created "gbp policy-rule-set show" "$WEB_TIER_PROVIDED_PRS_NAME"
gbp external-policy-update $EXT_POLICY_NAME --consumed-policy-rule-sets "$WEB_TIER_PROVIDED_PRS_NAME=true"

echo "*********************************************************************"
echo "SUCCESS: End $0"
echo "*********************************************************************"
