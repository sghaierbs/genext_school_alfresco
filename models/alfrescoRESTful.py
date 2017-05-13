# -*- coding: utf-8 -*-
import cookielib
import urllib2
import urllib
import requests
import json
import base64
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import inspect
from odoo.exceptions import ValidationError



class NodeAction:
    DELETE_NODE = 0
    UPDATE_NODE = 1
    GET_NODE = 2
    LIST_NODE_CHILDREN = 3
    CREATE_NODE = 4
    UPDATE_NODE_CONTENT = 5
    GET_NODE_CONTENT = 6


class Client:

    BASE_URL = 'alfresco/api/-default-/public'
    # Login
    LOGIN_URL = 'authentication/versions/1/tickets'
    LOGOUT_URL = 'authentication/versions/1/tickets/-me-'
    VALIDATE_TICKET = 'authentication/versions/1/tickets/-me-'
    # Sites
    GET_ALL_SITES = 'alfresco/versions/1/sites'
    CREATE_SITE = 'alfresco/versions/1/sites'
    UPDATE_SITE = 'alfresco/versions/1/sites'
    DELETE_SITE = 'alfresco/versions/1/sites'
    CREATE_SITE_MEMBERSHIP = 'alfresco/versions/1/sites'
    # Groups
    ADD_GROUP_TO_SITE = 'alfresco/service/api/sites'
    REMOVE_GROUP_FROM_SITE = 'alfresco/service/api/sites'
    # Users
    CREATE_USER = 'alfresco/versions/1/people'
    UPDATE_USER = 'alfresco/versions/1/people'
    DELETE_USER = '/alfresco/service/api/people'
    GET_USER_GROUPS = 'alfresco/service/api/people'
    # Nodes
    CREATE_NODE = 'alfresco/versions/1/nodes/-my-/children'
    NODE_SHARE_URL = 'alfresco/service/api/sites/shareUrl'
    NODE_CONTENT = 'alfresco/versions/1/nodes'

    CREATE_USER_FIELDS = {'id':'required', 'firstName':'required', 'lastName':False, 'description':False, 'email':'required', 'jobTitle':False, 'location':False, 'mobile':False, 'userStatus':False, 'enabled':False, 'password':'required'}
    UPDATE_USER_FIELDS = {'id':'required', 'firstName':False,'lastName':False, 'description':False, 'email':False, 'jobTitle':False, 'location':False, 'mobile':False, 'userStatus':False, 'enabled':False, 'password':False, 'oldPassword':False}

    def __init__(self, url='http://localhost:8080',debug=0):
        self.cookies = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPHandler(),urllib2.HTTPCookieProcessor(self.cookies))


        self.headers = {'Content-Type':'application/json', 'accept':'application/json'}
        self.rootUrl = url
        self.url = '%s/%s' % (url.rstrip('/'),Client.BASE_URL)
        self.login = None
        self.password = None
        self.ticket = None
        self.opener = opener
        self.instance = AlfrescoInstance(self.url)
        self.debug = debug

        

    def loginUser(self, login, password):
        loginUrl = '%s/%s' % (self.url, Client.LOGIN_URL)
        data = json.dumps({ "userId": login,"password": password})
        request = AlfrescoRequest(loginUrl, data=data, headers=self.headers, method='POST')
        serverResponse = None
        response = {'success':False,'error':[]}
        try:
            if self.debug == 1:
                print 'Try to connect as %s' % login
            serverResponse = self.opener.open(request)
            if self.debug == 1:
                print 'Connection success !! Code : %s'% serverResponse.getcode()
        except urllib2.HTTPError ,e:
            if e.code == 400:
                if self.debug == 1:
                    print 'Login or password is not provided'
                response['error'].append('Login or password is not provided')
            elif e.code == 403:
                if self.debug == 1:
                    print 'Login failed'
                response['error'].append('Login failed')
            elif e.code == 110:
                if self.debug == 1:
                    print 'Request time out'
                response['error'].append('Request time out')
            elif e.code == 111:
                if self.debug == 1:
                    print 'Connection refused'
                response['error'].append('Connection refused')
            else:
                printException(e)
        except urllib2.URLError, e:
            if self.debug == 1:
                print 'Unable to open url, Connection refused'
            response['error'].append('Unable to open url, Connection refused')
                
        if serverResponse is not None:
            jsonData = serverResponse.read()
            if self.debug == 1:
                print jsonData
            data = json.loads(jsonData)
            self.ticket = data['entry']['id']
            self.login = data['entry']['userId']
            self.password = password
            # Insert ticket in header for any later request for the same session
            self.headers['Authorization'] = "Basic %s"% base64.b64encode(self.ticket)
            serverResponse.close()
            response['success'] = True
            return response
        else:
            return response

    def reconnect(self):
        if not self.login or not self.password:
            raise ValidationError('Unable to reconnect to alfresco server')

        loginUrl = '%s/%s' % (self.url, Client.LOGIN_URL)
        data = json.dumps({ "userId": self.login,"password": self.password})
        request = AlfrescoRequest(loginUrl, data=data, headers=self.headers, method='POST')
        serverResponse = None
        response = {'success':False,'error':[]}
        try:
            if self.debug == 1:
                print 'Try to connect as %s' % login
            serverResponse = self.opener.open(request)
            if self.debug == 1:
                print 'Connection success !! Code : %s'% serverResponse.getcode()
        except urllib2.HTTPError ,e:
            if e.code == 400:
                if self.debug == 1:
                    print 'Login or password is not provided'
                response['error'].append('Login or password is not provided')
            elif e.code == 403:
                if self.debug == 1:
                    print 'Login failed'
                response['error'].append('Login failed')
            elif e.code == 110:
                if self.debug == 1:
                    print 'Request time out'
                response['error'].append('Request time out')
            elif e.code == 111:
                if self.debug == 1:
                    print 'Connection refused'
                response['error'].append('Connection refused')
            else:
                printException(e)
        except urllib2.URLError, e:
            if self.debug == 1:
                print 'Unable to open url, Connection refused'
            response['error'].append('Unable to open url, Connection refused')
                
        if serverResponse is not None:
            jsonData = serverResponse.read()
            if self.debug == 1:
                print jsonData
            data = json.loads(jsonData)
            self.ticket = data['entry']['id']
            # Insert ticket in header for any later request for the same session
            self.headers['Authorization'] = "Basic %s"% base64.b64encode(self.ticket)
            serverResponse.close()
            response['success'] = True
            return response
        else:
            return response

    def logoutUser(self):
        logoutUrl = '%s/%s' % (self.url, Client.LOGOUT_URL)
        request = AlfrescoRequest(logoutUrl, headers=self.headers, method='DELETE')
        serverResponse = None
        response = {'success':False,'error':[]}
        try:
            if self.debug == 1:
                print 'Try to disconnect user ...'
            serverResponse = self.opener.open(request)
        except urllib2.HTTPError ,e:
            if e.code == 400:
                if self.debug == 1:
                    print 'URL path does not include -me- or the ticket is not provided by the Authorization header'
                response['error'].append('URL path does not include -me- or the ticket is not provided by the Authorization header')
            elif e.code == 404:
                if self.debug == 1:
                    print 'Status of the user has changed (for example, the user is locked or the account is disabled) or the ticket has expired'
                response['error'].append('Status of the user has changed (for example, the user is locked or the account is disabled) or the ticket has expired')
            else:
                printException(e)
        except urllib2.URLError, e:
            if self.debug == 1:
                print 'Unable to open url, Connection refused'
            response['error'].append('Unable to open url, Connection refused')
                
        if serverResponse is not None:
            self.ticket = None
            self.login = None
            self.password = None
            # Insert ticket in header for any later request for the same session
            #self.headers['Authorization'] = "Basic %s"% base64.b64encode(self.ticket)
            #serverResponse.close()
            response['success'] = True
            return response
        else:
            return response

    def validateSession(self):
        validateUrl = '%s/%s' % (self.url, Client.VALIDATE_TICKET)
        request = AlfrescoRequest(validateUrl, headers=self.headers, method='GET')
        serverResponse = None
        response = {'success':False,'error':[]}
        try:
            serverResponse = self.opener.open(request)
        except urllib2.HTTPError ,e:
            if e.code == 400:
                if self.debug == 1:
                    print 'URL path does not include -me- or the ticket is not provided by the Authorization header'
                response['error'].append('URL path does not include -me- or the ticket is not provided by the Authorization header')
            elif e.code == 401:
                if self.debug == 1:
                    print 'Authentication failed'
                response['error'].append('Authentication failed')
            elif e.code == 404:
                if self.debug == 1:
                    print 'The request is authorized correctly but the status of the user (of the supplied ticket) has changed (for example, the user is locked or the account is disabled) or the ticket has expired'
                response['error'].append('Request time out')
            else:
                printException(e)
        except urllib2.URLError:
            print 'validateSession ------ > Unable to reach server'

        if serverResponse is not None:
            jsonData = serverResponse.read()
            serverResponse.close()
            response['success'] = True
            return response
        else:
            return response


