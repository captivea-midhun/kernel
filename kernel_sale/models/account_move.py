# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_notes = fields.Char(string='Notes')
    sale_id = fields.Many2one(
        'sale.order', compute='_compute_sale_source_document', store=True)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(AccountMove, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if self._context.get('default_type') not in ('out_invoice', 'out_refund'):
            if res.get('toolbar') and res['toolbar'].get('print'):
                for action in res['toolbar']['print']:
                    if action.get('xml_id', False) == \
                            'kernel_sale.action_report_customer_invoice_kernel':
                        res['toolbar']['print'].remove(action)

        if self._context.get('default_type') in ('out_invoice', 'out_refund'):
            if res.get('toolbar') and res['toolbar'].get('print'):
                for action in res['toolbar']['print']:
                    if action.get('xml_id', False) == 'account.account_invoices':
                        res['toolbar']['print'].remove(action)
        return res

    @api.depends('invoice_line_ids.sale_line_ids', 'invoice_line_ids.payment_id')
    def _compute_sale_source_document(self):
        for move in self:
            order_id = move.invoice_line_ids.mapped('sale_line_ids').mapped('order_id')
            if not order_id:
                order_id = move.invoice_line_ids.mapped('payment_id').invoice_ids.mapped('sale_id')
            move.sale_id = order_id and order_id.id or False


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    sale_id = fields.Many2one('sale.order', compute="_compute_sale_source_document", store=True)

    @api.depends('move_id')
    def _compute_sale_source_document(self):
        for line in self:
            order_id = line.move_id.invoice_line_ids.mapped('sale_line_ids').mapped('order_id')
            if not order_id:
                order_id = line.move_id.invoice_line_ids.mapped('payment_id'). \
                    invoice_ids.mapped('sale_id')
            line.sale_id = order_id and order_id.id or False
