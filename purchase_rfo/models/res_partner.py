# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    nda = fields.Boolean('NDA')
    nda_note = fields.Char(string="NDA Notes")
    export_restriction = fields.Boolean()
    export_restriction_note = fields.Char(string="Export Restriction Notes")

    @api.onchange('nda')
    def onchange_nda_note(self):
        if not self.nda:
            self.nda_note = False

    @api.onchange('export_restriction')
    def onchange_export_restriction_note(self):
        if not self.export_restriction:
            self.export_restriction_note = False

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        res = super(ResPartner, self)._name_search(name, args, operator, limit, name_get_uid)
        context = dict(self.env.context) or {}
        if context.get('from_shipping_address', False):
            shipping_partner_ids = self.env['res.partner'].search(
                ['|', ('is_company', '=', True),
                 ('parent_id.is_company', '=', True), ('type', '=', 'delivery')])
            return models.lazy_name_get(
                shipping_partner_ids.with_user(name_get_uid))
        return res
