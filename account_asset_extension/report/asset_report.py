# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, _
from odoo.exceptions import UserError


class FixedAssetTemplate(models.AbstractModel):
    _name = 'report.account_asset_extension.fixed_asset_template'
    _description = "Account Fixed Asset Report Template"

    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        asset_ids = self.env[data['model']].browse(data['form']['asset_ids'])
        move_ids = self.env['account.move'].browse(data['form']['move_ids'])
        return {
            'data': list(set([asset.model_id if asset.model_id else False for asset in asset_ids])),
            'doc_model': 'account.asset',
            'docs': asset_ids,
            'move_ids': move_ids,
            'start_date': data['form']['start_date'],
            'end_date': data['form']['end_date'],
            'hide_zero_lines': data['form']['hide_zero_lines']}


class CIPAssetTemplate(models.AbstractModel):
    _name = 'report.account_asset_extension.cip_asset_template'
    _description = "Account CIP Asset Report Template"

    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        cip_account_ids = self.env['account.account'].search([('is_cip', '=', True)])
        return {'data': data,
                'cip_account_ids': cip_account_ids,
                'doc_model': 'account.move.line',
                'currency_id': self.env.user.company_id.currency_id,
                'start_date': data['form']['start_date'],
                'end_date': data['form']['end_date']}
