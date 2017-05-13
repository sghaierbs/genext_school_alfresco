#!/usr/bin/env python
#coding: utf8 
from odoo import fields, models,api
from odoo.exceptions import ValidationError
from alfrescoRESTful import Client
from openerp.exceptions import except_orm,ValidationError, Warning
import json
import base64
import alfresco
import os


class SchoolStudent(models.Model):
    _name='school.student'
    _inherit = 'school.student' 
        

    site_id = fields.Char('Alfresco SiteId', required=False, default=None)
    site_node_ref = fields.Char('Alfresco site nodeRef', required=False, default=None)
    site_title = fields.Char('Alfresco Site Title', required=False, default=None)
    site_share_url = fields.Char('Site Share url')
    document_library_node_ref = fields.Char('Document Library nodeRef')

   
    
    # To-Do make the group list dynamic
    alfresco_groups_roles = {'SiteConsumer':'GROUP_student_consumer', 'SiteCollaborator':'GROUP_student_collaborator', 
                            'SiteContributor':'GROUP_student_contributor', 'SiteManager':'GROUP_student_manager'}


    @alfresco.api
    @api.model
    def create(self, vals):
        vals['site_id'] = None
        vals['site_node_ref'] = None
        vals['site_title'] = None
        vals['document_library_node_ref'] = None
        vals['site_share_url'] = None
    	result = super(SchoolStudent, self).create(vals)
    	
    	print '# Content of self ', self
    	print '# Content of vals ', result.matricule
    	print '# Content of result ', result.display_name
        #print '# Content of vals ', vals
        if self.alfresco.instance.auto_create_site == True:
            response = self.autoCreateSite(result)
            result['site_id'] = response['id']
            result['site_node_ref'] = response['guid']
            result['site_title'] = response['title']
            result['document_library_node_ref'] = self.alfresco.admin.getDocumentLibraryNodeRef(response['guid'])
            result['site_share_url'] = None
            for role, group in SchoolStudent.alfresco_groups_roles.iteritems():
                print self.alfresco.admin.addGroupToSite(result['site_id'], group, role)
        return result

    #@alfresco.api
    #@api.multi
    #def write(self, values):
     


    @alfresco.api
    @api.multi
    def unlink(self):
        for student in self:
            if student.site_id:
                print 'Deleting site of student: ',student.name
                self.alfresco.admin.deleteSite(student.site_id, True)

        print '---------------------deleting a student'
        return super(SchoolStudent, self).unlink()

    @alfresco.api
    @api.model
    def get_folders(self):
        print '----------------------- alfresco config obtained ----------------------'
        return self.alfresco.config.get_paths()

    @api.model
    def getSite(self, studentId):
        return {'siteId':'whatever'}

    @alfresco.api
    def autoCreateSite(self, student):
    	"""
    		this method creates a site for the current student 
    		it gets called if the alfresco auto create site config is activated while creating 
    		a new student
    	"""
        siteData = {}
        siteData["id"] = str(student.matricule)
        siteData["title"] = str(student.display_name)
        if student.comment is not False:
        	siteData["description"] = str(student.comment)
        siteData["visibility"] = str(self.alfresco.instance.default_site_visibility)
        response = self.alfresco.admin.createSite(siteData, self.alfresco.instance.skipConfiguration, self.alfresco.instance.skipAddToFavorites)
        if response['success'] == False:
        	error = ''
        	for msg in response['error']:
	        	error = '%s\n%s'%(error,msg)
	        raise ValidationError(error)
        return response['response']


    @alfresco.api
    def createSite(self):
    	"""
    		this method creates a site for the current student using the create alfresco site action menu
    		it gets called from a server action
    	"""
    	#self._init_client()
    	if self.site_id == False:
    		siteData = {}
	        siteData["id"] = str(self.matricule)
	        siteData["title"] = str(self.display_name)
	        siteData["visibility"] = str(self.alfresco.instance.default_site_visibility)
	        response = self.alfresco.admin.createSite(siteData, self.alfresco.instance.skipConfiguration, self.alfresco.instance.skipAddToFavorites)
	        if response['success'] == False:
	        	error = ''
	        	for msg in response['error']:
		        	error = '%s\n%s'%(error,msg)
		        raise ValidationError(error)
	        else:
	        	data = response['response']
	        	site = {'site_id':data['id'], 'site_node_ref':data['guid'], 'site_title':data['title'],
        				 'document_library_node_ref':self.alfresco.admin.getDocumentLibraryNodeRef(data['guid'])}

        		self.write(site)
        else:
        	raise ValidationError("This student's site already created !")
    	return True

    @alfresco.api
    @api.model
    def uploadFile(self,fileName, fileTitle, base64_str, path, description, docLibNodeRef):
        print 'filename ',fileName
        print 'base64 ',base64_str
        print 'path ',path
        file = open(fileName,'w')
        import base64
        decoded = base64.b64decode(base64_str)
        print decoded
        file.write(decoded)
        file.close()
        file = open(fileName,'rb')
        nodeData = {"filedata":file, "name":fileName,'cm:title':fileTitle,"cm:description":description, "nodeType":"cm:content","relativePath":path}
        response = self.alfresco.user.multipartUploadDocument(docLibNodeRef,nodeData)
        file.close()
        if os.path.isfile(fileName):
            os.remove(fileName)
        print response
        return True

    @alfresco.api
    @api.model
    def uploadNewVersion(self,fileName, base64_str,nodeRef, comments, version):
        print 'filename ',fileName
        print 'base64 ',base64_str
        file = open(fileName,'w')
        import base64
        decoded = base64.b64decode(base64_str)
        print decoded
        file.write(decoded)
        file.close()
        file = open(fileName,'rb')
        response = self.alfresco.user.updateDocumentVersion(nodeRef, file, version, comments)
        file.close()
        #if os.path.isfile(fileName):
        #    os.remove(fileName)
        print response
        return True

    @alfresco.api
    @api.model
    def getNode(self,node_ref):
        node = self.alfresco.user.getNode(node_ref)
        print 'content of node_ref : ',node_ref
        print 'content of node : ',node
        return node


    @alfresco.api
    @api.model
    def getNodeChildren(self,parent_node_ref,isFolder=True,include=[]):
        print '#### inside call self: ',self.alfresco
        nodes = self.alfresco.user.getNodeChildren(parent_node_ref,isFolder,include)
        return nodes


    @alfresco.api
    @api.model
    def getNodeShareUrl(self,node_ref):
        """
        Structure of api response
        {
            "error": [], 
            "result": {
                "site": "siteId", 
                "url": ""
            }, 
            "success": true
        }
        
        Any error needs to be handled in client side in order to show any message to the user
        """
        response = self.alfresco.user.getNodeShareUrl(node_ref)
        return response
        

    @alfresco.api
    @api.model
    def getNodeContent(self, node_ref):
        print 'Recieved node_ref: ',node_ref
        response = self.alfresco.user.getNodeContent(node_ref)
        print 'Content of node getcode: ',response.getcode()
        print 'Content of node url: ',response.geturl()
        print 'Content of node info: ',response.info()
        print 'content of node: read ',response.read()
        file = [str(response.getcode()), str(response.geturl()), str(response.info())]
        return file

    def _get_alfresco_config(self):
        SchoolStudent.config = self.env['school.alfresco.config'].search([('enabled','=','enabled')])
        if len(SchoolStudent.config) >1:
            raise ValidationError('Instance_id must contains only one value check for errors')
        return SchoolStudent.config


    def _get_alfresco_instance(self, block_on_error=False):
        SchoolStudent.config = self._get_alfresco_config()

    	if SchoolStudent.config == None:
    		SchoolStudent.instance = False
    		if block_on_error == True:
    			raise ValidationError('Instance Configuration is missing, contact your system administrator for further information')
    		return False
        SchoolStudent.instance = SchoolStudent.config.alfresco_instance_id
        return SchoolStudent.instance

    def _init_client(self):
    	SchoolStudent.instance = self._get_alfresco_instance()
    	SchoolStudent.client = Client(url=SchoolStudent.instance.baseUrl, debug=1)
        result = SchoolStudent.client.loginUser(SchoolStudent.instance.username, SchoolStudent.instance.password)
        if result['success'] == False:
        	SchoolStudent.client = False
        	error = ''
        	for msg in result['error']:
        		error = '%s\n%s'%(error,msg)
        	raise ValidationError(error)
        	return False
        else:
        	return True


