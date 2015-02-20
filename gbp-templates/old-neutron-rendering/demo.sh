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

USAGE="$0 <aci|neutron>"
ACTIVE_TIMEOUT=120

function set_user_password_tenant {
    local xtrace=$(set +o | grep xtrace)
    set +o xtrace
    export OS_USERNAME=$1
    export OS_PASSWORD=$2
    export OS_TENANT_NAME=$3
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

source $OPENSTACK_ENV_FILE

set_user_password_tenant $ADMIN_USERNAME $ADMIN_PASSWORD $ADMIN_TENANT_NAME

# Print the commands being run so that we can see the command that triggers
# an error.  It is also useful for following allowing as the install occurs.
set -o xtrace

heat stack-create -f external_connectivity.yaml external -P "external_network_cidr=$EXT_NET_CIDR;external_network_gateway=$EXT_NET_GATEWAY;external_segment_name=$EXT_SEGMENT_NAME;physical_network_name=$PHYSICAL_NETWORK_NAME;physical_network_type=$PHYSICAL_NETWORK_TYPE;port_address_translation=$PORT_ADDRESS_TRANSLATION"

confirm_resource_created "gbp external-segment-show" "$EXT_SEGMENT_NAME" "id"

EXT_SEGMENT_ID=`gbp external-segment-show $EXT_SEGMENT_NAME | grep ' id ' | cut -d"|" -f3 | sed 's/ //g'`

set_user_password_tenant $NON_ADMIN_USERNAME $NON_ADMIN_PASSWORD $NON_ADMIN_TENANT_NAME
 
heat stack-create -f three_tier_with_lb.yaml $THREE_TIER_STACK_NAME -P "monitoring_vm_image=$MONITORING_VM_IMAGE_NAME;web_vm_image=$WEB_VM_IMAGE_NAME;app_vm_image=$APP_VM_IMAGE_NAME;db_vm_image=$DB_VM_IMAGE_NAME;app_ip_pool=$APP_IP_POOL;mgmt_ip_pool=$SERVICES_MGMT_IP_POOL;external_policy_name=$EXT_POLICY_NAME;external_segment_id=$EXT_SEGMENT_ID;web_tier_consumed_prs_name=$WEB_TIER_CONSUMED_PRS_NAME;web_tier_provided_prs_name=$WEB_TIER_PROVIDED_PRS_NAME"

confirm_resource_created "heat stack-show" "$THREE_TIER_STACK_NAME" "CREATE_COMPLETE"
#confirm_resource_created "gbp policy-rule-set show" "$WEB_TIER_CONSUMED_PRS_NAME"

gbp external-policy-update $EXT_POLICY_NAME --provided-policy-rule-sets "$WEB_TIER_CONSUMED_PRS_NAME=true"

#confirm_resource_created "policy-rule-set" "$WEB_TIER_PROVIDED_PRS_NAME"

gbp external-policy-update $EXT_POLICY_NAME --consumed-policy-rule-sets "$WEB_TIER_PROVIDED_PRS_NAME=true"

set +o xtrace
echo "*********************************************************************"
echo "SUCCESS: End $0"
echo "*********************************************************************"
