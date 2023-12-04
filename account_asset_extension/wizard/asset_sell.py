# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields
from odoo.tools import float_is_zero


class AssetSell(models.TransientModel):
    _inherit = 'account.asset.sell'

    dispose_date = fields.Date(string="Dispose Date", default=fields.Date.context_today)

    def do_action(self):
        res = super(AssetSell, self).do_action()
        if res and res['res_id']:
            move_id = self.env['account.move'].browse(res['res_id'])
            move_id.update({'date': self.dispose_date})
        if self.action == 'dispose' and float_is_zero(
                self.asset_id.book_value, precision_rounding=self.asset_id.currency_id.rounding):
            asset_id = self.asset_id
            move_obj = self.env['account.move']
            move_vals = move_obj.with_context(type='entry').default_get(
                ['journal_id', 'type', 'date', 'currency_id'])
            move_lines = []
            move_vals.update({'asset_id': asset_id.id,
                              'date': self.dispose_date,
                              'ref': asset_id.name,
                              'auto_post': True})
            # Credit Lines
            move_lines.append(
                (0, 0, {'account_id': asset_id.account_asset_id.id,
                        'credit': asset_id.original_value,
                        'name': asset_id.name,
                        'debit': 0.00,
                        'analytic_tag_ids': asset_id.analytic_tag_ids and [
                            (6, 0, asset_id.analytic_tag_ids.ids)] or [], }))
            # Debit Lines
            move_lines.append(
                (0, 0, {'account_id': asset_id.account_depreciation_id.id,
                        'credit': 0.00,
                        'debit': asset_id.original_value,
                        'name': asset_id.name,
                        'analytic_tag_ids': asset_id.analytic_tag_ids and [
                            (6, 0, asset_id.analytic_tag_ids.ids)] or [], }))
            move_vals.update({'line_ids': move_lines})
            move_id = move_obj.create(move_vals)
            move_id.action_post()
        return res
