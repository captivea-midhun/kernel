# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

import base64
import tempfile

from odoo import models, fields, _
from odoo.exceptions import UserError
from odoo.tools.misc import xlwt


class WizardFixedAssetReport(models.TransientModel):
    _name = "wizard.fixed.asset.report"
    _description = "Fixed Asset Report"

    start_date = fields.Date(string="From Date")
    end_date = fields.Date(string="To Date")
    report_type = fields.Selection([
        ('asset', 'Asset'), ('cip', 'CIP')], default='asset', string="Report")
    datas = fields.Binary('File')
    hide_zero_lines = fields.Boolean(string="Hide zero amount lines?", default=True)

    def action_print_xls_asset_report(self, data):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        asset_ids = self.env[data['model']].browse(data['form']['asset_ids'])
        move_ids = self.env['account.move'].browse(data['form']['move_ids'])
        category_ids = list(
            set([asset.model_id if asset.model_id else False for asset in asset_ids]))

        tmp = tempfile.NamedTemporaryFile(prefix="xlsx", delete=False)
        file_path = tmp.name

        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Fixed Asset Report', cell_overwrite_ok=True)

        # Start Date and End Date
        header_format = xlwt.easyxf("font: bold on; alignment: horiz centre;pattern: pattern solid, fore_colour cyan_ega;")
        content_text_format = xlwt.easyxf("font: bold off; alignment: horiz centre;pattern: pattern solid, fore_colour white;")
        worksheet.write(0, 0, 'Date Range', header_format)
        worksheet.write(2, 0, 'Start Date', header_format)
        worksheet.write(2, 1, 'End Date', header_format)
        worksheet.write(3, 0, str(self.start_date), content_text_format)
        worksheet.write(3, 1, str(self.end_date), content_text_format)

        # Set title
        title_style = xlwt.easyxf("font: bold on, height 200; alignment: horiz centre")
        worksheet.write_merge(1, 2, 3, 5, 'Fixed Asset Report', title_style)

        # Prepare Headers
        header_bold = xlwt.easyxf(
            "font: bold on; alignment: horiz centre;pattern: pattern solid, fore_colour cyan_ega;")
        header_title = {'category': "Category", 'date': "Date", 'disposed_date': "Disposed Date",
                        'description': "Description", 'analytic_tags': 'Analytic Tag', 'journal_entry': "Journal Entry",
                        'po_name': "Purchase Order",
                        'dep_years': "Dep Years", 'beg_cost': "Beg Cost",
                        'purchase': "Purchase", 'disposed': "Disposed",
                        'end_cost': "End Cost", 'beg_acc_dep': "Beg Acc Dep",
                        'depreciation': "Depreciation", 'disposal': "Disposal",
                        'end_acc_dep': "End Acc Dep", 'net_value': "Net Value"}

        headers = ['category', 'date', 'disposed_date', 'description', 'analytic_tags',
                   'journal_entry','po_name', 'dep_years',
                   'beg_cost', 'purchase', 'disposed', 'end_cost',
                   'beg_acc_dep', 'depreciation', 'disposal', 'end_acc_dep',
                   'net_value']

        # Set headers
        column_counter = 0
        for header in headers:
            worksheet.col(column_counter).width = 256 * 18
            worksheet.write(5, column_counter, header_title.get(header), header_bold)
            column_counter += 1

        # Set Freeze pane
        worksheet.set_panes_frozen(True)
        worksheet.set_horz_split_pos(6)

        # write data in sheet
        currency_style = xlwt.XFStyle()
        currency_style.num_format_str = "$#,##0.00"

        total_style = xlwt.XFStyle()
        font = xlwt.Font()
        font.bold = True
        total_style.font = font
        total_style.num_format_str = "$#,##0.00"

        row = 6
        line_col = 0
        style = xlwt.easyxf("font: bold on;")
        total_beg_cost = total_purchase = total_disposed = total_end_cost = 0.00
        total_beg_acc_dep = total_depreciation = total_disposal = 0.00
        total_end_acc_dep = total_net_value = 0.00

        for category_id in category_ids:
            if category_id:
                category_name = category_id.name
            else:
                category_name = 'Undefined'
            worksheet.write(row, 0, category_name, style)
            line_row = row + 1
            categ_beg_cost = categ_purchase = categ_disposed = 0.00
            categ_end_cost = categ_beg_acc_dep = categ_depreciation = 0.00
            categ_disposal = categ_end_acc_dep = categ_net_value = 0.00
            # print ("asset_ids.with_context(zero_lines=self.hide_zero_lines).get_category_data(category_id, move_ids, str(self.start_date), str(self.end_date)): --->>", asset_ids.with_context(zero_lines=self.hide_zero_lines).get_category_data(category_id, move_ids, str(self.start_date), str(self.end_date)))
            for line in asset_ids.with_context(
                    zero_lines=self.hide_zero_lines).get_category_data(
                category_id, move_ids, str(self.start_date), str(self.end_date)):
                line_col = 1
                worksheet.write(line_row, line_col, str(line['date']))
                line_col += 1
                worksheet.write(line_row, line_col, str(
                    line['disposal_date']) if line['disposal_date'] else '')
                line_col += 1
                worksheet.write(line_row, line_col, line['description'])
                line_col += 1
                worksheet.write(line_row, line_col, line['analytic_tags'])
                line_col += 1
                worksheet.write(line_row, line_col, line['journal_entry'])
                line_col += 1
                worksheet.write(line_row, line_col, line['po_name'])
                line_col += 1
                worksheet.write(line_row, line_col, str(line['dep_year']))
                line_col += 1

                worksheet.write(line_row, line_col, line['beg_cost'], currency_style)
                categ_beg_cost += line['beg_cost']
                line_col += 1

                worksheet.write(line_row, line_col, line['purchase'], currency_style)
                categ_purchase += line['purchase']
                line_col += 1

                worksheet.write(line_row, line_col, line['disposed'], currency_style)
                categ_disposed += line['disposed']
                line_col += 1

                worksheet.write(line_row, line_col, line['end_cost'], currency_style)
                categ_end_cost += line['end_cost']
                line_col += 1

                worksheet.write(line_row, line_col, line['beg_acc_dep'], currency_style)
                categ_beg_acc_dep += line['beg_acc_dep']
                line_col += 1

                worksheet.write(line_row, line_col, line['depreciation'], currency_style)
                categ_depreciation += line['depreciation']
                line_col += 1

                worksheet.write(line_row, line_col, line['disposal'], currency_style)
                categ_disposal += line['disposal']
                line_col += 1

                worksheet.write(line_row, line_col, line['end_acc_dep'], currency_style)
                categ_end_acc_dep += line['end_acc_dep']
                line_col += 1

                worksheet.write(line_row, line_col, line['net_value'], currency_style)
                categ_net_value += line['net_value']
                line_col += 1

                line_row += 1

            line_col = 7
            worksheet.write(line_row, line_col, categ_beg_cost, total_style)
            total_beg_cost += categ_beg_cost
            line_col += 1

            worksheet.write(line_row, line_col, categ_purchase, total_style)
            total_purchase += categ_purchase
            line_col += 1

            worksheet.write(line_row, line_col, categ_disposed, total_style)
            total_disposed += categ_disposed
            line_col += 1

            worksheet.write(line_row, line_col, categ_end_cost, total_style)
            total_end_cost += categ_end_cost
            line_col += 1

            worksheet.write(line_row, line_col, categ_beg_acc_dep, total_style)
            total_beg_acc_dep += categ_beg_acc_dep
            line_col += 1

            worksheet.write(line_row, line_col, categ_depreciation, total_style)
            total_depreciation += categ_depreciation
            line_col += 1

            worksheet.write(line_row, line_col, categ_disposal, total_style)
            total_disposal += categ_disposal
            line_col += 1

            worksheet.write(line_row, line_col, categ_end_acc_dep, total_style)
            total_end_acc_dep += categ_end_acc_dep
            line_col += 1

            worksheet.write(line_row, line_col, categ_net_value, total_style)
            total_net_value += categ_net_value
            line_col += 1

            line_row += 1
            row = line_row

        line_col = 6
        row += 2
        worksheet.write(row, line_col, 'Total', style)
        line_col += 1
        worksheet.write(row, line_col, total_beg_cost, total_style)
        line_col += 1

        worksheet.write(row, line_col, total_purchase, total_style)
        line_col += 1

        worksheet.write(row, line_col, total_disposed, total_style)
        line_col += 1

        worksheet.write(row, line_col, total_end_cost, total_style)
        line_col += 1

        worksheet.write(row, line_col, total_beg_acc_dep, total_style)
        line_col += 1

        worksheet.write(row, line_col, total_depreciation, total_style)
        line_col += 1

        worksheet.write(row, line_col, total_disposal, total_style)
        line_col += 1

        worksheet.write(row, line_col, total_end_acc_dep, total_style)
        line_col += 1

        worksheet.write(row, line_col, total_net_value, total_style)

        workbook.save(file_path + ".xlsx")
        buffer_data = base64.encodestring(open(
            file_path + '.xlsx', 'rb').read())
        if buffer_data:
            self.write({'datas': buffer_data})
            filename = 'Fixed Asset Report ' + str(
                self.start_date) + ' TO ' + str(self.end_date) + '.xls'
            return {
                'name': 'Fixed Asset Report',
                'type': 'ir.actions.act_url',
                'url': "web/content/?model=wizard.fixed.asset.report&id=" + str(
                    self.id) + "&filename_field=filename&field=datas&download=true&filename=" + filename,
                'target': 'self',
            }
        return True

    def print_asset_report(self):
        context = dict(self._context) or {}
        [data] = self.read()
        move_data = self.env['account.move']
        move_ids = self.env['account.move'].search([
            ('asset_id', '!=', False), ('asset_id.parent_id', '=', False),
            ('asset_id.state', '!=', 'model'),
            ('asset_id.asset_type', '=', 'purchase')], order='date desc', )
        asset_ids = move_ids.mapped('asset_id') or []
        for asset in asset_ids:
            moves = asset.depreciation_move_ids.filtered(lambda mv: mv.date <= self.end_date)
            if moves:
                move_data |= moves[0]
        data['move_ids'] = move_data and move_data.ids or []
        data['asset_ids'] = asset_ids and asset_ids.ids or []
        data['model_ids'] = asset_ids and asset_ids.mapped('model_id') or []
        datas = {'ids': self._ids, 'model': 'account.asset', 'form': data}
        if context.get('xls_report', False):
            return self.action_print_xls_asset_report(datas)
        return self.env.ref(
            'account_asset_extension.fixed_asset_report').report_action(asset_ids, data=datas)

    def action_print_xls_cip_asset_report(self, data):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        cip_account_ids = self.env['account.account'].search([('is_cip', '=', True)])
        tmp = tempfile.NamedTemporaryFile(prefix="xlsx", delete=False)
        file_path = tmp.name

        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('CIP Asset Report', cell_overwrite_ok=True)

        # Set title
        title_style = xlwt.easyxf("font: bold on, height 200; alignment: horiz centre")
        worksheet.write_merge(1, 2, 3, 5, 'CIP Asset Report', title_style)

        # Prepare Headers
        header_bold = xlwt.easyxf(
            "font: bold on; alignment: horiz centre;pattern: pattern solid, fore_colour cyan_ega;")
        header_title = {'cip_account_header': "CIP Account", 'date': "Date",
                        'cip_account': "CIP Account",
                        'analytic_tag': "Analytic Tag", 'dep_years': 'Dep.Years',
                        'beg_value': "Beginning Value",
                        'current_value': "Purchase", 'disposed': "Disposed",
                        'end_cost': 'End Cost', 'beg_acc_dep': 'Beg Acc Dep',
                        'depreciation': 'Depreciation', 'disposal': 'Disposal',
                        'end_acc_dep': 'End Acc Dep',
                        'net_value': "Net Value"}

        headers = ['cip_account_header', 'date', 'cip_account', 'analytic_tag', 'dep_years',
                   'beg_value', 'current_value', 'disposed', 'end_cost',
                   'beg_acc_dep', 'depreciation', 'disposal', 'end_acc_dep',
                   'net_value']

        # Set headers
        column_counter = 0
        for header in headers:
            worksheet.col(column_counter).width = 256 * 18
            worksheet.write(5, column_counter, header_title.get(header), header_bold)
            column_counter += 1

        # Set Freeze pane
        worksheet.set_panes_frozen(True)
        worksheet.set_horz_split_pos(6)

        # write data in sheet
        currency_style = xlwt.XFStyle()
        currency_style.num_format_str = "$#,##0.00"

        total_style = xlwt.XFStyle()
        font = xlwt.Font()
        font.bold = True
        total_style.font = font
        total_style.num_format_str = "$#,##0.00"

        row = line_row = 6
        style = xlwt.easyxf("font: bold on;")
        total_beginning_value = total_current_value = total_disposed = 0.00
        total_end_cost = total_beg_acc_amt = total_depreciation = 0.00
        total_disposal = total_end_acc_dep = total_net_value = 0.00

        for cip_account_id in cip_account_ids:
            beginning_value = current_value = disposed = 0.00
            end_cost = beg_acc_amt = depreciation = 0.00
            disposal = end_acc_dep = net_value = 0.00
            move_lines = cip_account_id.get_move_line_data(
                str(self.start_date), str(self.end_date))
            if not move_lines:
                continue
            worksheet.write(row, 0, cip_account_id.display_name, style)
            line_row = row + 1
            for line in move_lines:
                line_col = 1
                worksheet.write(line_row, line_col, str(line['date']))
                line_col += 1
                worksheet.write(line_row, line_col, line['cip_account'])
                line_col += 1
                worksheet.write(line_row, line_col, line['analytic_tag'])
                line_col += 1
                worksheet.write(line_row, line_col, '')
                line_col += 1

                worksheet.write(line_row, line_col, line['beginning_value'] or 0.00,
                                style=currency_style)
                beginning_value += line['beginning_value'] or 0.00
                line_col += 1

                worksheet.write(line_row, line_col, line['current_value'] or 0.00,
                                style=currency_style)
                current_value += line['current_value']
                line_col += 1

                worksheet.write(line_row, line_col, line['disposed'] or 0.00,
                                style=currency_style)
                disposed += line['disposed']
                line_col += 1

                worksheet.write(line_row, line_col, line['end_cost'] or 0.00,
                                style=currency_style)
                end_cost += line['end_cost']
                line_col += 1

                worksheet.write(line_row, line_col, line['beg_acc_amt'] or 0.00,
                                style=currency_style)
                beg_acc_amt += line['beg_acc_amt']
                line_col += 1

                worksheet.write(line_row, line_col, line['depreciation'] or 0.00,
                                style=currency_style)
                depreciation += line['depreciation']
                line_col += 1

                worksheet.write(line_row, line_col, line['disposal'] or 0.00,
                                style=currency_style)
                disposal += line['disposal']
                line_col += 1

                worksheet.write(line_row, line_col, line['end_acc_dep'] or 0.00,
                                style=currency_style)
                end_acc_dep += line['end_acc_dep']
                line_col += 1

                worksheet.write(line_row, line_col, line['net_value'] or 0.00,
                                style=currency_style)
                net_value += line['net_value']
                line_col += 1
                line_row += 1
            row = line_row

            line_col = 5
            worksheet.write(line_row, line_col, beginning_value, total_style)
            total_beginning_value += beginning_value
            line_col += 1

            worksheet.write(line_row, line_col, current_value, total_style)
            total_current_value += current_value
            line_col += 1

            worksheet.write(line_row, line_col, disposed, total_style)
            total_disposed += disposed
            line_col += 1

            worksheet.write(line_row, line_col, end_cost, total_style)
            total_end_cost += end_cost
            line_col += 1

            worksheet.write(line_row, line_col, beg_acc_amt, total_style)
            total_beg_acc_amt += beg_acc_amt
            line_col += 1

            worksheet.write(line_row, line_col, depreciation, total_style)
            total_depreciation += depreciation
            line_col += 1

            worksheet.write(line_row, line_col, disposal, total_style)
            total_disposal += disposal
            line_col += 1

            worksheet.write(line_row, line_col, end_acc_dep, total_style)
            total_end_acc_dep += end_acc_dep
            line_col += 1

            worksheet.write(line_row, line_col, net_value, total_style)
            total_net_value += net_value
            line_col += 1

            line_row += 1
            row = line_row

        line_col = 4
        row += 2
        worksheet.write(row, line_col, 'Grand Total', style)
        line_col += 1
        worksheet.write(row, line_col, total_beginning_value, total_style)
        line_col += 1

        worksheet.write(row, line_col, total_current_value, total_style)
        line_col += 1

        worksheet.write(row, line_col, total_disposed, total_style)
        line_col += 1

        worksheet.write(row, line_col, total_end_cost, total_style)
        line_col += 1

        worksheet.write(row, line_col, total_beg_acc_amt, total_style)
        line_col += 1

        worksheet.write(row, line_col, total_depreciation, total_style)
        line_col += 1

        worksheet.write(row, line_col, total_disposal, total_style)
        line_col += 1

        worksheet.write(row, line_col, total_end_acc_dep, total_style)
        line_col += 1

        worksheet.write(row, line_col, total_net_value, total_style)

        workbook.save(file_path + ".xlsx")
        buffer_data = base64.encodestring(open(
            file_path + '.xlsx', 'rb').read())
        if buffer_data:
            self.write({'datas': buffer_data})
            filename = 'CIP Asset Report ' + str(
                self.start_date) + ' TO ' + str(self.end_date) + '.xls'
            return {
                'name': 'CIP Asset Report',
                'type': 'ir.actions.act_url',
                'url': "web/content/?model=wizard.fixed.asset.report&id=" + str(
                    self.id) + "&filename_field=filename&field=datas&download=true&filename=" + filename,
                'target': 'self',
            }
        return True

    def print_asset_cip_report(self):
        context = dict(self._context) or {}
        [data] = self.read()
        datas = {'ids': self._ids, 'model': 'account.move.line', 'form': data}
        if context.get('xls_report', False):
            return self.action_print_xls_cip_asset_report(datas)
        return self.env.ref(
            'account_asset_extension.cip_asset_report').report_action(self, data=datas)

    def action_print_report(self):
        self.ensure_one()
        start_date_year = self.start_date.strftime("%Y")
        end_date_year = self.end_date.strftime("%Y")
        if start_date_year != end_date_year:
            raise UserError(_("Date Range should be in same year."))
        if self.end_date < self.start_date:
            raise UserError(_('To date should be greater than from date.'))
        if self.report_type == 'asset':
            return self.print_asset_report()
        else:
            return self.print_asset_cip_report()
