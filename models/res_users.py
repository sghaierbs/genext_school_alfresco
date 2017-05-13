# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID
from odoo.exceptions import AccessDenied, AccessError, UserError
from alfrescoRESTful import Client
import alfresco
import inspect

class Users(models.Model):

    _name = 'res.users'
    _inherit = 'res.users'

    alfresco_password = fields.Char(readonly=True)
    
    @alfresco.api
    @api.model
    def create(self, vals):
        response = None
        user = super(Users, self).create(vals)
        if user.active:
            # using odoo user ( id user_[id] ) as username in alfresco since changing user id is not allowed in alfresco 
            # using login as default password in alfresco because it's a required field to create a user
            # using default@email.com as default email which can be [altered later] <-- TO-DO
            user.alfresco_password = user.login
            userData = {'id': 'user_%s'%user.id, 'firstName': user.name, 'email': 'default@email.com', 'password': user.login, 'enabled':True}
            # only admin user can create users in alfresco 
            # => bypassing access rights by using admin account 
            response = self.alfresco.admin.createUser(userData)
        else:
            user.alfresco_password = user.login
            client = Connector().getClient(self, as_admin=True)
            userData = {'id': 'user_%s'%user.id, 'firstName': user.name, 'email': 'default@email.com', 'password': user.login, 'enabled':False}
            response = self.alfresco.admin.createUser(userData)


        sel_groups_ids = self.selection_group_name('genext_school_alfresco','alfresco_roles')
        if sel_groups_ids is not None and sel_groups_ids in vals.keys():
            if vals[sel_groups_ids] is not False:
                print 'need to add this user to the selected group'
                group = self.env['res.groups'].search([('id', '=',vals[sel_groups_ids])])
                print 'group name %s | group id %s'%(group.name, group.id)
                role = str(group.name).replace(" ", "")
                if response['success'] == True:
                    alfresco_group_name = 'student_%s'%str(group.name)[5:].lower() 
                    response = self.alfresco.admin.addUserToGroup(alfresco_group_name, 'user_%s'%user.id)
                    print response
            else:
                print 'found but equals False'
        else:
            print 'not need to Add user'

        return user

    def selection_group_name(self, module, group_category):
        category_id = self.env['ir.model.data'].get_object(module,group_category)
        groups = self.env['res.groups'].search([('category_id', '=', category_id.id)])
        # ids needs to be sorted in order to construct a valide key value
        ids  = sorted(groups.ids, key=int)
        if ids:
            return 'sel_groups_' + '_'.join(map(str, ids))
        else:
            return None

    @alfresco.api
    @api.multi
    def write(self, values):
        print '### calling write method from res.user'
        sel_groups_ids = self.selection_group_name('genext_school_alfresco','alfresco_roles')
        res = super(Users, self).write(values)
        userData = {}
        client = None
        for user in self:
            if user.id != SUPERUSER_ID:
                if values.get('active') == False:
                    userData = {'enabled': False}
                elif values.get('active') == True:
                    userData = {'enabled': True}

                if 'name' in values.keys():
                    userData['firstName'] = values['name']

                if sel_groups_ids is not None and sel_groups_ids in values.keys():
                    if values[sel_groups_ids] is not False:
                        # first remove user from groups that he belongs to
                        response = self.alfresco.admin.getUserGroups('user_%s'%user.id)
                        if response['success'] == True:                            
                            for group in response['groups']:                          
                                response = self.alfresco.admin.removeUserFromGroup(group['itemName'], 'user_%s'%user.id)
                        # then add the user to the selected group
                        group = self.env['res.groups'].search([('id', '=',values[sel_groups_ids])])
                        print 'group name %s | group id %s'%(group.id,group.name)
                        role = str(group.name).replace(" ", "")
                        alfresco_group_name = 'student_%s'%str(group.name)[5:].lower() 
                        response = self.alfresco.admin.addUserToGroup(alfresco_group_name, 'user_%s'%user.id)
                        print response
                    else:
                        # just remove the user from all groups that he belongs to
                        response = self.alfresco.admin.getUserGroups('user_%s'%user.id)
                        if response['success'] == True:
                            for group in response['groups']:                                
                                response = self.alfresco.admin.removeUserFromGroup(group['itemName'], 'user_%s'%user.id)
                        

                # TO-DO check if related patener email is altered 
                
                if len(userData):
                    userData['id'] = 'user_%s'%user.id
                    response = None
                    if user.id == self._uid:
                        client = self.alfresco.user
                    else:
                        client = self.alfresco.admin
                    response = client.updateUser(userData)
                    if response['success'] == False:
                        raise UserError(response['error'])
        return res

    @alfresco.api
    @api.multi
    def unlink(self):
        if SUPERUSER_ID not in self.ids:
            for user in self:
                if user.id == self._uid:
                    raise UserError('You can not remove your own account which have a related alfresco account')
                else:
                    response = self.alfresco.admin.deleteUser('user_%s'%user.id)
                    if response['success'] == False:
                        raise UserError(response['error'])
        else:
            raise UserError('You can not remove the admin user as it is used internally for resources created by Odoo (updates, module installation, ...)')
        return super(Users, self).unlink()

    @alfresco.api
    @api.model
    def change_password(self, old_passwd, new_passwd):
        """ 
        called when user try to change his own password therefore the old password needs to be supplied
        """
        password = super(Users, self).change_password(old_passwd, new_passwd)
        if password:
            userData = {'id': 'user_%s'%self.env.user.id, 'password': new_passwd, 'oldPassword':old_passwd}
            response = self.alfresco.user.updateUser(userData)
            self.env.user.alfresco_password = new_passwd
            print '--------- response: ',response
        return password


class ChangePasswordUser(models.TransientModel):
    """ A model to configure users in the change password wizard. """
    _name = 'change.password.user'
    _inherit = 'change.password.user'

    @alfresco.api
    @api.multi
    def change_password_button(self):
        """ called when admin user try to update user password """
        for line in self:
            # admin user account is immutable 
            if line.user_id.id != SUPERUSER_ID:
                userData = {'id': 'user_%s'%line.user_id.id,'password': line.new_passwd}                
                print 'CONENT OF SELF: ',self
                print 'CONENT OF line: ',line
                response = self.alfresco.admin.updateUser(userData)
                line.user_id.alfresco_password = line.new_passwd
                print '--------- response: ',response
        super(ChangePasswordUser, self).change_password_button()

