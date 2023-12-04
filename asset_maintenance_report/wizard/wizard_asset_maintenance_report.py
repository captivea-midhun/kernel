# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

import base64
import tempfile

from odoo import models, fields
from odoo.tools.misc import xlwt


class WizardAssetMaintenanceReport(models.TransientModel):
    _name = 'wizard.asset.maintenance.report'
    _description = 'Asset Maintenance Report'

    asset_model_ids = fields.Many2many('account.asset', string="Asset Models")
    sort_by = fields.Selection(
        [('asset_tag_id', 'Asset ID'), ('category_id', 'Equipment Category'),
         ('purchase_date', 'Purchase Date')], string="Sort By", default='asset_tag_id')
    starting_point = fields.Selection(
        [('account', 'Accounting'), ('equipment', 'Equipment')],
        string="Starting Point", default='account')
    equipment_status = fields.Selection(
        [('assigned', 'Assigned'), ('unassigned', 'Unassigned'), ('both', 'Both')],
        string="Equipment status", default='unassigned')
    datas = fields.Binary(string="Excel Report Data")

    def action_print_excel_report(self, equipment_ids=[]):
        tmp = tempfile.NamedTemporaryFile(prefix="xlsx", delete=False)
        file_path = tmp.name
        workbook = xlwt.Workbook()
        font = xlwt.Font()
        font.name = 'Calibri'
        font.height = 180

        # Currency Format
        currency_style = xlwt.XFStyle()
        currency_style.font = font
        currency_style.num_format_str = "%s#,##0.00" % (
            self.env.user.company_id.currency_id.symbol)

        # Common Style
        common_style = xlwt.XFStyle()
        common_style.font = font
        common_style.alignment.wrap = 1

        # Total Value of column style
        total_style = xlwt.XFStyle()
        total_style_font = xlwt.Font()
        total_style_font.name = 'Calibri'
        total_style_font.height = 180
        total_style_font.bold = True
        total_style.font = total_style_font
        total_style.num_format_str = "$#,##0.00"
        total_asset_cost = 0.00
        total_equip_cost = 0.00
        row = 7
        context = dict(self._context) or {}
        if context.get('all_assets'):
            asset_ids = context.get('asset_ids')
            if not asset_ids:
                return {'type': 'ir.actions.act_window_close'}

            worksheet = workbook.add_sheet(
                'Accounting Asset Assigned/Unassigned Report', cell_overwrite_ok=True)

            # Set title
            title_style = xlwt.easyxf("font: bold on, height 200; alignment: horiz centre")
            worksheet.write_merge(
                1, 2, 1, 3, 'Accounting Asset Assigned/Unassigned Report', title_style)

            # Prepare Headers
            headers = []
            header_title = {}
            header_title = {'asset_model': 'Asset Model',
                            'purchase_date': 'Purchase Date',
                            'asset_desc': 'Asset Description',
                            'asset_cost': 'Asset Cost', 'asset_id': 'Asset ID',
                            'equip_name': 'Equipment Name',
                            'brand': 'Brand', 'model': 'Model',
                            'equip_cost': 'Equip Cost'}

            headers = ['asset_model', 'purchase_date', 'asset_desc',
                       'asset_cost', 'asset_id', 'equip_name', 'brand',
                       'model', 'equip_cost']

            header_bold = xlwt.easyxf(
                "font: bold on, name Calibri, height 200; alignment: horiz centre;"
                "pattern: pattern solid, fore_colour cyan_ega;")

            column_title = xlwt.easyxf(
                "font: bold on, name Calibri, height 200; alignment: horiz centre;"
                "pattern: pattern solid, fore_colour gold;")

            # Set Column Title
            worksheet.write_merge(5, 5, 1, 2, 'Accounting Records', column_title)
            worksheet.write_merge(5, 5, 5, 7, 'Equipment Records', column_title)

            # Set headers
            column_counter = 0
            for header in headers:
                worksheet.col(column_counter).width = 256 * 18
                worksheet.write(6, column_counter, header_title.get(header), header_bold)
                column_counter += 1

            # Set Freeze pane
            worksheet.set_panes_frozen(True)
            worksheet.set_horz_split_pos(7)

            assigned_asset_ids = asset_ids.filtered(
                lambda asset: asset.asset_equipment_ids).mapped('asset_equipment_ids')
            unassigned_asset_ids = asset_ids.filtered(
                lambda asset: not asset.asset_equipment_ids)

            for equip in assigned_asset_ids:
                line_col = 0
                worksheet.write(row, line_col, equip.asset_id.model_id.name, common_style)
                line_col += 1
                worksheet.write(row, line_col, str(equip.asset_id.acquisition_date), common_style)
                line_col += 1
                worksheet.write(row, line_col, equip.asset_id.name, common_style)
                line_col += 1
                worksheet.write(row, line_col, equip.asset_id.original_value, currency_style)
                total_asset_cost += equip.asset_id.original_value
                line_col += 1
                worksheet.write(row, line_col, equip.asset_tag_id, common_style)
                line_col += 1
                worksheet.write(row, line_col, equip.name, common_style)
                line_col += 1
                worksheet.write(row, line_col, equip.equipment_brand or '', common_style)
                line_col += 1
                worksheet.write(row, line_col, equip.model or '', common_style)
                line_col += 1
                worksheet.write(row, line_col, equip.cost, currency_style)
                total_equip_cost += equip.cost
                line_col += 1
                row += 1

            for asset_id in unassigned_asset_ids:
                line_col = 0
                worksheet.write(row, line_col, asset_id.model_id.name, common_style)
                line_col += 1
                worksheet.write(row, line_col, str(asset_id.acquisition_date), common_style)
                line_col += 1
                worksheet.write(row, line_col, asset_id.name, common_style)
                line_col += 1
                worksheet.write(row, line_col, asset_id.original_value, currency_style)
                total_asset_cost += asset_id.original_value
                line_col += 1
                worksheet.write(row, line_col, '', common_style)
                line_col += 1
                worksheet.write(row, line_col, '', common_style)
                line_col += 1
                worksheet.write(row, line_col, '', common_style)
                line_col += 1
                worksheet.write(row, line_col, '', common_style)
                line_col += 1
                worksheet.write(row, line_col, '', currency_style)
                line_col += 1
                row += 1

            line_col = 2
            worksheet.write(row, line_col, 'Total', total_style)
            line_col += 1
            worksheet.write(row, line_col, total_asset_cost, total_style)

            line_col += 4
            worksheet.write(row, line_col, 'Total', total_style)
            line_col += 1
            worksheet.write(row, line_col, total_equip_cost, total_style)

            workbook.save(file_path + ".xlsx")
            buffer_data = base64.encodestring(open(file_path + '.xlsx', 'rb').read())
            if buffer_data:
                self.write({'datas': buffer_data})
                filename = 'Accounting Asset Assigned/Unassigned Report.xls'
                return {
                    'name': 'Accounting Asset Report',
                    'type': 'ir.actions.act_url',
                    'url': "web/content/?model=wizard.asset.maintenance.report&id=" + str(
                        self.id) + "&filename_field=filename&field=datas&download=true&filename=" + filename,
                    'target': 'self',
                }
            return {'type': 'ir.actions.act_window_close'}

        starting_point = self.starting_point
        equipment_status = self.equipment_status

        worksheet = workbook.add_sheet('Accounting Asset Report', cell_overwrite_ok=True)

        # Set title
        title_style = xlwt.easyxf("font: bold on, height 200; alignment: horiz centre")
        worksheet.write_merge(1, 2, 1, 3, 'Accounting Asset Report', title_style)

        # Prepare Headers
        headers = []
        header_title = {}
        if self.equipment_status == 'assigned' and self.starting_point == 'account':
            header_title = {'asset_model': 'Asset Model',
                            'purchase_date': 'Purchase Date',
                            'asset_desc': 'Asset Description',
                            'asset_cost': 'Asset Cost', 'asset_id': 'Asset ID',
                            'equip_name': 'Equipment Name',
                            'brand': 'Brand', 'model': 'Model',
                            'equip_cost': 'Equip Cost'}

            headers = ['asset_model', 'purchase_date', 'asset_desc',
                       'asset_cost', 'asset_id', 'equip_name', 'brand',
                       'model', 'equip_cost']
        elif self.equipment_status == 'assigned' and self.starting_point == 'equipment':
            header_title = {'asset_id': 'Asset ID',
                            'equip_name': 'Equipment Name', 'brand': 'Brand',
                            'model': 'Model', 'equip_cost': 'Equip Cost',
                            'asset_model': 'Asset Model',
                            'purchase_date': 'Purchase Date',
                            'asset_desc': 'Asset Description',
                            'asset_cost': 'Asset Cost'}

            headers = ['asset_id', 'equip_name', 'brand',
                       'model', 'equip_cost', 'asset_model', 'purchase_date',
                       'asset_desc', 'asset_cost']
        else:
            header_title = {'asset_id': 'Asset ID',
                            'equip_name': 'Equipment Name', 'brand': 'Brand',
                            'model': 'Model', 'purchase_date': 'Purchase Date',
                            'equip_cost': 'Equip Cost'}

            headers = ['asset_id', 'equip_name', 'brand',
                       'model', 'purchase_date', 'equip_cost']

        header_bold = xlwt.easyxf(
            "font: bold on, name Calibri, height 200; alignment: horiz centre;pattern: pattern solid, fore_colour cyan_ega;")

        column_title = xlwt.easyxf(
            "font: bold on, name Calibri, height 200; alignment: horiz centre;pattern: pattern solid, fore_colour gold;")
        # Set Column Title
        if self.equipment_status == 'assigned' and self.starting_point == 'account':
            worksheet.write_merge(5, 5, 1, 2, 'Accounting Records', column_title)
            worksheet.write_merge(5, 5, 5, 7, 'Equipment Records', column_title)
        elif self.equipment_status == 'assigned' and self.starting_point == 'equipment':
            worksheet.write_merge(5, 5, 1, 3, 'Equipment Records', column_title)
            worksheet.write_merge(5, 5, 6, 7, 'Accounting Records', column_title)
        else:
            worksheet.write_merge(5, 5, 1, 3, 'Equipment Records', column_title)

        # Set headers
        column_counter = 0
        for header in headers:
            worksheet.col(column_counter).width = 256 * 18
            worksheet.write(6, column_counter, header_title.get(header), header_bold)
            column_counter += 1

        # Set Freeze pane
        worksheet.set_panes_frozen(True)
        worksheet.set_horz_split_pos(7)

        if self.equipment_status == 'assigned' and self.starting_point == 'account':
            for equip in equipment_ids:
                line_col = 0
                worksheet.write(row, line_col, equip.asset_id.model_id.name, common_style)
                line_col += 1
                worksheet.write(row, line_col, str(equip.asset_id.acquisition_date), common_style)
                line_col += 1
                worksheet.write(row, line_col, equip.asset_id.name, common_style)
                line_col += 1
                worksheet.write(row, line_col, equip.asset_id.original_value, currency_style)
                total_asset_cost += equip.asset_id.original_value
                line_col += 1
                worksheet.write(row, line_col, equip.asset_tag_id, common_style)
                line_col += 1
                worksheet.write(row, line_col, equip.name, common_style)
                line_col += 1
                worksheet.write(row, line_col, equip.equipment_brand or '', common_style)
                line_col += 1
                worksheet.write(row, line_col, equip.model or '', common_style)
                line_col += 1
                worksheet.write(row, line_col, equip.cost, currency_style)
                total_equip_cost += equip.cost
                line_col += 1
                row += 1

            line_col = 2
            worksheet.write(row, line_col, 'Total', total_style)
            line_col += 1
            worksheet.write(row, line_col, total_asset_cost, total_style)

            line_col += 4
            worksheet.write(row, line_col, 'Total', total_style)
            line_col += 1
            worksheet.write(row, line_col, total_equip_cost, total_style)

        elif self.equipment_status == 'assigned' and self.starting_point == 'equipment':
            for equip in equipment_ids:
                line_col = 0
                worksheet.write(row, line_col, equip.asset_tag_id, common_style)
                line_col += 1
                worksheet.write(row, line_col, equip.name, common_style)
                line_col += 1
                worksheet.write(row, line_col, equip.equipment_brand or '', common_style)
                line_col += 1
                worksheet.write(row, line_col, equip.model or '', common_style)
                line_col += 1
                worksheet.write(row, line_col, equip.cost, currency_style)
                total_equip_cost += equip.cost
                worksheet.write(row, line_col, equip.asset_id.model_id.name, common_style)
                line_col += 1
                line_col += 1
                worksheet.write(row, line_col, str(
                    equip.asset_id.acquisition_date) if equip.asset_id.acquisition_date else '',
                                common_style)
                line_col += 1
                worksheet.write(row, line_col, equip.asset_id.name, common_style)
                line_col += 1
                worksheet.write(row, line_col, equip.asset_id.original_value, currency_style)
                total_asset_cost += equip.asset_id.original_value
                line_col += 1
                row += 1

            line_col = 3
            worksheet.write(row, line_col, 'Total', total_style)
            line_col += 1
            worksheet.write(row, line_col, total_equip_cost, total_style)

            line_col += 3
            worksheet.write(row, line_col, 'Total', total_style)
            line_col += 1
            worksheet.write(row, line_col, total_asset_cost, total_style)
        else:
            for equip in equipment_ids:
                line_col = 0
                worksheet.write(row, line_col, equip.asset_tag_id or '', common_style)
                line_col += 1
                worksheet.write(row, line_col, equip.name, common_style)
                line_col += 1
                worksheet.write(row, line_col, equip.equipment_brand or '', common_style)
                line_col += 1
                worksheet.write(row, line_col, equip.model or '', common_style)
                line_col += 1
                worksheet.write(row, line_col, str(
                    equip.purchase_date) if equip.purchase_date else '', common_style)
                line_col += 1
                worksheet.write(row, line_col, equip.cost, currency_style)
                total_equip_cost += equip.cost
                line_col += 1
                row += 1

            line_col = 4
            worksheet.write(row, line_col, 'Total', total_style)
            line_col += 1
            worksheet.write(row, line_col, total_equip_cost, total_style)

        workbook.save(file_path + ".xlsx")
        buffer_data = base64.encodestring(open(file_path + '.xlsx', 'rb').read())
        if buffer_data:
            self.write({'datas': buffer_data})
            filename = 'Accounting Asset Report.xls'
            return {
                'name': 'Accounting Asset Report',
                'type': 'ir.actions.act_url',
                'url': "web/content/?model=wizard.asset.maintenance.report&id=" + str(
                    self.id) + "&filename_field=filename&field=datas&download=true&filename=" + filename,
                'target': 'self',
            }
        return {'type': 'ir.actions.act_window_close'}

    def action_print_report(self):
        asset_models_ids = self.asset_model_ids
        if not asset_models_ids:
            asset_models_ids = self.env['account.asset'].search(
                [('asset_type', '=', 'purchase'), ('state', '=', 'model')])
        equipment_obj = self.env['maintenance.equipment']
        if self.equipment_status != 'both':
            if self.equipment_status == 'unassigned':
                equipment_ids = equipment_obj.search([('asset_id', '=', False)])
            elif self.equipment_status == 'assigned':
                domain = [('asset_id', '!=', False),
                          ('asset_id.model_id', 'in', asset_models_ids.ids)]
                equipment_ids = equipment_obj.search(domain)
            datas = {'ids': equipment_ids.ids,
                     'model': 'maintenance.equipment',
                     'form': self.read()[0]}
            if self._context.get('excel_report', False):
                return self.action_print_excel_report(equipment_ids)
            return self.env.ref(
                'asset_maintenance_report.maintenance_accounting_asset_report_kernel'
                ).report_action(self, data=datas)
        else:
            asset_ids = self.env['account.asset'].search(
                [('model_id', 'in', asset_models_ids.ids)], order='model_id asc')
            datas = {'ids': asset_ids.ids,
                     'model': 'account.asset',
                     'form': self.read()[0]}
            if self._context.get('excel_report', False):
                return self.with_context(
                    all_assets=True, asset_ids=asset_ids).action_print_excel_report()
            return self.env.ref(
                'asset_maintenance_report.maintenance_accounting_asset_both_report_kernel'
            ).report_action(self, data=datas)
