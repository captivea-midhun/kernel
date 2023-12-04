# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import fields, api, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    department_id = fields.Many2one('hr.department', string="Project")
    manager_id = fields.Many2one('res.users', string='Project Manager')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Department')
    purchase_order_id = fields.Many2one(
        'purchase.order', compute='_compute_purchase_source_document', store=True)

    @api.onchange('purchase_vendor_bill_id', 'purchase_id')
    def _onchange_purchase_auto_complete(self):
        purchase_id = self.purchase_id
        res = super(AccountMove, self)._onchange_purchase_auto_complete()
        if purchase_id:
            self.department_id = purchase_id.department_id.id or False
            self.manager_id = purchase_id.manager_id.id
        return res

    @api.onchange('department_id')
    def onchange_department_id(self):
        if self.department_id and self.department_id.user_id:
            self.manager_id = self.department_id.user_id.id
        else:
            self.manager_id = False
        if self.department_id and self.department_id.analytic_account_id:
            self.analytic_account_id = self.department_id.analytic_account_id.id
            self.invoice_line_ids.update(
                {'analytic_account_id': self.analytic_account_id.id})
        else:
            self.analytic_account_id = False
            self.invoice_line_ids.update({'analytic_account_id': False})

    @api.onchange('analytic_account_id')
    def onchange_analytic_account_id(self):
        self.invoice_line_ids.update(
            {'analytic_account_id': self.analytic_account_id and
                                    self.analytic_account_id.id or False})

    @api.depends('invoice_line_ids.purchase_line_id', 'invoice_line_ids.payment_id')
    def _compute_purchase_source_document(self):
        for move in self:
            order_id = move.invoice_line_ids.mapped('purchase_line_id').mapped('order_id')
            if not order_id:
                order_id = move.invoice_line_ids.mapped('payment_id').invoice_ids.mapped(
                    'purchase_order_id')
        move.purchase_order_id = order_id and order_id.id or False


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    product_type = fields.Selection(related='product_id.type', readonly=True, store=True)
    requestor_id = fields.Many2one('res.users', compute='_get_purchase_requestor',
                                   string='Purchase Requestor')
    purpose_type = fields.Many2one('purpose.type', compute='_get_purchase_requestor',
                                   string="Purpose")
    purchase_order_id = fields.Many2one(
        'purchase.order', compute='_compute_purchase_source_document', store=True)

    def _get_computed_account(self):
        account_id = super(AccountMoveLine, self)._get_computed_account()
        if self.purchase_line_id and self.purchase_line_id.account_id:
            account_id = self.purchase_line_id.account_id.id
        return account_id

    @api.depends('move_id')
    def _get_purchase_requestor(self):
        purchase_obj = self.env['purchase.order']
        for rec in self:
            self._cr.execute('select purchase_order_id from account_move_purchase_order_rel where '
                             'account_move_id = %s', [rec.move_id.id])
            purchase_ids = self.env.cr.fetchone()
            if purchase_ids:
                purchase_order_id = purchase_obj.browse(purchase_ids)
                rec.requestor_id = purchase_order_id and purchase_order_id.user_id \
                                   and purchase_order_id.user_id.id or False
                # Set purpose_type
                rec.purpose_type = purchase_order_id and purchase_order_id.purpose_type \
                                   and purchase_order_id.purpose_type.id or False
            else:
                rec.requestor_id = False
                rec.purpose_type = False

    @api.depends('move_id')
    def _compute_purchase_source_document(self):
        for line in self:
            order_id = line.move_id.invoice_line_ids.mapped('purchase_line_id').mapped('order_id')
            if not order_id:
                order_id = line.move_id.invoice_line_ids.mapped('payment_id').invoice_ids.mapped(
                    'purchase_order_id')
            line.purchase_order_id = order_id and order_id.id or False
