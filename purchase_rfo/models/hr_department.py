# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import fields, models, api


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Department')
    user_id = fields.Many2one('res.users')

    @api.model
    def create(self, vals):
        analytic_account_obj = self.env['account.analytic.account']
        if not vals.get('analytic_account_id'):
            analytic_account = analytic_account_obj.create({
                'name': vals.get('name')
            })
            vals.update({'analytic_account_id': analytic_account.id})
        department_id = super(HrDepartment, self).create(vals)
        if vals.get('user_id', False):
            if department_id.user_id.id not in department_id.user_id.department_ids.ids:
                department_id.user_id.write(
                    {'department_ids': [(6, 0, department_id.ids)]})
        self.env['ir.rule'].clear_caches()
        return department_id

    def write(self, vals):
        user_obj = self.env['res.users']
        for department in self:
            if vals.get('user_id', False):
                user_id = user_obj.browse(vals['user_id'])
                if user_id.id not in user_id.department_ids.ids:
                    user_id.write({'department_ids': [
                        (6, 0, user_id.department_ids.ids + department.ids)]})
                department.user_id.write(
                    {'department_ids': [(3, department.id)]})
            else:
                department.user_id.write(
                    {'department_ids': [(3, department.id)]})
            self.env['ir.rule'].clear_caches()
        return super(HrDepartment, self).write(vals)
