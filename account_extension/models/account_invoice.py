# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_origin = fields.Char(
        string='Origin', readonly=False, tracking=True,
        help="The document(s) that generated the invoice.", copy=False)

    @api.model
    def create(self, vals):
        move_id = self.env['stock.move'].browse(vals.get('stock_move_id', []))
        if move_id and move_id.quant_id:
            default_adjustment_account_id = self.env['ir.config_parameter'].sudo()\
                .get_param('inventory_adjustment_extended.default_adjustment_account_id')
            for line in vals.get('line_ids'):
                line[2].update({
                    'ref': move_id.quant_id.description
                })
                if default_adjustment_account_id:
                    if line[2]['credit'] > 0 and line[2]['debit'] == 0 \
                            and line[2]['quantity'] > 0:
                        line[2].update({
                            'account_id': int(default_adjustment_account_id)
                        })
                    if line[2]['credit'] == 0 and line[2]['debit'] > 0 \
                            and line[2]['quantity'] < 0:
                        line[2].update({
                            'account_id': int(default_adjustment_account_id)
                        })
            vals.update({
                'ref': move_id.quant_id.description,
                'date' : move_id.quant_id.accounting_date
            })
        if move_id and move_id.inventory_id:
            for line in vals.get('line_ids'):
                line[2].update({
                    'ref': move_id.inventory_id.description
                })
            vals.update({
                'ref': move_id.inventory_id.description
            })
        return super(AccountMove, self).create(vals)