# ---------------------------------------------------- USER -----------------------------------------------------------------------


    def createUser(self,userData):
        """
        @param: dict() contains keys recognized by the alfresco REST API 
                items : 'id', 'firstName', 'email', 'password' are required 
        @return: response dict() with two items 
            'success': equals True when everything goes right, False otherwise
            'error': contains dict() containing the errors returned from alfresco
        @Exceptions:
            ValidationError if one of the required items is missing
        """
        createUserUrl = '%s/%s' % (self.url, Client.CREATE_USER)
        user = {}
        response = {'success':True, 'error':None}
        for key, value in userData.items():
            # accept only recognized fields 
            if key in self.CREATE_USER_FIELDS.keys():
                user[key] = value

        for key, value in {k:v for k, v in self.CREATE_USER_FIELDS.items() if v == 'required'}.items():
            if key not in user:
                raise ValidationError('field %s is required to create a new user in alfresco'%key)

        request = AlfrescoRequest(createUserUrl,data=json.dumps(user), headers=self.headers,method='POST')
        serverResponse = None
        try:
            print 'Creating a user ...'
            serverResponse = self.opener.open(request)
            jsonResponse = json.loads(serverResponse.read())
            print json.dumps(jsonResponse, indent=4, sort_keys=True)    
        except urllib2.HTTPError, e:
            if e.code == 400:
                response['error'] = 'Invalid parameter: personBodyCreate is invalid'
                print 'Invalid parameter: personBodyCreate is invalid'
            elif e.code == 401:
                response['error'] = 'Authentication failed'
                print 'Authentication failed'   
            elif e.code == 403:
                response['error'] = 'Current user does not have permission to create a person'
                print 'Current user does not have permission to create a person'
            elif e.code == 409:
                response['error'] = 'Person within given id already exists'
                print 'Person within given id already exists'
            elif e.code == 422:
                response['error'] = 'Model integrity exception'
                print 'Model integrity exception'
            else:
                printException(e)
        except urllib2.URLError:
            print 'createUser ------ > Unable to reach server'


        if serverResponse is not None:
            serverResponse.close()
            return response
        else:
            response['success'] = False()
            return response

    def updateUser(self,userData):
        """
        @param: dict() contains keys recognized by the alfresco REST API 
                items : 'id' is required 
        @return: response dict() with two items 
            'success': equals True when everything goes right, False otherwise
            'error': contains dict() containing the errors returned from alfresco
        @Exceptions:
            ValidationError if 'id' item is missing
        """
        user = {}
        response = {'success':True, 'error':None}

        for key, value in userData.items():
            # accept only recognized fields 
            if key in self.UPDATE_USER_FIELDS.keys():
                if isinstance(value,bool):
                    if value:
                        user[key] = 'true'
                    else:
                        user[key] = 'false'
                else:
                    user[key] = str(value)

        for key, value in {k:v for k, v in self.UPDATE_USER_FIELDS.items() if v == 'required'}.items():
            if key not in user:
                raise ValidationError('field %s is required to update a user in alfresco'%key)
        

        updateUrl = '%s/%s/%s' % (self.url, Client.UPDATE_USER,user['id'])
        # user id is supplied in the url i must be deleted from json object
        del(user['id'])
        print 'CONTENT OF USER TO UPDATE: ',user
        print 'CONTENT OF URL TO UPDATE: ',updateUrl

        request = AlfrescoRequest(updateUrl,data=json.dumps(user), headers=self.headers,method='PUT')
        serverResponse = None
        try:
            print 'Updating a user ...'
            serverResponse = self.opener.open(request)
            jsonResponse = json.loads(serverResponse.read())
            print json.dumps(jsonResponse, indent=4, sort_keys=True)    
        except urllib2.HTTPError, e:
            if e.code == 400:
                response['error'] = 'Updating user: the update request is invalid or personId is not a valid format or personBodyUpdate is invalid'
                print 'Updating user: the update request is invalid or personId is not a valid format or personBodyUpdate is invalid'
            elif e.code == 401:
                response['error'] = 'Updating user: Authentication failed'
                print 'Updating user: Authentication failed'
            elif e.code == 403:
                response['error'] = 'Updating user: Current user does not have permission to update a person'
                print 'Updating user: Current user does not have permission to update a person' 
            elif e.code == 404:
                response['error'] = 'Updating user: personId does not exist'
                print 'Updating user: personId does not exist'
            elif e.code == 422:
                response['error'] = 'Updating user: Model integrity exception'
                print 'Updating user: Model integrity exception'
            else:
                printException(e)
        except urllib2.URLError:
            print 'updateUser ------ > Unable to reach server'

        if serverResponse is not None:
            serverResponse.close()
            return response
        else:
            response['success'] =False
            return response

    def deleteUser(self, userId):
        """
        @param: userId of the user to delete (required) and must be an str() object
        @return: response dict() with two items 
            'success': equals True when everything goes right, False otherwise
            'error': contains dict() containing the errors returned from alfresco
        @Exceptions:
            ValidationError if 'userId' param is missing
        """
        response = {'success':True, 'error':None}
        if not isinstance(userId, str) or not len(userId):
            raise ValidationError('Deleting User: userId cannot be Null')

        deleteUrl = '%s/%s/%s' % (self.rootUrl, Client.DELETE_USER, str(userId))
        request = AlfrescoRequest(deleteUrl, headers=self.headers, method='DELETE')
        serverResponse = None
        try:
            print 'Deleting a user ...'
            serverResponse = self.opener.open(request)
            jsonResponse = json.loads(serverResponse.read())
            print json.dumps(jsonResponse, indent=4, sort_keys=True)    
        except urllib2.HTTPError, e:
            if e.code == 400:
                response['error'] = 'Updating user: the update request is invalid or personId is not a valid format or personBodyUpdate is invalid'
                print 'Updating user: the update request is invalid or personId is not a valid format or personBodyUpdate is invalid'
            elif e.code == 401:
                response['error'] = 'Deleting user: Current user does not have permission to delete a person'
                print 'Deleting user: Current user does not have permission to delete a person'
            elif e.code == 404:
                response['error'] = 'Deleting user: personId does not exist'
                print 'Deleting user: personId does not exist'
            else:
                printException(e)
        except urllib2.URLError:
            print 'updateUser ------ > Unable to reach server'

        if serverResponse is not None:
            serverResponse.close()
            return response
        else:
            response['success'] =False
            return response

    def getUserGroups(self, userId):
        # alfresco/service/api/people
        response = {'success':True, 'error':None, 'groups':None}
        getGroupsUrl = '%s/%s/%s?groups=true' % (self.rootUrl, Client.GET_USER_GROUPS, str(userId))
        request = AlfrescoRequest(getGroupsUrl, headers=self.headers, method='GET')
        serverResponse = None
        try:
            print 'obtaining users groups ...'
            serverResponse = self.opener.open(request)
            jsonResponse = json.loads(serverResponse.read())
            print json.dumps(jsonResponse, indent=4, sort_keys=True)    
        except urllib2.HTTPError, e:
            if e.code == 400:
                response['error'] = 'Updating user: the update request is invalid or personId is not a valid format or personBodyUpdate is invalid'
                print 'Updating user: the update request is invalid or personId is not a valid format or personBodyUpdate is invalid'
            elif e.code == 401:
                response['error'] = 'Deleting user: Current user does not have permission to delete a person'
                print 'Deleting user: Current user does not have permission to delete a person'
            elif e.code == 404:
                response['error'] = 'Deleting user: personId does not exist'
                print 'Deleting user: personId does not exist'
            else:
                printException(e)
        except urllib2.URLError:
            print 'updateUser ------ > Unable to reach server'

        if serverResponse is not None and serverResponse.getcode() == 200:
            response['groups'] = jsonResponse['groups']
            serverResponse.close()
            return response
        else:
            response['success'] = False
            return response

