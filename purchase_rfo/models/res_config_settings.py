# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import fields, api, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def default_get(self, fields):
        res = super(ResConfigSettings, self).default_get(fields)
        res.update({'default_purchase_method': 'purchase'})
        return res

    department_id = fields.Many2one('hr.department', string="Project")
    po_expense_account_id = fields.Many2one(
        'account.account', string="Expense Account",
        domain=lambda self: [
            ('tag_ids', 'in', self.env.ref('purchase_rfo.account_tag_expense_account').ids)])
    inventoried_product_expense_account_id = fields.Many2one(
        'account.account', string="Purchase Order Expense Account",
        domain=lambda self: [
            ('tag_ids', 'in', self.env.ref('purchase_rfo.account_tag_expense_account').ids)])
    terms_conditions = fields.Text()

    @api.model
    def get_values(self):
        ICP = self.env['ir.config_parameter'].sudo()
        res = super(ResConfigSettings, self).get_values()
        res.update(
            department_id=int(ICP.get_param('purchase_rfo.department_id', default=False)),
            terms_conditions=ICP.get_param('purchase_rfo.terms_conditions'),
            po_expense_account_id=int(
                ICP.get_param('purchase_rfo.po_expense_account_id', default=False)),
            inventoried_product_expense_account_id=int(
                ICP.get_param('purchase_rfo.inventoried_product_expense_account_id',
                              default=False)))
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('purchase_rfo.department_id', self.department_id.id or False)
        params.set_param('purchase_rfo.terms_conditions', self.terms_conditions or '')
        params.set_param('purchase_rfo.po_expense_account_id',
                         self.po_expense_account_id.id or False)
        params.set_param('purchase_rfo.inventoried_product_expense_account_id',
                         self.inventoried_product_expense_account_id.id or False)
        return res
