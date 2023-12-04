# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Department', index=True)


class AccountReconcileModel(models.Model):
    _inherit = 'account.reconcile.model'

    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Department', ondelete='set null')


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Department',
        groups="analytic.group_analytic_accounting")


class AccountAnalyticDistribution(models.Model):
    _inherit = 'account.analytic.distribution'

    account_id = fields.Many2one(
        'account.analytic.account', string='Department', required=True)


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    name = fields.Char(
        string='Department', index=True, required=True, tracking=True)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    account_id = fields.Many2one(
        'account.analytic.account', string='Department', required=True, ondelete='restrict',
        index=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    account_analytic_id = fields.Many2one(
        'account.analytic.account', string='Department', readonly=True)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    account_analytic_id = fields.Many2one(
        'account.analytic.account', string='Department')


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    account_analytic_id = fields.Many2one(
        'account.analytic.account', string='Department',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_analytic_accounting = fields.Boolean(
        string='Department', implied_group='analytic.group_analytic_accounting')