# ---------------------------------------------------- SITE -----------------------------------------------------------------------


    def deleteSite(self, siteId=None, permanent=False):
        if siteId is None:
            raise ValueError('site ID is required !')
        if permanent == True:
            permanent = 'true'
        else:
            permanent = 'false'

        deleteSiteUrl = '%s/%s/%s?permanent=%s' % (self.url, Client.DELETE_SITE, siteId, permanent)
        request = AlfrescoRequest(deleteSiteUrl, headers=self.headers, method='DELETE')
        serverResponse = None
        response = {'success':False, 'response':{}, 'error':[]}
        try:
            print 'Deleting a site ...'
            serverResponse = self.opener.open(request)
        except urllib2.HTTPError, e:
            if e.code == 204:
                if self.debug == 1:
                    print 'Successful response Site deleted'
                response['error'].append('Invalid parameter: id, title, or description exceed the maximum length; or id contains invalid characters; or siteBodyCreate invalid')
            elif e.code == 401:
                if self.debug == 1:
                    print 'Authentication failed'   
                response['error'].append('Authentication failed')
            elif e.code == 403:
                if self.debug == 1:
                    print 'Current user does not have permission to delete the site that is visible to them'
                response['error'].append('Site with the given identifier already exists')
            elif e.code == 404:
                if self.debug == 1:
                    print 'siteId does not exist'
                response['error'].append('siteId does not exist')
            else:
                printException(e)

    def createSite(self, siteData=None, skipConfiguration=False, skipAddToFavorites=False):
        self.validateSession()
        """
        @param siteData: {"id": "SiteId","title": "SiteTitle","description": "description of site","visibility": "PRIVATE"}
        """
        if skipConfiguration == False:
            skipConfiguration = 'false'
        else:
            skipConfiguration = 'true'
        if skipAddToFavorites == False:
            skipAddToFavorites = 'false'
        else:
            skipAddToFavorites = 'true'
        
        createSiteUrl = '%s/%s?skipConfiguration=%s&skipAddToFavorites=%s' % (self.url,Client.CREATE_SITE, skipConfiguration, skipAddToFavorites)
        if 'id' not in siteData:
            raise ValueError('site ID is required !')
        elif 'title' not in siteData:
            raise ValueError('site Title is required !')
        elif 'visibility' not in siteData:
            raise ValueError('site Visibility is required !')

        request = AlfrescoRequest(createSiteUrl,data=json.dumps(siteData), headers=self.headers,method='POST')
        serverResponse = None
        response = {'success':False, 'response':{}, 'error':[]}
        try:
            print 'Creating a site ...'
            serverResponse = self.opener.open(request)
        except urllib2.HTTPError, e:
            if e.code == 400:
                if self.debug == 1:
                    print 'Invalid parameter: id, title, or description exceed the maximum length; or id contains invalid characters; or siteBodyCreate invalid'
                response['error'].append('Invalid parameter: id, title, or description exceed the maximum length; or id contains invalid characters; or siteBodyCreate invalid')
            elif e.code == 401:
                if self.debug == 1:
                    print 'Authentication failed'   
                response['error'].append('Authentication failed')
            elif e.code == 409:
                if self.debug == 1:
                    print 'Site with the given identifier already exists'
                response['error'].append('Site with the given identifier already exists')
            else:
                printException(e)

        if serverResponse is not None:
            data = json.loads(serverResponse.read())
            if self.debug == 1:
                print json.dumps(data, indent=4, sort_keys=True)
            response['response']['guid'] = data['entry']['guid']
            response['response']['id'] = data['entry']['id']
            response['response']['title'] = data['entry']['title']
            response['response']['visibility'] = data['entry']['visibility']
            response['response']['preset'] = data['entry']['preset']
            response['response']['role'] = data['entry']['role']
            response['success'] = True
            serverResponse.close()
            return response
        else:
            return response

    def updateSite(self, siteId=None, siteData=None):
        self.validateSession()
        """
        @param siteData: {"title": "SiteTitle","description": "description of site","visibility": "PRIVATE"}
        """
        if siteId is None:
            raise ValueError('Site ID is required !')

        createSiteUrl = '%s/%s/%s' % (self.url, Client.CREATE_SITE, siteId)
        print '------------- siteID %s'% createSiteUrl
        request = AlfrescoRequest(createSiteUrl, data=json.dumps(siteData), headers=self.headers, method='PUT')
        response = None
        try:
            print 'Updating a site ...'
            response = self.opener.open(request)
            jsonResponse = json.loads(response.read())
            print json.dumps(jsonResponse, indent=4, sort_keys=True)    
        except urllib2.HTTPError, e:
            if e.code == 400:
                print 'Invalid parameter: id, title, or description exceed the maximum length; or id contains invalid characters; or siteBodyCreate invalid'
            elif e.code == 401:
                print 'Authentication failed'   
            elif e.code == 409:
                print 'Site with the given identifier already exists'
            elif e.code == 403:
                print 'Current user does not have permission to update the site that is visible to them.'
            elif e.code == 404:
                print 'siteId does not exist'
            else:
                printException(e)


    def getAllSites(self):
        getAllSitesUrl = '%s/%s' % (self.url, Client.GET_ALL_SITES)
        response = {'success':True, 'error':None, 'sites':None}
        serverResponse = None
        request = AlfrescoRequest(getAllSitesUrl, headers=self.headers, method='GET')
        try:
            print 'get site list ...'
            serverResponse = self.opener.open(request)
            jsonResponse = json.loads(serverResponse.read())
            #print json.dumps(jsonResponse, indent=4, sort_keys=True)   
            response['sites'] = jsonResponse['list']['entries'] 
        except urllib2.HTTPError, e:
            if e.code == 400:
                print 'Invalid parameter: value of maxItems, skipCount, orderBy, or where is invalid'
                response['error'] = 'Invalid parameter: value of role or id is invalid or siteMembershipBodyCreate invalid'
            elif e.code == 401:
                print 'Authentication failed'
                response['error'] = 'Iuthentication failed'   
            else:
                printException(e)
        if serverResponse is not None and serverResponse.getcode() == 200:
            return response
        else:
            response['success'] = False
            return response

