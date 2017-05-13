# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError
import json
import re


class SchoolSetting(models.Model):
    _name = 'school.alfresco.config'


    alfresco_instance_id = fields.Many2one(
        'alfresco.config',
        'Alfresco Instance',
        domain="[('instance_state', '=', 'confirmed')]",
        help='Alfresco instance setup to use')

    enabled = fields.Selection([('enabled','Enabled'),('disabled','Disabled')], default='disabled')
    json_tree = fields.Char('json directory tree')


    @api.one
    @api.constrains('enabled')
    def _check_confirm(self):
    	if self.enabled == 'enabled':
    		confirmedConfigList = self.env['school.alfresco.config'].search([('enabled', '=', 'enabled'),('id','!=',self.id)])
    		if len(confirmedConfigList) > 0:
    			for rec in confirmedConfigList:
    				rec.write({'enabled':'disabled'})
    		
            
    #@api.onchange('json_tree')
    def _on_change_path_ids(self):
        paths = json.loads(self.json_tree)
        paths = dict()
        for el in paths:
            if el['data']['is_container']:
                paths[el['text']] = el
                print 'PATH: %s'%(el['data']['path'])
        return paths

    @api.multi
    def get_paths(self):
        containers_paths = list()
        if self.json_tree:
            paths = json.loads(self.json_tree)
            for el in paths:
                if el['data']['is_container']:
                    print '#### : ',el
                    containers_paths.append(el)
        return containers_paths



    @api.model
    def load_node_children(self):
        pass


class Path(models.Model):
    _name = 'school.alfresco.path'




class FolderStructure(models.Model):
    _name = 'school.folder.structure'

    @api.multi
    def _get_document_types(self):
        choices = []
        docTypes = self.env['school.document.type'].search([])
        for doc in docTypes:
            print 'doc name ',doc.name
            choices.append((str(doc.id),str(doc.name)))
        return choices

    @api.onchange('path_ids')
    def _on_change_path_ids(self):
        path = ''
        for element in self.path_ids:
            path = '%s/%s'%(path,element.name)
        self.name = path

    settings_id = fields.Many2one('school.alfresco.config')
    name = fields.Char('path')
    doc_type = fields.Selection(selection=_get_document_types)
    path_ids = fields.One2many('school.naming.pattern','folder')


class NamingPattern(models.Model):
    _name = 'school.naming.pattern'

    name = fields.Char('Folder name')
    dynamic = fields.Boolean('Is Dynamic ', default=False)

    name_pattern = fields.Selection([
        ('year','year'),
        ('month','month'),
        ('day','day'),
        ])

    folder = fields.Many2one('school.folder.structure')

    @api.one
    @api.constrains('name')
    def _check_name(self):
        print 'name = ', self.name
        print 'dynamic ', self.dynamic
        if self.dynamic == False:
        	p = re.compile('[^a-zA-Z0-9-]')
        	res = p.findall(self.name)

	        if len(res):
	            errorMsg = ''
	            for elem in res:
	                errorMsg = '%s, %s'%(errorMsg,str(elem))
	            raise ValidationError('not accepted charecters in none dynamic Folder name %s'%errorMsg)
	        else:
	        	return True
	        	
        p = re.compile('[^a-zA-Z0-9-\{\}]')
        res = p.findall(self.name)

        if len(res):
            errorMsg = ''
            for elem in res:
                errorMsg = '%s, %s'%(errorMsg,str(elem))
            raise ValidationError('not accepted charecters %s'%errorMsg)
        
        p = re.compile('^\{\}|\{\}$')
        res = p.findall(self.name)
        if len(res) == 0:
            raise ValidationError('You need to define the place of the dynamic part of the name using {} [ %s ]'%self.name)
        elif len(res) > 1:
        	raise ValidationError('You can define only one dynamic part of the folder name  [ %s ]'%self.name)