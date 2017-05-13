# -*- coding: utf-8 -*-

from odoo import fields, models,api


class Document(models.Model):
    _name = 'school.document'

    node_ref = fields.Char('Node ref of document')
    share_url = fields.Char('Share URL')
    parent_node_ref = fields.Many2one(comodel_name='school.folder', ondelete='cascade')
    node_type = fields.Selection([('content','content'),('folder','folder')])

    version = fields.Char('Document version')
    student = fields.Many2one('school.student')

class Folder(models.Model):
	_name = 'school.folder'


	node_ref = fields.Char('Node ref of folder')
	site_node_id = fields.Many2one(comodel_name='school.site', ondelete='cascade')
	children_node_ids = fields.One2many(comodel_name='school.document', inverse_name='parent_node_ref')



class Site(models.Model):
    _name = 'school.site'


    site_id = fields.Char('Alfresco SiteId', required=False, default=None)
    site_node_ref = fields.Char('Alfresco site nodeRef', required=False, default=None)
    site_title = fields.Char('Alfresco Site Title', required=False, default=None)
    site_share_url = fields.Char('Site Share url')
    root_node_ref = fields.Char('Document Library nodeRef')

    children_node_ids = fields.One2many(comodel_name='school.folder',inverse_name='site_node_id')
    

    site_visibility = fields.Selection([
    	('PUBLIC','PUBLIC'),
    	('MODERATED','MODERATED'),
    	('PRIVATE','PRIVATE')
    	])