# ---------------------------------------------------- GROUP -----------------------------------------------------------------------

    def addGroupToSite(self, siteId, groupFullName, role='SiteConsumer'):
        """ groupFullName must begin with GROUP_ exp: GROUP_students_managers """
        addGroupUrl = '%s/%s/%s/memberships'%(self.rootUrl, Client.ADD_GROUP_TO_SITE,siteId)
        data = {
            'group':{
                'fullName':groupFullName
            },
            'role':role
            }
        print '##URL ',addGroupUrl
        print '## data ',data
        response = {'success':True, 'error':None}
        serverResponse = None
        request = AlfrescoRequest(addGroupUrl, data=json.dumps(data), headers=self.headers, method='POST')
        try:
            print 'adding group to site ...'
            serverResponse = self.opener.open(request)
            jsonResponse = json.loads(serverResponse.read())
            print json.dumps(jsonResponse, indent=4, sort_keys=True)    
        except urllib2.HTTPError, e:
            if e.code == 400:
                print 'Invalid parameter: value of role or id is invalid or siteMembershipBodyCreate invalid'
                response['error'] = 'Invalid parameter: value of role or id is invalid or siteMembershipBodyCreate invalid'
            elif e.code == 401:
                print 'Authentication failed'
                response['error'] = 'Iuthentication failed'   
            elif e.code == 409:
                print 'Person with this id is already a member'
                response['error'] = 'Person with this id is already a member'
            elif e.code == 403:
                print 'User does not have permission to invite a person'
                response['error'] = 'User does not have permission to invite a person'
            elif e.code == 404:
                print 'siteId or personId does not exist'
                response['error'] = 'siteId or personId does not exist'
            else:
                printException(e)
        if serverResponse is not None and serverResponse.getcode() == 201:
            return response
        else:
            response['success'] = False
            return response

    def removeGroupFromSite(self, siteId, groupFullName):
        removeGroupFromSiteUrl = '%s/%s/%s/memberships/%s'%(self.rootUrl,Client.REMOVE_GROUP_FROM_SITE,siteId,groupFullName)
        response = {'success':True, 'error':None}
        serverResponse = None
        request = AlfrescoRequest(createSiteMembershipUrl, data=json.dumps(data), headers=self.headers, method='DELETE')
        try:
            print 'removing group from site ...'
            serverResponse = self.opener.open(request)
            jsonResponse = json.loads(serverResponse.read())
            print json.dumps(jsonResponse, indent=4, sort_keys=True)    
        except urllib2.HTTPError, e:
            if e.code == 400:
                print 'Invalid parameter: value of role or id is invalid or siteMembershipBodyCreate invalid'
                response['error'] = 'Invalid parameter: value of role or id is invalid or siteMembershipBodyCreate invalid'
            elif e.code == 401:
                print 'Authentication failed'
                response['error'] = 'Iuthentication failed'   
            elif e.code == 409:
                print 'Person with this id is already a member'
                response['error'] = 'Person with this id is already a member'
            elif e.code == 403:
                print 'User does not have permission to invite a person'
                response['error'] = 'User does not have permission to invite a person'
            elif e.code == 404:
                print 'siteId or personId does not exist'
                response['error'] = 'siteId or personId does not exist'
            else:
                printException(e)
        if serverResponse is not None and serverResponse.getcode() == 200:
            return response
        else:
            response['success'] = False
            return response

    def addUserToGroup(self, groupShortName, userId):
        # /alfresco/service/api/groups/{shortName}/children/{fullAuthorityName} 
        addUserUrl = '%s/alfresco/service/api/groups/%s/children/%s'%(self.rootUrl, groupShortName, userId)
        print addUserUrl
        response = {'success':True, 'error':None}
        serverResponse = None
        data = {} # needs to post an empty json object because of the header Content-Type: application/json
        request = AlfrescoRequest(addUserUrl, data=json.dumps(data), headers=self.headers, method='POST')
        try:
            print 'ading user to group ...'
            serverResponse = self.opener.open(request)
            jsonResponse = json.loads(serverResponse.read())
            print json.dumps(jsonResponse, indent=4, sort_keys=True)    
        except urllib2.HTTPError, e:
            if e.code == 400:
                print 'Invalid parameter: value of role or id is invalid or siteMembershipBodyCreate invalid'
                response['error'] = 'Invalid parameter: value of role or id is invalid or siteMembershipBodyCreate invalid'
            elif e.code == 401:
                print 'Authentication failed'
                response['error'] = 'Iuthentication failed'   
            elif e.code == 409:
                print 'Person with this id is already a member'
                response['error'] = 'Person with this id is already a member'
            elif e.code == 403:
                print 'User does not have permission to invite a person'
                response['error'] = 'User does not have permission to invite a person'
            elif e.code == 404:
                print 'siteId or personId does not exist'
                response['error'] = 'siteId or personId does not exist'
            else:
                printException(e)
        if serverResponse is not None and serverResponse.getcode() == 200:
            return response
        else:
            response['success'] = False
            return response


    def removeUserFromGroup(self, groupShortName, userId):
        # '/alfresco/service/api/groups/{shortGroupName}/children/{fullAuthorityName}'
        removeUserUrl = '%s/alfresco/service/api/groups/%s/children/%s'%(self.rootUrl, groupShortName, userId)
        print removeUserUrl
        response = {'success':True, 'error':None}
        serverResponse = None
        request = AlfrescoRequest(removeUserUrl, headers=self.headers, method='DELETE')
        try:
            print 'removing user form group ...'
            serverResponse = self.opener.open(request)
            jsonResponse = json.loads(serverResponse.read())
            print json.dumps(jsonResponse, indent=4, sort_keys=True)    
        except urllib2.HTTPError, e:
            if e.code == 400:
                print 'Invalid parameter: value of role or id is invalid or siteMembershipBodyCreate invalid'
                response['error'] = 'Invalid parameter: value of role or id is invalid or siteMembershipBodyCreate invalid'
            elif e.code == 401:
                print 'Authentication failed'
                response['error'] = 'Iuthentication failed'   
            elif e.code == 409:
                print 'Person with this id is already a member'
                response['error'] = 'Person with this id is already a member'
            elif e.code == 403:
                print 'User does not have permission to invite a person'
                response['error'] = 'User does not have permission to invite a person'
            elif e.code == 404:
                print 'siteId or personId does not exist'
                response['error'] = 'siteId or personId does not exist'
            else:
                printException(e)
        if serverResponse is not None and serverResponse.getcode() == 200:
            return response
        else:
            response['success'] = False
            return response



    def createSiteMembership(self, siteId, userId, role='SiteConsumer'):
        createSiteMembershipUrl = '%s/%s/%s/members' % (self.url, Client.CREATE_SITE_MEMBERSHIP, siteId)
        print '------------- siteID %s'% createSiteMembershipUrl
        data = {'role':role, 'id':userId}
        response = {'success':True, 'error':None}
        serverResponse = None
        request = AlfrescoRequest(createSiteMembershipUrl, data=json.dumps(data), headers=self.headers, method='POST')
        try:
            print 'Create site membership ...'
            serverResponse = self.opener.open(request)
            jsonResponse = json.loads(serverResponse.read())
            print json.dumps(jsonResponse, indent=4, sort_keys=True)    
        except urllib2.HTTPError, e:
            if e.code == 400:
                print 'Invalid parameter: value of role or id is invalid or siteMembershipBodyCreate invalid'
                response['error'] = 'Invalid parameter: value of role or id is invalid or siteMembershipBodyCreate invalid'
            elif e.code == 401:
                print 'Authentication failed'
                response['error'] = 'Iuthentication failed'   
            elif e.code == 409:
                print 'Person with this id is already a member'
                response['error'] = 'Person with this id is already a member'
            elif e.code == 403:
                print 'User does not have permission to invite a person'
                response['error'] = 'User does not have permission to invite a person'
            elif e.code == 404:
                print 'siteId or personId does not exist'
                response['error'] = 'siteId or personId does not exist'
            else:
                printException(e)
        if serverResponse is not None and serverResponse.getcode() == 201:
            return response
        else:
            response['success'] = False
            return response




    def updateDocumentVersion(self,nodeRef,file, majorVersion=False, comment='',params=None):
        if isinstance(majorVersion, bool):
            if majorVersion == True:
                majorVersion = 'true'
            else:
                majorVersion = 'false'

        params = {'majorVersion':majorVersion,'comment':comment}
        encodedParams = urllib.urlencode(params)
        url = '%s/alfresco/versions/1/nodes/%s/content'% (str(self.url), str(nodeRef))
        url = '%s?%s'%(url,encodedParams)
        print '#### url: ',url
        try:
            len(file)
        except TypeError:
            file = file.read()

        request = AlfrescoRequest(url, data=file, headers=self.headers, method='PUT')
        try:
            response = self.opener.open(request)
        except urllib2.HTTPError, e:
                print e

        jsonResponse = json.loads(response.read())
        print json.dumps(jsonResponse, indent=4, sort_keys=True)
    

    def multipartUploadDocument(self, parentNodeRef=None, nodeData=None):
        register_openers()
        datagen, headers = multipart_encode(nodeData)
        self.headers.update(headers)
        createNodeUrl = '%s/alfresco/versions/1/nodes/%s/children' % (self.url,parentNodeRef)
        print 'URL : ',createNodeUrl
        request = AlfrescoRequest(createNodeUrl, data=datagen, headers=self.headers, method='POST')
        serverResponse = None
        response = {'success':False, 'result':[], 'errorMsg':'', 'errorCode':''}
        try:
            serverResponse = urllib2.urlopen(request)
        except urllib2.HTTPError, e:
            if e.code == 400:
                if self.debug == 1:
                    print 'Invalid parameter: nodeId is not a valid format or nodeBodyCreate is invalid'
                response['errorMsg']= 'Invalid parameter: nodeId is not a valid format or nodeBodyCreate is invalid'
                response['errorCode']= e.code
            if e.code == 401:
                if self.debug == 1:
                    print 'Authentication failed'
                response['errorMsg'] ='Authentication failed'
                response['errorCode']= e.code
            if e.code == 403:
                if self.debug == 1:
                    print 'Current user does not have permission to create children of nodeId'
                response['errorMsg'] = 'Current user does not have permission to create children of nodeId'
                response['errorCode']= e.code
            if e.code == 404:
                if self.debug == 1:
                    print 'nodeId does not exist'
                response['errorMsg'] = 'nodeId does not exist'
                response['errorCode']= e.code
            if e.code == 409:
                if self.debug == 1:
                    print 'New name clashes with an existing node in the current parent folder'
                response['errorMsg'] = 'New name clashes with an existing node in the current parent folder'
                response['errorCode']= e.code
            if e.code == 413:
                if self.debug == 1:
                    print 'Content exceeds individual file size limit configured for the network or system'
                response['errorMsg'] = 'Content exceeds individual file size limit configured for the network or system'
                response['errorCode']= e.code
            if e.code == 422:
                if self.debug == 1:
                    print 'Model integrity exception including a file name containing invalid characters'
                response['errorMsg'] = 'Model integrity exception including a file name containing invalid characters'
                response['errorCode']= e.code
            if e.code == 507:
                if self.debug == 1:
                    print 'Content exceeds overall storage quota limit configured for the network or system'
                response['errorMsg'] = 'Content exceeds overall storage quota limit configured for the network or system'
                response['errorCode']= e.code
            else:
                printException(e)
        
        if serverResponse is not None:
            #print ' ----- data --- %s'%serverResponse
            jsonResponse = json.loads(serverResponse.read())
            print json.dumps(jsonResponse, indent=4, sort_keys=True)    
            response['result'] = jsonResponse
            response['success'] = True
            return response
        else:
            return response


    def createNode(self,parentNodeRef=None, nodeData=None):
        self.validateSession()
        #createNodeUrl = '%s/alfresco/versions/1/nodes/%s/children' % (self.url, parentNodeRef)
        createNodeUrl = '%s/alfresco/versions/1/nodes/a945184f-42db-43cd-8416-f8bf65973286/children' % (self.url)
        #nodeData = {"name": "UploadingFolder","nodeType": "cm:folder"}
        #files = {"filedata": open("file.txt", "rb")}
        #request = AlfrescoRequest(createNodeUrl, data=json.dumps(nodeData), headers=self.headers, method='POST')
        request = AlfrescoRequest(createNodeUrl, data=open("file.txt", "rb").read(), headers=self.headers, method='POST')
        response = None
        try:
            print 'Creating a node ...'
            response = self.opener.open(request)
            jsonResponse = json.loads(response.read())
            print json.dumps(jsonResponse, indent=4, sort_keys=True)    
            node = {'id':'','parentId':''}
            node['id'] = jsonResponse['entry']['id']
            node['parentId'] = jsonResponse['entry']['parentId']
            return node
        except urllib2.HTTPError, e:
            if e.code == 400:
                print 'Invalid parameter: nodeId is not a valid format or nodeBodyCreate is invalid'
            elif e.code == 401:
                print 'Authentication failed'   
            elif e.code == 409:
                print 'New name clashes with an existing node in the current parent folder'
            elif e.code == 403:
                print 'Current user does not have permission to create children of nodeId'
            elif e.code == 404:
                print 'nodeId does not exist'
            else:
                printException(e)

    def getNode(self, nodeRef=None):
        self.validateSession()
        getNodeUrl = '%s/alfresco/versions/1/nodes/%s' % (self.url, nodeRef)
        request = AlfrescoRequest(getNodeUrl, headers=self.headers, method='GET')
        response = None
        try:
            print 'Obtaining a node ...'
            response = self.opener.open(request)
            jsonResponse = json.loads(response.read())
            print json.dumps(jsonResponse['entry'], indent=4, sort_keys=True)
            node = jsonResponse['entry']
        except urllib2.HTTPError, e:
            if e.code == 400:
                print 'Invalid parameter: nodeId is not a valid format'
            elif e.code == 401:
                print 'Authentication failed'
            elif e.code == 403:
                print 'Current user does not have permission to create children of nodeId'
            elif e.code == 404:
                print 'nodeId does not exist'
            else:
                printException(e)
        if response is not None:
            return node
        else:
            return None

    def getNodeChildren(self, parentNodeRef=None,isFolder=None,include=[]):
        """
            TO-DO : support pagination 
        """
        self.validateSession()
        createNodeUrl = '%s/alfresco/versions/1/nodes/%s/children' % (self.url, parentNodeRef)

        if isFolder == True:
            createNodeUrl = '%s?where=(isFolder=true)'%createNodeUrl
        elif isFolder == False:
            createNodeUrl = '%s?where=(isFolder=false)'%createNodeUrl

        if len(include):
            print '--------include is not empty ',include
            params = '&include='
            for param in include:
                print '----- content of one param : ',param
                params = '%s%s,'%(params,param)
            # delete the last comma
            params = params[:-1]
            createNodeUrl = '%s%s'%(createNodeUrl,params)
        else:
            print '--------include is empty ',include
        print '------------- getNodeChildren URL :',createNodeUrl

        request = AlfrescoRequest(createNodeUrl, headers=self.headers, method='GET')
        response = None
        try:
            print 'Obtaining a node ...'
            response = self.opener.open(request)
            jsonResponse = json.loads(response.read())
            print json.dumps(jsonResponse['list']['entries'], indent=4, sort_keys=True)
            nodes = jsonResponse['list']['entries']
            if isFolder == False:
                for node in nodes:
                    downloadUrl = '%s/%s/%s/content?attachment=true'%(self.url, Client.NODE_CONTENT, node['entry']['id'])
                    node['entry']['downloadUrl'] = downloadUrl
                    previewUrl = '%s/%s/%s/content?attachment=false'%(self.url, Client.NODE_CONTENT, node['entry']['id'])
                    node['entry']['previewUrl'] = previewUrl

                print '########!!!!!!!!!!!!! ',json.dumps(nodes, indent=4, sort_keys=True)

        except urllib2.HTTPError, e:
            if e.code == 400:
                print 'Invalid parameter: nodeId is not a valid format or nodeBodyCreate is invalid'
            elif e.code == 401:
                print 'Authentication failed'   
            elif e.code == 409:
                print 'New name clashes with an existing node in the current parent folder'
            elif e.code == 403:
                print 'Current user does not have permission to create children of nodeId'
            elif e.code == 404:
                print 'nodeId does not exist'
            else:
                printException(e)
        if response is not None:
            return nodes
        else:
            return None

    def getNodeShareUrl(self, nodeRef):
        self.validateSession()
        getShareUrl = '%s/%s?nodeRef=workspace://SpacesStore/%s'%(self.rootUrl, Client.NODE_SHARE_URL, nodeRef)
        serverResponse = None
        response = {'success':False, 'result':[], 'error':[]}
        request = AlfrescoRequest(getShareUrl, headers=self.headers, method='GET')
        try:
            serverResponse = self.opener.open(request)
        except urllib2.HTTPError, e:
            printException(e)

        if serverResponse is not None:
            jsonResponse = json.loads(serverResponse.read())
            print '-------- ROOT URL %s'%self.rootUrl
            print json.dumps(jsonResponse, indent=4, sort_keys=True)    
            serverResponse.close()
            response['result'] = jsonResponse
            response['success'] = True
            return response
        else:
            return response

    def getNodeContent(self,nodeRef):
        self.validateSession()
        getNodeContentUrl = '%s/%s/%s/content?attachment=true'%(self.url, Client.NODE_CONTENT, nodeRef)
        request = AlfrescoRequest(getNodeContentUrl, headers=self.headers, method='GET')
        response = None
        try:
            print 'Obtaining a node content ...'
            response = self.opener.open(request)
        except urllib2.HTTPError, e:
            if e.code == 304:
                print 'Content has not been modified since the date provided in the If-Modified-Since header'
            elif e.code == 400:
                print 'Invalid parameter: nodeId is not a valid format, or is not a file'   
            elif e.code == 401:
                print 'Authentication failed'
            elif e.code == 403:
                print 'Current user does not have permission to retrieve content of nodeId'
            elif e.code == 404:
                print 'nodeId does not exist'
            else:
                printException(e)
        if response is not None:
            return response
        else:
            return None


    def getDocumentLibraryNodeRef(self, siteNodeRef):
        nodes = self.getNodeChildren(siteNodeRef)
        docLibNodeRef = False
        for node in nodes:
            if node['entry']['name'] == 'documentLibrary':
                docLibNodeRef = node['entry']['id']
                break
        return docLibNodeRef


