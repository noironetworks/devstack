#!/usr/bin/env python
import sys
import logging
import re
import string
from commands import *
from gbpclient.v2_0 import client as gbpclient

# Initialize logging
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s', level=logging.WARNING)
_log = logging.getLogger( __name__ )

_log.setLevel(logging.INFO)
_log.setLevel(logging.DEBUG)

class GBPCrud(object):
    """
    The intent of this Base Class is for doing CRUD and associated operations
    by calling directly the APIs of the GBP Python Client
    """

    def __init__(self,ostack_controller,
                 username='admin',
                 password='noir0123',
                 tenant='admin'):
        cred = {}
        cred['username']=username
        cred['password']=password
        cred['tenant_name']=tenant
        cred['auth_url'] = "http://%s:5000/v2.0/" % ostack_controller
        self.client = gbpclient.Client(**cred)

    def create_gbp_policy_action(self,name,**kwargs):
        """
        Create a GBP Policy Action
        Supported  keyword based attributes and their values:
        'action_type'= 'allow','redirect'
        'action_value'= uuid string
        'shared'= 'True', 'False'
        'description'= any string
        """
        policy_action= {"name":name}
        try:
           for arg,val in kwargs.items():
               policy_action[arg]=val
           body = {"policy_action":policy_action}
           self.client.create_policy_action(body)
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Create of Policy Action= %s, failed" %(name))
           return 0
    
    def verify_gbp_policy_action(self,name):
        """
        Verify the GBP Policy Action by passing its name
        """
        for action in self.client.list_policy_actions()['policy_actions']:
            if action['name'].encode('ascii') == name:
               return action['id'].encode('ascii')
        _log.error("Policy Action NOT Found")
        return 0
 
    def get_gbp_policy_action_list(self,getdict=False):
        """
        Fetch a List of GBP Policy Actions
        getdict: 'True', will return a dictionary comprising 'name' & 'uuid'
        """
        try:
           if getdict == True:
              name_uuid = {}
              for action in self.client.list_policy_actions()['policy_actions']:
                  name_uuid[action['name'].encode('ascii')]= action['id'].encode('ascii')
           else: # Return list of ids
               pa_list = [item['id'] for item in self.client.list_policy_actions()['policy_actions']]
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Fetching Policy Action List, failed")
           return 0
        if getdict == True:
           return name_uuid
        else:
           return pa_list

    def get_gbp_policy_action_show(self,uuid):
        """
        Fetch the details of a given GBP Policy Action
        """
        try:
           pa = self.client.show_policy_action(uuid)
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Fetching a given Policy Action=%s, failed" %(uuid))
           return 0
        return pa

    def delete_gbp_policy_action(self,name_uuid,property_type='name'):
         """
         Delete a GBP Policy Action
         property_type='name' or 'uuid'
         If property_type=='name', pass 'name_string' for name_uuid,
         else pass 'uuid_string' for name_uuid param
         """
         try:
            if property_type=='name':
               action_uuid=self.verify_gbp_policy_action(name_uuid)
               self.client.delete_policy_action(action_uuid)
            else:
               self.client.delete_policy_action(name_uuid)
         except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Deleting Policy Action = %s, failed" %(name_uuid))
           return 0

    def create_gbp_policy_classifier(self,name,**kwargs): 
        """
        Create GBP Policy Classifier
        Supported  keyword based attributes and their values:
        'direction'= 'in','bi','out'
        'protocol'= 'tcp','udp','icmp'
        'port_range'= 'x:y', where x<=y, 66:67 or 66:66
        'shared'= 'True', 'False'
        'description'= any string
        """
        policy_classifier= {"name":name}
        try:
           for arg,val in kwargs.items():
               policy_classifier[arg]=val
           body = {"policy_classifier":policy_classifier}
           self.client.create_policy_classifier(body)
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Create of Policy Classifier= %s, failed" %(name))
           return 0

    def update_gbp_policy_classifier(self,
                                     name_uuid,
                                     property_type='name',
                                     **kwargs):
         """
         Update GBP Policy Classifier editable attributes
         Supported  keyword based attributes and their values:
         'direction'= 'in','bi','out'
         'protocol'= 'tcp','udp','icmp'
         'port_range'= 'x:y', where x<=y, 66:67 or 66:66
         'shared'= 'True', 'False'
         'description'= any string
         """
         if property_type=='uuid':
            classifier_id=name_uuid
         else:
            classifier_id=self.verify_gbp_policy_classifier(name_uuid)
         policy_classifier= {}
         try:
            for arg,val in kwargs.items():
               policy_classifier[arg]=val
            body = {"policy_classifier":policy_classifier}
            self.client.update_policy_classifier(classifier_id,body)
         except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Update of Policy Classifier= %s, failed" %(name_uuid))
           return 0

    def get_gbp_policy_classifier_list(self,getdict=False):
        """
        Fetch a List of GBP Policy Classifiers
        getdict: 'True', will return a dictionary comprising 'name' & 'uuid'
        """
        try:
           if getdict == True:
              name_uuid = {}
              for classifier in self.client.list_policy_classifiers()['policy_classifiers']:
                  name_uuid[classifier['name'].encode('ascii')]= classifier['id'].encode('ascii')
           else:
               pc_list = [item['id'] for item in self.client.list_policy_classifiers()['policy_classifiers']]
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Fetching Policy Classifier List, failed")
           return 0
        if getdict == True:
           return name_uuid
        else:
           return pc_list

    def delete_gbp_policy_classifier(self,name_uuid,property_type='name'):
         """
         Delete a GBP Policy Classifier
         property_type='name' or 'uuid'
         If property_type=='name', pass 'name_string' for name_uuid,
         else pass 'uuid_string' for name_uuid param
         """
         try:
            if property_type=='name':
               class_uuid=self.verify_gbp_policy_classifier(name_uuid)
               self.client.delete_policy_classifer(class_uuid)
            else:
               self.client.delete_policy_classifier(name_uuid)
         except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Deleting Policy Classifier = %s, failed" %(name_uuid))
           return 0

    def verify_gbp_policy_classifier(self,name):
        """
        Verify the GBP Policy Classifier by passing its name and fetch its UUID
        """
        for classifier in self.client.list_policy_classifiers()['policy_classifiers']:
            if classifier['name'].encode('ascii') == name:
               return classifier['id'].encode('ascii')
        _log.error("Policy Classifier NOT Found")
        return 0

    def create_gbp_policy_rule(self,name,classifier,action,property_type='name',**kwargs):
        """
        Create a GBP Policy Rule
        classifier/action: Pass name-string or uuid-string
        depending on property_type
        property_type: 'uuid' or 'name'(default)
        Supported  keyword based attributes and their values:
        'shared'= 'True', 'False'
        'description'= any string
        """
        if property_type == 'name':
           classifier_id = self.verify_gbp_policy_classifier(classifier)
           action_id = self.verify_gbp_policy_action(action)
        else:
           classifier_id = classifier
           action_id = action
        body = {"policy_rule": {
				"policy_actions": [action_id],
				"policy_classifier_id": classifier_id,
				"name": name
			      }
		}
        try:
           self.client.create_policy_rule(body)
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Creating Policy Rule = %s, failed" %(name))
           return 0
        
    def update_gbp_policy_rule(self,name_uuid,property_type='name',**kwargs):
         """
         Update GBP Policy Rule editable attributes
         Supported  keyword based attributes and their values:
         'policy_classifer'= uuid of policy_classifier
         'policy_actions' = uuid of policy_action
         'shared'= 'True', 'False'
         'description'= any string
         """
         if property_type=='uuid':
            rule_id=name_uuid
         else:
            rule_id=self.verify_gbp_policy_rule(name_uuid)
         policy_rule = {}
         try:
            for arg,val in kwargs.items():
               policy_rule[arg]=val
            body = {"policy_rule":policy_rule}
            self.client.update_policy_rule(rule_id,body)
         except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Update of Policy Rule= %s, failed" %(name_uuid))
           return 0

    def verify_gbp_policy_rule(self,name):
        """
        Verify the GBP Policy Rule by passing its name and fetch its UUID
        """
        for rule in self.client.list_policy_rules()['policy_rules']:
            if rule['name'].encode('ascii') == name:
               return rule['id'].encode('ascii')
        _log.error("Policy Rule NOT Found")
        return 0

    def get_gbp_policy_rule_list(self,getdict=False):
        """
        Fetch a List of GBP Policy Rules
        getdict: 'True', will return a dictionary comprising 'name' & 'uuid'
        """
        try:
           if getdict == True:
              name_uuid = {}
              for rule in self.client.list_policy_rules()['policy_rules']:
                  name_uuid[rule['name'].encode('ascii')]= rule['id'].encode('ascii')
           else:
               rules_list = [item['id'] for item in self.client.list_policy_rules()['policy_rules']]
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Fetching Policy Rule List, failed")
           return 0
        if getdict == True:
           return name_uuid
        else:
           return rules_list

    def delete_gbp_policy_rule(self,name_uuid,property_type='name'):
         """
         Delete a GBP Policy Rule
         property_type='name' or 'uuid'
         If property_type=='name', pass 'name_string' for name_uuid,
         else pass 'uuid_string' for name_uuid param
         """
         try:
            if property_type=='name':
               rule_uuid=self.verify_gbp_policy_rule(name_uuid)
               self.client.delete_policy_rule(rule_uuid)
            else:
               self.client.delete_policy_rule(name_uuid)
         except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Deleting Policy Rule = %s, failed" %(name_uuid))
           return 0

    def create_gbp_policy_rule_set(self,name,rule_list=[],property_type='name',**kwargs):
        """
        Create a GBP Policy RuleSet
        rule_list: List of policy_rules,pass list of rule_names or rule_uuid strings
               depending on the property_type(defaulted to 'name')
        Supported  keyword based attributes and their values:
        'shared' = False,True
        'description' = any string
        """
        try:
           if property_type=='name':
              temp=rule_list
              rule_list=[]
              for rule in temp:
                  rule_uuid=self.verify_gbp_policy_rule(rule)
                  rule_list.append(rule_uuid)
           policy_rule_set = {"name": name,"policy_rules":rule_list}
           for arg,val in kwargs.items():
               policy_rule_set[arg]=val
           body = {"policy_rule_set":policy_rule_set}
           self.client.create_policy_rule_set(body)
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Creating Policy RuleSet = %s, failed" %(name))
           return 0

    def verify_gbp_policy_rule_set(self,name):
        """
        Verify the GBP Policy RuleSet by passing its name and fetch its UUID
        """
        for ruleset in self.client.list_policy_rule_sets()['policy_rule_sets']:
            if ruleset['name'].encode('ascii') == name:
               return ruleset['id'].encode('ascii')
        _log.error("Policy RuleSet NOT Found")
        return 0

    def update_gbp_policy_rule_set(self,
                                   name_uuid,
                                   property_type='name',
                                   **kwargs):
         """
         Update GBP Policy Rule editable attributes
         Supported  keyword based attributes and their values/type:
         'policy_rules'= [list of policy-rule uuid]
         'shared'= 'True', 'False'
         'description'= any string
         """
         if property_type=='uuid':
            ruleset_id=name_uuid
         else:
            ruleset_id=self.verify_gbp_policy_rule_set(name_uuid)
         policy_rule_set = {}
         try:
            for arg,val in kwargs.items():
               policy_rule_set[arg]=val
            body = {"policy_rule_set":policy_rule_set}
            self.client.update_policy_rule_set(ruleset_id,body)
         except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Update of Policy RuleSet= %s, failed" %(name_uuid))
           return 0

    def delete_gbp_policy_rule_set(self,name_uuid,property_type='name'):
         """
         Delete a GBP Policy RuleSet
         property_type='name' or 'uuid'
         If property_type=='name', pass 'name_string' for name_uuid,
         else pass 'uuid_string' for name_uuid param
         """
         try:
            if property_type=='name':
               ruleset_uuid=self.verify_gbp_policy_rule_set(name_uuid)
               self.client.delete_policy_rule_set(ruleset_uuid)
            else:
               self.client.delete_policy_rule_set(name_uuid)
         except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Deleting Policy RuleSet = %s, failed" %(name_uuid))
           return 0

    def get_gbp_policy_rule_set_list(self,getdict=False):
        """
        Fetch a List of GBP Policy RuleSet
        getdict: 'True', will return a dictionary comprising 'name' & 'uuid'
        """
        try:
           if getdict == True:
              name_uuid = {}
              for ruleset in self.client.list_policy_rule_sets()['policy_rule_sets']:
                  name_uuid[ruleset['name'].encode('ascii')]= ruleset['id'].encode('ascii')
           else:
               rulesets_list = [item['id'] for item in self.client.list_policy_rule_sets()['policy_rule_sets']]
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Fetching Policy RuleSet List, failed")
           return 0
        if getdict == True:
           return name_uuid
        else:
           return rulesets_list

    def create_gbp_policy_target_group(self,name,**kwargs):
        """
        Create a GBP Policy Target Group
        Supported  keyword based attributes and their values/types:
        'l2_policy_id' = l2policy_uuid
        'network_service_policy_id' = nsp_uuid
        'consumed_policy_rule_sets' = [list of policy_rule_set_uuid]
        'provided_policy_rule_sets' = [list policy_rule_set_uuid]
        'nextwork_service_policy' = name_uuid_network_service_policy
        'shared' = False,True
        'description' = any string
        """
        try:
           policy_target_group = {"name": name}
           for arg,val in kwargs.items():
               policy_target_group[arg]=val
           body = {"policy_target_group":policy_target_group}
           ptg_uuid = self.client.create_policy_target_group(body)['policy_target_group']['id'].encode('ascii')
           
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Creating Policy Target Group = %s, failed" %(name))
           return 0
        return ptg_uuid

    def verify_gbp_policy_target_group(self,name):
        """
        Verify the GBP Policy Target Group by passing its name and fetch its UUID
        """
        for ptg in self.client.list_policy_target_groups()['policy_target_groups']:
            if ptg['name'].encode('ascii') == name:
               return ptg['id'].encode('ascii')
        _log.error("Policy Target Group NOT Found")
        return 0


    def update_gbp_policy_target_group(self,
                                       name_uuid,
                                       property_type='name',
                                       consumed_policy_rulesets='',
                                       provided_policy_rulesets='',
                                       shared=False,
                                       network_service_policy=''):
        """
        Update the Policy Target Group
        Provide uniform property_type('name' or 'uuid') across objects
        Pass policy_rulesets as []
        """
        try:
          consumed_dict = {}
          provided_dict = {}
          if property_type == 'name':
             group_id =  self.verify_gbp_policy_target_group(name_uuid)
             if consumed_policy_rulesets:
                for ruleset in consumed_policy_rulesets:
                        id = self.verify_gbp_policy_rule_set(ruleset)
                        consumed_dict[id] = "scope"
             if provided_policy_rulesets:
                for ruleset in provided_policy_rulesets:
                        id = self.verify_gbp_policy_rule_set(ruleset)
                        provided_dict[id] = "scope"
          else:
              group_id = name_uuid
              if consumed_policy_rulesets:
                 for ruleset in consumed_policy_rulesets:
                        consumed_dict[ruleset] = "scope"
              if provided_policy_rulesets:
                for ruleset in provided_policy_rulesets:
                        provided_dict[ruleset] = "scope"
          body = {"policy_target_group" : {"shared" : shared}}
          while True:
               if consumed_policy_rulesets != '' and consumed_policy_rulesets is not None:
                  if provided_policy_rulesets!= '' and provided_policy_rulesets is not None:
                     body = {"policy_target_group" : {
                             "provided_policy_rule_sets" : provided_dict,
                             "consumed_policy_rule_sets" : consumed_dict
                                                    }
                         }
                     if network_service_policy != '' and network_service_policy is not None:
                        body["policy_target_group"]["network_service_policy_id"]=network_service_policy
                        break
                     else:
                        break
               elif consumed_policy_rulesets != '' and consumed_policy_rulesets is not None:
                    if provided_policy_rulesets == '':
                       body = {"policy_target_group" : {
                               "consumed_policy_rule_sets" : consumed_dict
                                                  }
                              }
                       if network_service_policy != '' and network_service_policy is not None:
                          body["policy_target_group"]["network_service_policy_id"]=network_service_policy
                          break
                       else:
                          break
               elif provided_policy_rulesets != '' and provided_policy_rulesets is not None:
                    if consumed_policy_rulesets == '':
                       body = {"policy_target_group" : {
                               "provided_policy_rule_sets" : provided_dict
                                                  }
                              }
                       if network_service_policy != '' and network_service_policy is not None:
                          body["policy_target_group"]["network_service_policy_id"]=network_service_policy
                          break
                       else:
                          break
               elif provided_policy_rulesets is None and consumed_policy_rulesets is None:
                    body = {"policy_target_group" : {
                            "provided_policy_rule_sets" : {},
                            "consumed_policy_rule_sets" : {}
                                                  }
                         }
                    if network_service_policy != '' and network_service_policy is not None:
                          body["policy_target_group"]["network_service_policy_id"]=network_service_policy
                          break
               elif provided_policy_rulesets == '' and consumed_policy_rulesets == '':
                    if network_service_policy is None:
                       body["policy_target_group"]["network_service_policy_id"]=None
                       break
                    if network_service_policy == '':
                       break
                    if network_service_policy != '' and network_service_policy is not None:
                       body["policy_target_group"]["network_service_policy_id"]=network_service_policy
                       break
               else:
                   print 'Do nothing'
                   break
          self.client.update_policy_target_group(group_id, body)
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Updating Policy Target Group = %s, failed" %(name_uuid))
           return 0

    def delete_gbp_policy_target_group(self,name_uuid,property_type='name'):
         """
         Delete a GBP Policy Group
         property_type='name' or 'uuid'
         If property_type=='name', pass 'name_string' for name_uuid,
         else pass 'uuid_string' for name_uuid param
         """
         try:
            if property_type=='name':
               ptg_uuid=self.verify_gbp_policy_target_group(name_uuid)
               self.client.delete_policy_target_group(ptg_uuid)
            else:
               self.client.delete_policy_target_group(name_uuid)
         except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Deleting Policy Target Group = %s, failed" %(name_uuid))
           return 0

    def get_gbp_policy_target_group_list(self,getdict=False):
        """
        Fetch a List of GBP Policy Target Group
        getdict: 'True', will return a dictionary comprising 'name' & 'uuid'
        """
        try:
           if getdict == True:
              name_uuid = {}
              for ptg in self.client.list_policy_target_groups()['policy_target_groups']:
                  name_uuid[ptg['name'].encode('ascii')]= ptg['id'].encode('ascii')
           else:
               ptgs_list = [item['id'] for item in self.client.list_policy_target_groups()['policy_target_groups']]
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Fetching Policy Target Group List, failed")
           return 0
        if getdict == True:
           return name_uuid
        else:
           return ptgs_list

    def create_gbp_policy_target(self,name,ptg_name,pt_count=1):
        """
        Create a Policy Target for a given PTG
        'pt_count'= number of PTs to be created for a given PTG
        """
        try:
           ptg_id = self.verify_gbp_policy_target_group(ptg_name)
           for i in range(pt_count):
               body = {"policy_target" : {
                                       "policy_target_group_id" : ptg_id,
                                       "name" : name
                                         }
                      }
           post_result = self.client.create_policy_target(body)['policy_target']
           pt_uuid = post_result['id'].encode('ascii')
           neutron_port_id = post_result['port_id'].encode('ascii')
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Creating PT = %s, failed" %(name))
           return 0
        return pt_uuid,neutron_port_id

    def verify_gbp_policy_target(self,name):
        """
        Verify the GBP Policy Target by passing its name
        Returns PT and its corresponding Neutron Port UUIDs
        """
        for pt in self.client.list_policy_targets()['policy_targets']:
            if pt['name'].encode('ascii') == name:
               return pt['id'].encode('ascii'),pt['port_id'].encode('ascii')
        _log.error("Policy Target NOT Found")
        return 0

    def get_gbp_policy_target_list(self):
        """
        Fetches a list of Policy Targets
        Returns a dict of Policy Targets UUIDs
        and their corresponding Neutron Port UUIDs
        """
        pt_nic_id = {}
        for pt in self.client.list_policy_targets()['policy_targets']:
            pt_nic_id[pt['id'].encode('ascii')] = pt['port_id'].encode('ascii')
        return pt_nic_id

    def delete_gbp_policy_target(self,name_uuid,property_type='name'):
         """
         Delete a GBP Policy Target
         property_type='name' or 'uuid'
         If property_type=='name', pass 'name_string' for name_uuid,
         else pass 'uuid_string' for name_uuid param
         """
         try:
            if property_type=='name':
               pt_uuid=self.verify_gbp_policy_target(name_uuid)
               self.client.delete_policy_target(pt_uuid)
            else:
               self.client.delete_policy_target(name_uuid)
         except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Deleting Policy Target = %s, failed" %(name_uuid))
           return 0

    def create_gbp_l3policy(self,name,**kwargs):
        """
        Create a GBP L3Policy
        Supported  keyword based attributes and their values/type:
        'ip_pool' = string (eg:'1.2.3.0/24')
        'subnet_prefix_length' = integer
        'external_segments': {}
        'shared': True, False
        'description': string
        """
        try:
           l3policy={"name":name}
           for arg,val in kwargs.items():
               if arg == 'external_segments':
                  val = {val:[]}
               l3policy[arg]=val
           body = {"l3_policy": l3policy}
           l3p_uuid = self.client.create_l3_policy(body)['l3_policy']['id'].encode('ascii')
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Creating L3Policy = %s, failed" %(name))
           return 0
        return l3p_uuid

    def verify_gbp_l3policy(self,name):
        """
        Verify the GBP L3Policy by passing its name and fetch its UUID
        """
        for l3p in self.client.list_l3_policies()['l3_policies']:
            if l3p['name'].encode('ascii') == name:
               return l3p['id'].encode('ascii')
        _log.error("L3Policy NOT Found")
        return 0

    def delete_gbp_l3policy(self,name_uuid,property_type='name'):
         """
         Delete a GBP L3Policy
         property_type='name' or 'uuid'
         If property_type=='name', pass 'name_string' for name_uuid,
         else pass 'uuid_string' for name_uuid param
         """
         try:
            if property_type=='name':
               l3p_uuid=self.verify_gbp_l3policy(name_uuid)
               self.client.delete_l3_policy(l3p_uuid)
            else:
               self.client.delete_l3_policy(name_uuid)
         except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Deleting L3Policy = %s, failed" %(name_uuid))
           return 0

    def update_gbp_l3policy(self,name_uuid,property_type='name',**kwargs):
         """
         Update GBP L3Policy editable attributes
         Supported keyword based attributes and their values/type:
         'subnet_prefix_length' = integer'
         'shared'= 'True', 'False'
         'description'= any string
         'external_segments'= UUID of the external segment 
         """
         if property_type=='uuid':
            l3p_id=name_uuid
         else:
            l3p_id=self.verify_gbp_l3policy(name_uuid)
         l3p = {}
         try:
            for arg,val in kwargs.items():
               if arg == 'external_segments':
                  val = {val:[]}
               l3p[arg]=val
            body = {"l3_policy":l3p}
            self.client.update_l3_policy(l3p_id,body)
         except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Update of L3Policy = %s, failed" %(name_uuid))
           return 0
 
    def get_gbp_l3policy_list(self,getdict=False):
        """
        Fetch a List of GBP L3Policy
        getdict: 'True', will return a dictionary comprising 'name' & 'uuid'
        """
        try:
           if getdict == True:
              name_uuid = {}
              for l3p  in self.client.list_l3_policies()['l3_policies']:
                  name_uuid[l3p['name'].encode('ascii')]= l3p['id'].encode('ascii')
           else:
               l3p_list = [item['id'] for item in self.client.list_l3_policies()['l3_policies']]
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Fetching L3Policy List, failed")
           return 0
        if getdict == True:
           return name_uuid
        else:
           return l3p_list

    def create_gbp_l2policy(self,name,**kwargs):
        """
        Create a GBP L2Policy
        Supported  keyword based attributes and their values/type:
        'l3_policy_id' = string (eg:'1.2.3.0/24')
        'subnet_prefix_length' = integer
        'shared': True, False
        'description': string
        """
        try:
           l2policy={"name":name}
           for arg,val in kwargs.items():
               l2policy[arg]=val
           body = {"l2_policy": l2policy}
           l2p_uuid = self.client.create_l2_policy(body)['l2_policy']['id'].encode('ascii')
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Creating L2Policy = %s, failed" %(name))
           return 0
        return l2p_uuid

    def verify_gbp_l2policy(self,name):
        """
        Verify the GBP L2Policy by passing its name and fetch its UUID
        """
        try:
          for l2p in self.client.list_l2_policies()['l2_policies']:
            if l2p['name'].encode('ascii') == name:
               return l2p['id'].encode('ascii')
          _log.error("L2Policy NOT Found")     
          return 0
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Verifying L2Policy = %s, failed" %(name))
           return 0

    def delete_gbp_l2policy(self,name_uuid,property_type='name'):
         """
         Delete a GBP L2Policy
         property_type='name' or 'uuid'
         If property_type=='name', pass 'name_string' for name_uuid,
         else pass 'uuid_string' for name_uuid param
         """
         try:
            if property_type=='name':
               l2p_uuid=self.verify_gbp_l2policy(name_uuid)
               self.client.delete_l2_policy(l2p_uuid)
            else:
               self.client.delete_l2_policy(name_uuid)
         except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Deleting L2Policy = %s, failed" %(name_uuid))
           return 0

    def get_gbp_l2policy_list(self,getdict=False):
        """
        Fetch a List of GBP L2Policy
        getdict: 'True', will return a dictionary comprising 'name' & 'uuid'
        """
        try:
           if getdict == True:
              name_uuid = {}
              for l2p  in self.client.list_l2_policies()['l2_policies']:
                  name_uuid[l2p['name'].encode('ascii')]= l2p['id'].encode('ascii')
           else:
               l2p_list = [item['id'] for item in self.client.list_l2_policies()['l2_policies']]
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Fetching L2Policy List, failed")
           return 0
        if getdict == True:
           return name_uuid
        else:
           return l2p_list

    def create_gbp_external_segment(self,name,**kwargs):
        """
        Create an External Segment
        Return Ext_Seg_uuid
        Supported  keyword based attributes and their values/type:
        'cidr' = string
        'external_policies'= [](list of external-policies)
        'external_routes' = [{'destination'=<>,'nexthop'=<>}](Pass list of dictionaries for each dest/nexthop pair)
        'nexthop' = string('address should be part of the cidr')
        'shared': True, False
        'description': string
        """
        try:
           external_segment={"name":name}
           for arg,val in kwargs.items():
               if arg == 'external_policies' or arg == 'external_routes':
                  if not isinstance(val,list):
                     raise TypeError
               external_segment[arg]=val
           body = {"external_segment": external_segment}
           ext_seg_uuid = self.client.create_external_segment(body)['external_segment']['id'].encode('ascii')
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Creating External Segment = %s, failed" %(name))
           return 0
        return ext_seg_uuid

    def delete_gbp_external_segment(self,uuid):
         """
         Delete a GBP External Segment
         """
         try:
             self.client.delete_external_segment(uuid)
         except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Deleting External Segment = %s, failed" %(uuid))
           return 0

    def update_gbp_external_segment(self,uuid,**kwargs):
        """
        Update an External Segment
        Supported  keyword based attributes and their values/type:
        'cidr' = string
        'external_policies'= [](list of external-policies)
        'external_routes' = [{'destination':<>,'nexthop':<>}](Pass list of dictionaries for each dest/nexthop pair)
        'nexthop' = string('address should be part of the cidr')
        'shared': True, False
        'description': string
        """
        external_segment = {}
        try:
            for arg,val in kwargs.items():
               external_segment[arg]=val
            body = {"external_segment":external_segment}
            self.client.update_external_segment(uuid,body)
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Update of External Segment = %s, failed" %(uuid))
           return 0

    def get_gbp_external_segment_list(self,getdict=False):
        """
        Fetch a List of GBP External Segments
        getdict: 'True', will return a dictionary comprising 'name' & 'uuid'
        """
        try:
           if getdict == True:
              name_uuid = {}
              for extseg in self.client.list_external_segments()['external_segments']:
                  name_uuid[extseg['name'].encode('ascii')]= extseg['id'].encode('ascii')
           else: # Return list of ids
               extseg_list = [item['id'] for item in self.client.list_external_segments()['external_segments']]
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Fetching External Segment List, failed")
           return 0
        if getdict == True:
           return name_uuid
        else:
           return extseg_list

    def create_gbp_nat_pool(self,name,**kwargs):
        """
        Create a NAT Pool
        Supported keywords based attributes and their values/type:
        'ip_pool' = string(must be exact or subnet of cidr)
        'external_segment_id' = string(name/uuid)
        """
        nat_pool = {'name':name}
        try:
            for arg,val in kwargs.items():
                nat_pool[arg]=val
            body = {"nat_pool":nat_pool}
            nat_pool_uuid = self.client.create_nat_pool(body)['nat_pool']['id'].encode('ascii')
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           return 0 
        return nat_pool_uuid

    def delete_gbp_nat_pool(self,uuid):
         """
         Delete a GBP NAT Pool
         """
         try:
             self.client.delete_nat_pool(uuid)
         except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Deleting NAT Pool %s, failed" %(uuid))
           return 0

    def get_gbp_nat_pool_list(self,getdict=False):
        """
        Fetch a List of GBP NAT Pools
        getdict: 'True', will return a dictionary comprising 'name' & 'uuid'
        """
        try:
           if getdict == True:
              name_uuid = {}
              for natpool in self.client.list_nat_pools()['nat_pools']:
                  name_uuid[natpool['name'].encode('ascii')]= natpool['id'].encode('ascii')
           else: # Return list of ids
               natpool_list = [item['id'] for item in self.client.list_nat_pools()['nat_pools']]
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Fetching NAT Pool List, failed")
           return 0
        if getdict == True:
           return name_uuid
        else:
           return natpool_list

    def update_gbp_nat_pool(self,uuid,**kwargs):
        """
        Update a NAT Pool
        Supported keywords based attributes and their values/type:
        'ip_pool' = string(must be exact or subnet of cidr)
        'external_segment_id' = string(name/uuid)
        """
        nat_pool = {}
        try:
            for arg,val in kwargs.items():
                nat_pool[arg]=val
            body = {"nat_pool":nat_pool}
            self.client.update_nat_pool(uuid,body)
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Update of NAT Pool = %s, failed" %(uuid))
           return 0

    def create_gbp_network_service_policy_for_nat(self,name,shared=False):
        """
        Create Network Service Policy
        """
        network_service_params = [{"type": "ip_pool",
                                   "name": "nat", 
                                   "value": "nat_pool"}]
        nsp_nat = {'name' : name, 'network_service_params' : network_service_params}
        try:
           body = {'network_service_policy':nsp_nat}
           nsp_nat_uuid = self.client.create_network_service_policy(body)['network_service_policy']['id'].encode('ascii')
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Creating NAT NSP failed")
           return 0
        return nsp_nat_uuid   

    def delete_gbp_network_service_policy(self,nspuuid=''):
        """
        Delete Network Service Policy
        """
        try:
           if nspuuid != '':
              self.client.delete_network_service_policy(nspuuid)
           else:
              nsp_list = self.client.list_network_service_policies()['network_service_policies']
              for nsp in nsp_list:
                  nspuuid = nsp['id']
                  self.client.delete_network_service_policy(nspuuid)
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Deleting NAT NSP = %s, failed" %(nspuuid))
           return 0
        
    def create_gbp_external_policy(self,name,**kwargs):
        """
        Create the External Policy
        Provide uniform property_type('name' or 'uuid') across objects
        Pass external_segments as a List
        """

        try:
           external_policy = {"name": name}
           for arg,val in kwargs.items():
               external_policy[arg]=val
           body = {"external_policy":external_policy}
           extpol_uuid = self.client.create_external_policy(body)['external_policy']['id'].encode('ascii')
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Creating External Policy = %s, failed" %(name))
           return 0
        return extpol_uuid


    def update_gbp_external_policy(self,
                                   name_uuid,
                                   property_type='name',
                                   consumed_policy_rulesets=None,
                                   provided_policy_rulesets=None, 
                                   external_segments=[],
                                   shared=False):
        """
        Update the External Policy
        Provide uniform property_type('name' or 'uuid')
        across objects EXCEPT external_segments(only id)
        Pass external_segments as a List
        """
        try:
          consumed_prs = {}
          provided_prs = {}
          if property_type == 'name':
             policy_id =  self.verify_gbp_external_policy(name_uuid)
             if consumed_policy_rulesets:
                for ruleset in consumed_policy_rulesets:
                        id = self.verify_gbp_policy_rule_set(ruleset)
                        consumed_prs[id] = "scope"
             if provided_policy_rulesets:
                for ruleset in provided_policy_rulesets:
                        id = self.verify_gbp_policy_rule_set(ruleset)
                        provided_prs[id] = "scope"
          else:
              policy_id = name_uuid
              if consumed_policy_rulesets:
                 for ruleset in consumed_policy_rulesets:
                        consumed_prs[ruleset] = "scope"
              if provided_policy_rulesets:
                for ruleset in provided_policy_rulesets:
                        provided_prs[ruleset] = "scope"
          body = {"external_policy" : {"shared" : shared}}
          while True:
               if consumed_policy_rulesets is not None and provided_policy_rulesets is not None:
                  body["external_policy"]["provided_policy_rule_sets"] = provided_prs
                  body["external_policy"]["consumed_policy_rule_sets"] = consumed_prs
                  if external_segments != []:
                     body["external_policy"]["external_segments"] = external_segments
                  break
               elif consumed_policy_rulesets is not None and provided_policy_rulesets is None:
                  body["external_policy"]["consumed_policy_rule_sets"] = consumed_prs
                  if external_segments != []:
                     body["external_policy"]["external_segments"] = external_segments
                  break
               elif provided_policy_rulesets is not None and consumed_policy_rulesets is None:
                  body["external_policy"]["provided_policy_rule_sets"] = provided_prs
                  if external_segments != []:
                     body["external_policy"]["external_segments"] = external_segments
                  break
               elif provided_policy_rulesets is None and consumed_policy_rulesets is None:
                  if external_segments != []:
                     body["external_policy"]["external_segments"] = external_segments
                  break
               else:
                  break
          self.client.update_external_policy(policy_id, body)
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Updating External Policy = %s, failed" %(name_uuid))
           return 0

    def delete_gbp_external_policy(self,uuid):
         """
         Delete a GBP External Policy
         """
         try:
             self.client.delete_external_policy(uuid)
         except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Deleting External Policy %s, failed" %(uuid))
           return 0

    def get_gbp_external_policy_list(self,getdict=False):
        """
        Fetch a List of GBP External Policies
        getdict: 'True', will return a dictionary comprising 'name' & 'uuid'
        """
        try:
           if getdict == True:
              name_uuid = {}
              for extpol in self.client.list_external_policies()['external_policies']:
                  name_uuid[extpol['name'].encode('ascii')]= extpol['id'].encode('ascii')
           else: # Return list of ids
               extpol_list = [item['id'] for item in self.client.list_external_policies()['external_policies']]
        except Exception as e:
           _log.error("\nException Error: %s\n" %(e))
           _log.error("Fetching External Policies List, failed")
           return 0
        if getdict == True:
           return name_uuid
        else:
           return extpol_list

    def verify_gbp_external_policy(self,name):
        """
        Verify the GBP External Policy by passing its name and fetch its UUID
        """
        for extpol in self.client.list_external_policies()['external_policies']:
            if extpol['name'].encode('ascii') == name:
               return extpol['id'].encode('ascii')
        _log.error("External Policy Group NOT Found")
        return 0

    def verify_gbp_any_object(self,obj,obj_uuid,**kwargs):
        """
        Verify any objects and its attributes
        Pass the keywords as it appears in a show cmd
        Valid objects are:: l3_policy,l2_policy,policy_target_group,
        policy_target,nat_pool,external_segment,external_policy and
        others as it appears in a gbp show CLI
        keywords:: the string should be exact as seen in gbp show CLI
        values:: should be passed as the datatype as it appears in CLI
        Example: For obj: l3_policy, key=l2_policies, val=['uuid of l2p']
        """
        if obj == 'l3_policy':
           attributes = self.client.show_l3_policy(obj_uuid)[obj]
           for arg,val in kwargs.items():
               if arg == 'external_segments':
                  # TODO: will revist this to handle single L3P
                  # associated to multiple ExtSeg.
                  if val not in attributes[arg].keys():
                     return 0
               else:
                   if isinstance(val,list) and isinstance(attributes[arg],list):
                      if set(attributes[arg]) != set(val):
                         _log.error("Attribute %s and its Value %s NOT found in Object %s %s" %(arg,val,obj,obj_uuid))
                         return 0
                   if isinstance(attributes[arg],list) and isinstance(val,str):
                      if val not in attributes[arg]:
                         _log.error("Attribute %s and its Value %s NOT found in Object %s %s" %(arg,val,obj,obj_uuid))
                         return 0
        if obj == 'l2_policy':
           attributes = self.client.show_l2_policy(obj_uuid)[obj]
           for arg,val in kwargs.items():
               if arg == 'policy_target_groups':
                  if val not in attributes[arg]:
                     _log.error("Attribute %s and its Value %s NOT found in Object %s %s" %(arg,val,obj,obj_uuid))
                     return 0
               else:
                   if attributes[arg] != val:
                      _log.error("Attribute %s and its Value %s NOT found in Object %s %s" %(arg,val,obj,obj_uuid))
                      return 0
        if obj == 'policy_target_group':
           attributes = self.client.show_policy_target_group(obj_uuid)[obj]
           for arg,val in kwargs.items():
               if isinstance(val,list) and isinstance(attributes[arg],list):
                  unmatched = [item for item in val if item not in attributes[arg]]
                  if len(unmatched) > 0:
                     _log.error("Attribute %s and its Value %s NOT found in Object %s %s" %(arg,val,obj,obj_uuid))
                     return 0
               elif isinstance(attributes[arg],list) and isinstance(val,str):
                      if val not in attributes[arg]:
                         _log.error("Attribute %s and its Value %s NOT found in Object %s %s" %(arg,val,obj,obj_uuid))
                         return 0
               else:
                   if attributes[arg] != val:
                      _log.error("Attribute %s and its Value %s NOT found in Object %s %s" %(arg,val,obj,obj_uuid))
                      return 0
        if obj == 'external_segment':
           attributes = self.client.show_external_segment(obj_uuid)[obj]
           for arg,val in kwargs.items():
               if isinstance(val,list) and isinstance(attributes[arg],list):
                  unmatched = [item for item in val if item not in attributes[arg]]
                  if len(unmatched) > 0:
                     _log.error("Attribute %s and its Value %s NOT found in Object %s %s" %(arg,val,obj,obj_uuid))
                     return 0
               elif isinstance(attributes[arg],list) and isinstance(val,str):
                      if val not in attributes[arg]:
                         _log.error("Attribute %s and its Value %s NOT found in Object %s %s" %(arg,val,obj,obj_uuid))
                         return 0   
               else:
                   if attributes[arg] != val:
                      _log.error("Attribute %s and its Value %s NOT found in Object %s %s" %(arg,val,obj,obj_uuid))
                      return 0
        if obj == 'external_policy':
           attributes = self.client.show_external_policy(obj_uuid)[obj]
           for arg,val in kwargs.items():
               if attributes[arg] != val:
                  _log.error("Attribute %s and its Value %s NOT found in Object %s %s" %(arg,val,obj,obj_uuid))
                  return 0

    def gbp_ext_route_add_to_extseg_util(self,extseg_id,extseg_name,route='0.0.0.0/0'):
        """
        Utility Method to add ext_routes to Ext_Seg
        ONLY needed for NAT DP TESTs
        """
        if extseg_name == 'Datacenter-Out':
           cmd = 'crudini --get /etc/neutron/neutron.conf apic_external_network:%s cidr_exposed' %(extseg_name)
           out = re.search('\\b(\d+.\d+.\d+).\d+.*' '', getoutput(cmd), re.I)
           route = out.group(1)+'.0/24'
        cmd = 'crudini --get /etc/neutron/neutron.conf apic_external_network:%s gateway_ip' %(extseg_name)
        route_gw = getoutput(cmd)
        _log.info("Route to be added to External Segment %s with GW %s  == %s" %(extseg_name,route_gw,route))
        self.update_gbp_external_segment(extseg_id,external_routes=[{'destination' : route, 'nexthop' : route_gw}])

