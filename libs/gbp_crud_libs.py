#!/usr/bin/env python
from gbpclient.v2_0 import client as gbpclient

class GBPCrud(object):
    """
    The intent of this Base Class is for doing CRUD and associated operations
    by calling directly the APIs of the GBP Python Client
    """

    def __init__(self,ostack_controller, username='admin', password='noir0123', tenant='admin'):
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
           _log.info("\nException Error: %s\n" %(e))
           _log.info("Create of Policy Action= %s, failed" %(name))
           return 0
    
    def verify_gbp_policy_action(self,name):
        """
        Verify the GBP Policy Action by passing its name
        """
        for action in self.client.list_policy_actions()['policy_actions']:
            if action['name'].encode('ascii') == name:
               return action['id'].encode('ascii')
            else:
               return 0
 
    def get_gbp_policy_action_list(self,getlist=False):
        """
        Fetch a List of GBP Policy Actions
        getlist: 'True', will return a dictionary comprising 'name' & 'uuid'
        """
        try:
           if getlist == True:
              name_uuid = {}
              for action in self.client.list_policy_actions()['policy_actions']:
                  name_uuid[action['name'].encode('ascii')]= action['id'].encode('ascii')
           else:
               pas = self.client.list_policy_actions()       
        except Exception as e:
           _log.info("\nException Error: %s\n" %(e))
           _log.info("Fetching Policy Action List, failed")
           return 0
        if getlist == True:
           return name_uuid
        else:
           return pas 

    def get_gbp_policy_action_show(self,uuid):
        """
        Fetch the details of a given GBP Policy Action
        """
        try:
           pa = self.client.show_policy_action(uuid)
        except Exception as e:
           _log.info("\nException Error: %s\n" %(e))
           _log.info("Fetching a given Policy Action=%s, failed" %(uuid))
           return 0
        return pa

    def delete_gbp_policy_action(self,name_uuid,property_type='name'):
         """
         Delete a GBP Policy Action
         property_type='name' or 'uuid'
         If property_type=='name', pass 'name_string' for name_uuid, else pass 'uuid_string' for name_uuid param
         """
         try:
            if property_type=='name':
               action_uuid=self.verify_gbp_policy_action(name_uuid)
               self.client.delete_policy_action(action_uuid)
            else:
               self.client.delete_policy_action(name_uuid)
         except Exception as e:
           _log.info("\nException Error: %s\n" %(e))
           _log.info("Deleting Policy Action = %s, failed" %(name))
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
           _log.info("\nException Error: %s\n" %(e))
           _log.info("Create of Policy Classifier= %s, failed" %(name))
           return 0

    def update_gbp_policy_classifier(self,name_uuid,property_type='name',**kwargs):
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
           _log.info("\nException Error: %s\n" %(e))
           _log.info("Update of Policy Classifier= %s, failed" %(name_uuid))
           return 0

    def get_gbp_policy_classifier_list(self,getlist=False):
        """
        Fetch a List of GBP Policy Classifiers
        getlist: 'True', will return a dictionary comprising 'name' & 'uuid'
        """
        try:
           if getlist == True:
              name_uuid = {}
              for classifier in self.client.list_policy_classifiers()['policy_classifiers']:
                  name_uuid[classifier['name'].encode('ascii')]= classifier['id'].encode('ascii')
           else:
               pcs = self.client.list_policy_classifiers()
        except Exception as e:
           _log.info("\nException Error: %s\n" %(e))
           _log.info("Fetching Policy Classifier List, failed")
           return 0
        if getlist == True:
           return name_uuid
        else:
           return pcs

    def delete_gbp_policy_classifier(self,name_uuid,property_type='name'):
         """
         Delete a GBP Policy Classifier
         property_type='name' or 'uuid'
         If property_type=='name', pass 'name_string' for name_uuid, else pass 'uuid_string' for name_uuid param
         """
         try:
            if property_type=='name':
               class_uuid=self.verify_gbp_policy_classifier(name_uuid)
               self.client.delete_policy_classifer(class_uuid)
            else:
               self.client.delete_policy_classifier(name_uuid)
         except Exception as e:
           _log.info("\nException Error: %s\n" %(e))
           _log.info("Deleting Policy Classifier = %s, failed" %(name))
           return 0

    def verify_gbp_policy_classifier(self,name):
        """
        Verify the GBP Policy Classifier by passing its name and fetch its UUID
        """
        for classifier in self.client.list_policy_classifiers()['policy_classifiers']:
            if classifier['name'].encode('ascii') == name:
               return classifier['id'].encode('ascii')
            else:
               return 0

    def create_gbp_policy_rule(self,name,classifier,action,property_type='name',**kwargs):
        """
        Create a GBP Policy Rule
        classifier/action: Pass name-string or uuid-string depending on property_type
        property_type: 'uuid' or 'name'(default)
        Supported  keyword based attributes and their values:
        'shared'= 'True', 'False'
        'description'= any string
        """
        if property_type == 'name':
           classifier_id = self.verify_policy_classifier(classifier)
           action_id = self.verify_policy_actions(action)
        else:
           classifier_id = classifier
           action_id = action
        body = {"policy_rule": {
				"policy_actions": action_id,
				"policy_classifier_id": classifier_id,
				"name": name
			      }
		}
        try:
           self.client.create_policy_rule(body)
        except Exception as e:
           _log.info("\nException Error: %s\n" %(e))
           _log.info("Creating Policy Classifier = %s, failed" %(name))
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
           _log.info("\nException Error: %s\n" %(e))
           _log.info("Update of Policy Rule= %s, failed" %(name_uuid))
           return 0

    def verify_gbp_policy_rule(self,name):
        """
        Verify the GBP Policy Rule by passing its name and fetch its UUID
        """
        for rule in self.client.list_policy_rules()['policy_rules']:
            if rule['name'].encode('ascii') == name:
               return rule['id'].encode('ascii')
            else:
               return 0

    def get_gbp_policy_rule_list(self,getlist=False):
        """
        Fetch a List of GBP Policy Rules
        getlist: 'True', will return a dictionary comprising 'name' & 'uuid'
        """
        try:
           if getlist == True:
              name_uuid = {}
              for rule in self.client.list_policy_rules()['policy_rules']:
                  name_uuid[rule['name'].encode('ascii')]= rule['id'].encode('ascii')
           else:
               rules = self.client.list_policy_rules()
        except Exception as e:
           _log.info("\nException Error: %s\n" %(e))
           _log.info("Fetching Policy Rule List, failed")
           return 0
        if getlist == True:
           return name_uuid
        else:
           return rules

    def delete_gbp_policy_rules(self,name_uuid,property_type='name'):
         """
         Delete a GBP Policy Rule
         property_type='name' or 'uuid'
         If property_type=='name', pass 'name_string' for name_uuid, else pass 'uuid_string' for name_uuid param
         """
         try:
            if property_type=='name':
               rule_uuid=self.verify_gbp_policy_rule(name_uuid)
               self.client.delete_policy_rule(rule_uuid)
            else:
               self.client.delete_policy_rule(name_uuid)
         except Exception as e:
           _log.info("\nException Error: %s\n" %(e))
           _log.info("Deleting Policy Rule = %s, failed" %(name))
           return 0

    def create_gbp_policy_ruleset(self,name,rule_list=[],property_type='name',**kwargs):
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
           self.clients.create_policy_rule_set(body)
        except Exception as e:
           _log.info("\nException Error: %s\n" %(e))
           _log.info("Creating Policy RuleSet = %s, failed" %(name))
           return 0

    def verify_gbp_policy_rule_set(self,name):
        """
        Verify the GBP Policy RuleSet by passing its name and fetch its UUID
        """
        for ruleset in self.client.list_policy_rule_sets()['policy_rule_sets']:
            if ruleset['name'].encode('ascii') == name:
               return ruleset['id'].encode('ascii')
            else:
               return 0

    def update_gbp_policy_rule_set(self,name_uuid,property_type='name',**kwargs):
         """
         Update GBP Policy Rule editable attributes
         Supported  keyword based attributes and their values:
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
           _log.info("\nException Error: %s\n" %(e))
           _log.info("Update of Policy RuleSet= %s, failed" %(name_uuid))
           return 0

    def delete_gbp_policy_rule_set(self,name_uuid,property_type='name'):
         """
         Delete a GBP Policy RuleSet
         property_type='name' or 'uuid'
         If property_type=='name', pass 'name_string' for name_uuid, else pass 'uuid_string' for name_uuid param
         """
         try:
            if property_type=='name':
               ruleset_uuid=self.verify_gbp_policy_rule_set(name_uuid)
               self.client.delete_policy_rule_set(ruleset_uuid)
            else:
               self.client.delete_policy_rule_set(name_uuid)
         except Exception as e:
           _log.info("\nException Error: %s\n" %(e))
           _log.info("Deleting Policy RuleSet = %s, failed" %(name))
           return 0

    def create_gbp_policy_target_group(self,name,**kwargs):
        """
        Create a GBP Policy Target Group
        Supported  keyword based attributes and their values/types:
        'l2_policy-id' = l2policy_uuid
        'network_service_policy_id' = nsp_uuid
        'consumed_policy_rule_sets' = [list of policy_rule_set_uuid]
        'provided_policy_rule_sets' = [list policy_rule_set_uuid]
        'shared' = False,True
        'description' = any string
        """
        try:
           policy_target_group = {"name": name}
           for arg,val in kwargs.items():
               policy_target_group[arg]=val
           body = {"policy_target_group":policy_target_group}
           self.clients.create_policy_target_group(body)
        except Exception as e:
           _log.info("\nException Error: %s\n" %(e))
           _log.info("Creating Policy Target Group = %s, failed" %(name))
           return 0

    def verify_gbp_policy_target_group(self,name):
        """
        Verify the GBP Policy Target Group by passing its name and fetch its UUID
        """
        for ptg in self.client.list_policy_rule_groups()['policy_target_groups']:
            if ptg['name'].encode('ascii') == name:
               return ptg['id'].encode('ascii')
            else:
               return 0

    def update_gbp_policy_target_group(self, name, consumed_policy_rulesets=None, provided_policy_rulesets=None):
		# Lookup the group id from the group name
		group_id =  self.verify_policy_target_group(name)
		consumed_dict = {}
		provided_dict = {}
		if consumed_policy_rulesets:
			for ruleset in consumed_policy_rulesets:
				id = self.verify_policy_rule_set(ruleset)
				consumed_dict[id] = "scope"
		if provided_policy_rulesets:
			for ruleset in provided_policy_rulesets:
				id = self.verify_policy_rule_set(ruleset)
				provided_dict[id] = "scope"
		
		body = {
			"policy_target_group" : {
				"provided_policy_rule_sets" : provided_dict,
				"consumed_policy_rule_sets" : consumed_dict
			}
		}
		self.clients.update_policy_target_group(group_id, body)