class AlfrescoInstance:

    def __init__(self, url):
        self.url = url.rstrip('/')

    def getBaseUrl(self):
        """ return the base url for the running alfresco instance"""
        return self.url

    def getUrl(self, path):
        """
        concat the base url with the path pointing to the needed function 
        @param path : path to the function Exp: 'sites' 
        """
        return '%s/%s' % (self.getBaseUrl(),path)



class AlfrescoRequest(urllib2.Request):
    """
    Extending the urllib2.Request class in order to add additional request method
    to GET and POST like PUT and DELETE 
    """
    def __init__(self, url, data=None, headers={}, origin_req_host=None, unverifiable=False, method=None):
        urllib2.Request.__init__(self, url, data, headers, origin_req_host, unverifiable)
        self.httpMethod = method

    def get_method(self):
        if self.httpMethod is not None:
            return self.httpMethod
        else:
            return urllib2.Request.get_method(self)

    def set_method(self, method):
        self.httpMethod = method



def printException(exception):
    print '---- > Unkown Error occured : \n\tURL : %s \n\tCODE : %s \n\tMSG : %s' % (exception.url, exception.code, exception.msg)
    jsonData = json.loads(exception.fp.read())
    if jsonData is not None:
        print json.dumps(jsonData, indent=4, sort_keys=True)    
    else:
        print 'Response is not of type JSON\n'


