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


class WizardMaintenanceEquipmentReport(models.TransientModel):
    _name = 'wizard.maintenance.equipment.report'
    _description = 'Maintenance Equipment Report'

    start_date = fields.Date(stirng="From Date", default=fields.Date.context_today)
    end_date = fields.Date(stirng="To Date")
    filter_option = fields.Selection(
        [('end_of_life', 'End of Life'), ('next_action_date', 'Next Preventive Maintenance'),
         ('both', 'All End of Life Dates')], stirng="Option", default='end_of_life')
    datas = fields.Binary(string="Excel Report Data")

    def action_print_excel_report(self, equipment_ids):
        tmp = tempfile.NamedTemporaryFile(prefix="xlsx", delete=False)
        file_path = tmp.name
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Maintenance Equipment Report', cell_overwrite_ok=True)
        # Set title
        title_style = xlwt.easyxf("font: bold on, height 200; alignment: horiz centre")
        worksheet.write_merge(1, 2, 1, 3, 'Maintenance Equipment Report', title_style)
        # Prepare Headers
        header_title = {'expected_end_of_life': 'Expected End of Life',
                        'next_action_date': 'Next Preventive Maintenance',
                        'asset_id': 'Asset ID',
                        'equip_name': 'Equipment Name',
                        'brand': 'Brand', 'model': 'Model',
                        'purchase_date': 'Purchase Date',
                        'equip_cost': 'Equip Cost'}

        headers = ['expected_end_of_life', 'next_action_date',
                   'asset_id', 'equip_name', 'brand',
                   'model', 'purchase_date', 'equip_cost']

        header_bold = xlwt.easyxf("font: bold on, name Calibri, height 200; "
                                  "alignment: horiz centre;"
                                  "pattern: pattern solid, fore_colour cyan_ega;")

        # Set headers
        column_counter = 0
        for header in headers:
            worksheet.col(column_counter).width = 256 * 18
            worksheet.write(5, column_counter, header_title.get(header), header_bold)
            column_counter += 1

        # Set Freeze pane
        worksheet.set_panes_frozen(True)
        worksheet.set_horz_split_pos(6)

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
        total_equip_cost = 0.00

        row = 6
        for equip in equipment_ids:
            line_col = 0
            worksheet.write(
                row, line_col, str(equip.expected_end_of_life) if equip.expected_end_of_life
                else '', common_style)
            line_col += 1
            worksheet.write(
                row, line_col, str(equip.next_action_date) if equip.next_action_date
                else '', common_style)
            line_col += 1
            worksheet.write(row, line_col, equip.asset_tag_id, common_style)
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
            worksheet.write(row, line_col, equip.cost or 0.00, currency_style)
            total_equip_cost += equip.cost
            line_col += 1
            row += 1

        line_col = 6
        worksheet.write(row, line_col, 'Total', total_style)
        line_col += 1
        worksheet.write(row, line_col, total_equip_cost, total_style)

        workbook.save(file_path + ".xlsx")
        buffer_data = base64.encodestring(open(file_path + '.xlsx', 'rb').read())
        if buffer_data:
            self.write({'datas': buffer_data})
            filename = 'Maintenance Equipment Report.xls'
            return {
                'name': 'Maintenance Equipment Report',
                'type': 'ir.actions.act_url',
                'url': "web/content/?model=wizard.maintenance.equipment.report&id=" + str(
                    self.id) + "&filename_field=filename&field=datas&download=true&filename=" + filename,
                'target': 'self',
            }
        return {'type': 'ir.actions.act_window_close'}

    def action_print_report(self):
        equipment_obj = self.env['maintenance.equipment']
        if self.filter_option == 'end_of_life':
            domain = [('expected_end_of_life', '>=', self.start_date),
                      ('expected_end_of_life', '<=', self.end_date)]
        elif self.filter_option == 'next_action_date':
            domain = [('next_action_date', '>=', self.start_date),
                      ('next_action_date', '<=', self.end_date)]
        else:
            domain = [('expected_end_of_life', '>=',
                       fields.Date.context_today(self))]
        equipment_ids = equipment_obj.search(domain)
        datas = {'ids': equipment_ids.ids, 'model': 'maintenance.equipment',
                 'form': self.read()[0]}
        if self._context.get('excel_report', False):
            return self.action_print_excel_report(equipment_ids)
        return self.env.ref(
            'asset_maintenance_report.maintenance_equip_report_kernel'
        ).report_action(self, data=datas)
