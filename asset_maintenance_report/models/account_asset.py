# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, api, _
from odoo.exceptions import UserError


class EquipmentAssetBothReport(models.AbstractModel):
    _name = 'report.asset_maintenance_report.accounting_asset_both_template'
    _description = "Equipment Asset Both Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        asset_report = self.env['ir.actions.report']._get_report_from_name(
            'asset_maintenance_report.accounting_asset_both_template')
        docs = self.env[asset_report.model].browse(data['ids'])
        assigned_asset_ids = docs.filtered(
            lambda asset: asset.asset_equipment_ids).mapped('asset_equipment_ids')
        unassigned_asset_ids = docs.filtered(
            lambda asset: not asset.asset_equipment_ids)
        return {'doc_ids': data['ids'],
                'doc_model': asset_report.model,
                'docs': docs,
                'assigned_asset_ids': assigned_asset_ids,
                'unassigned_asset_ids': unassigned_asset_ids,
                'equipment_status': data['form']['equipment_status']}


class EquipmentAssetReport(models.AbstractModel):
    _name = 'report.asset_maintenance_report.accounting_asset_template'
    _description = "Equipment Asset Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        asset_report = self.env['ir.actions.report']._get_report_from_name(
            'asset_maintenance_report.accounting_asset_template')
        return {'doc_ids': data['ids'],
                'doc_model': asset_report.model,
                'docs': self.env[asset_report.model].browse(data['ids']),
                'starting_point': data['form']['starting_point'],
                'equipment_status': data['form']['equipment_status']}


class MaintenanceEquipmentReport(models.AbstractModel):
    _name = 'report.asset_maintenance_report.maintenance_equip_template'
    _description = "Maintenance Equipment Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        asset_report = self.env['ir.actions.report']._get_report_from_name(
            'asset_maintenance_report.maintenance_equip_template')
        return {'doc_ids': data['ids'],
                'doc_model': asset_report.model,
                'docs': self.env[asset_report.model].browse(data['ids'])}