if __name__ == '__main__':
    client = Client(url='http://localhost:8080',debug=1)
    response = client.loginUser('admin','Nevermind')
    #siteData = {'id':'FileUploaderA','title':'FileUploaderA','visibility':'PUBLIC','description':'Description'}
    #response = client.createSite(siteData)
    #print '--------- response : %s'% response
    #siteID = response['response']['guid']

    #response = client.getNodeChildren(siteID)
    #docLibID = ''
    #for node in response:
    #   if node['entry']['name'] == 'documentLibrary':
    #       print 'documentLibrary NodeRef : %s'% node['entry']['id']
    #       docLibID = node['entry']['id']
    #       break
    #nodeData = {"name": "Quotation","nodeType": "cm:folder"}
    #print client.getNodeShareUrl('6417d086-f937-43c8-874d-e4a16efa7126')
    #client.uploadDocument()

    ##### -----------------------------------------------

    #Url = '%s/alfresco/versions/1/nodes/8272786f-1fe2-488a-ae53-3a25a37a7c9e/content?majorVersion=true'% (client.url)
    #print '# %s'%Url
    #url = 'http://vps385039.ovh.net:8080/alfresco/api/-default-/public/alfresco/versions/1/nodes/8272786f-1fe2-488a-ae53-3a25a37a7c9e/content?majorVersion=true'
    
    #files = open('SO035.pdf', "rb").read()
    
    #print '## HEADERS %s'% client.headers

    #request = AlfrescoRequest(Url, data=files, headers=client.headers, method='PUT')

    #try:
    #   response = client.opener.open(request)
    #except urllib2.HTTPError, e:
    #       printException(e)

    #jsonResponse = json.loads(response.read())
    #print json.dumps(jsonResponse, indent=4, sort_keys=True)
    #client.getNodeChildren('618d5146-059f-41bd-a95f-12b8df097cac');

    #print client.addUserToGroup('students_managers', '1_user')
    #file = open('file.txt', 'rb')
    #nodeData = {"filedata": file, "name":"whatat","cm:title":"whaats", "nodeType":"cm:content"}
    #response = client.multipartUploadDocument('8207d52c-f9fc-492b-9f45-6ad8825e3a0b',nodeData)
    #print response
    file = open('file.txt', 'rb')
    print client.updateDocumentVersion('3b995a10-418f-4209-91b1-afe8091a2256', file, 'true', 'comments of the new version from terminal')
    


#curl -uadmin:Nevermind -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{"name":"My text file.txt","nodeType":"cm:content"}' 'http://localhost:8080/alfresco/api/-default-/public/alfresco/versions/1/nodes/3210b291-3bb7-4675-a959-429a5caf56a7/children' -F filedata=@file.txt