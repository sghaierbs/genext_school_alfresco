# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID
from openerp.exceptions import except_orm,ValidationError, Warning
from alfrescoRESTful import Client
from functools import wraps
import wrapt # needs to be installed in aafter fresh odoo installation



@wrapt.decorator
def api(wrapped, instance, args, kwargs):
    if not hasattr(instance, 'alfresco'):
        print '#### adding alfresco object'
        alfresco = Connector(instance)
        setattr(instance, 'alfresco', alfresco)
    else:
        print '#### using the old alfresco object'
    return wrapped(*args, **kwargs)


class Connector:

    def __init__(self, recordset, block_on_empty_config= True, debug=1):
        self._client = None     # client object to performe REST calls against alfresco REST-API
        self._config = None     # record that conatains the json_tree and enabled instance_id
        self._instance = None   # record that conatains the baseUrl, login and password
        self.recordset = recordset  # an odoo recordset object ref to perform ORM actions

        self._admin = None
        self._user = None

        self.as_admin = False
        self.block_on_empty_config = block_on_empty_config
        self.debug = debug


    def _getClient(self):
        """ open a session for the current logged in user  """
        if not self._instance:
            self._getAlfrescoInstance() # will call _getAlfrescoConfi()
        self._client = self._connect()
        return self._client       

    def _getAdmin(self):
        """ open a session for the admin user """
        self.as_admin = True
        if not self._instance:
            self._getAlfrescoInstance() # will call _getAlfrescoConfi()
        if not self._admin:
            self._admin = self._connect()
        return self._admin

    def _getUser(self):
        """ open a session for the current user, similar to _getClient()"""
        self.as_admin = False
        if not self._instance:
            self._getAlfrescoInstance() # will call _getAlfrescoConfi()
        if not self._user:
            self._user = self._connect()
        return self._user

    def _getInstance(self):
        print 'calling _getInstance'
        if not self._instance:
            self._getAlfrescoInstance() # will call _getAlfrescoConfi()
        return self._instance

    def _getConfig(self):
        print 'calling _getConfig'
        if not self._config:
            self._getAlfrescoConfig()
        return self._config


    admin = property(_getAdmin)
    user = property(_getUser)
    client = property(_getClient)
    instance = property(_getInstance)
    config = property(_getConfig)

    def switch(self, as_admin):
        self.as_admin = as_admin
        if self._client:
            self._client.logoutUser()
        self._client = self._connect()
        return self._client
        
   

    def getClient(self, as_admin=False, block_on_empty_config=False, debug=1):
        self.as_admin = as_admin
        self.block_on_empty_config = block_on_empty_config
        self.debug = debug
        self._getAlfrescoInstance() # will call _getAlfrescoConfi()
        self._client = self._connect()
        return self.client

    def getConfig(self, block_on_empty_config=False, debug=1):
        self.block_on_empty_config = block_on_empty_config
        self.debug = debug
        self._getAlfrescoConfig()
        return self.config

    def getInstance(self, block_on_empty_config=False, debug=1):
        self.block_on_empty_config = block_on_empty_config
        self.debug = debug
        self._getAlfrescoInstance()
        return self.instance

    def _connect(self):
        if self.recordset != None:
            session = Client(url=self._instance.baseUrl, debug=self.debug)
            # current user is the administrator --> load login and password from alfresco config
            # or action needs to be performed as admin user
            if SUPERUSER_ID in self.recordset.env.user.ids or self.as_admin:
                response = session.loginUser(self._instance.username, self._instance.password)
                if response['success'] == True:
                    print '-----------------CONNECTED AS ADMIN'
                    return session
                else:
                    print '----------------- UNABLE TO CONNECT AS ADMIN-------------------'
                    if self.block_on_empty_config:
                        raise ValidationError(response['error'])
                    else:
                        return False
            else:
                response = session.loginUser('user_%s'%self.recordset.env.user.id, self.recordset.env.user.alfresco_password)
                if response['success'] == True:
                    print '-----------------CONNECTED AS ',self.recordset.env.user.name
                    return session
                else:
                    print '----------------- UNABLE TO CONNECT AS USER-------------------'
                    if self.block_on_empty_config:
                        raise ValidationError(response['error'])
                    else:
                        return False

    def _getAlfrescoInstance(self):
        print 'calling _getAlfrescoInstance'
        if self._config == None:
            self._config = self._getAlfrescoConfig()
        if self._config.alfresco_instance_id:
            self._instance = self._config.alfresco_instance_id
        elif self.block_on_empty_config:
            raise ValidationError('No DMS  settings found, contact your system administrator for further information')
        return self._instance


    def _getAlfrescoConfig(self):
        print 'calling _getAlfrescoConfig'
        config = self.recordset.env['school.alfresco.config'].sudo().search([('enabled', '=', 'enabled')])
        if len(config) == 1:
            self._config = config
            # school.alfresco.config contains a confirmed record  -- > domain="[('instance_state', '=', 'confirmed')]"
            return self._config
        else:
            if self.debug == 1:
                print '#[class %s][method %s] -------> Unable to get [school.alfresco.config] record'%(self.__class__.__name__, inspect.getframeinfo(inspect.currentframe()).function)
            if self.block_on_empty_config:
                raise ValidationError('No DMS  settings found, contact your system administrator for further information')

