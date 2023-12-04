# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    department_ids = fields.Many2many('hr.department')
    team_ids = fields.Many2many('hr.department', 'user_department_rel',
                                'user_id', 'department_id', string='Teams')

    @api.model
    def create(self, vals):
        user_id = super(ResUsers, self).create(vals)
        self.env['ir.rule'].clear_caches()
        return user_id

    def write(self, vals):
        self.env['ir.rule'].clear_caches()
        return super(ResUsers, self).write(vals)
