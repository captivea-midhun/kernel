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
from odoo.tools import float_round
from odoo.tools.misc import xlwt


class DeferredExpensesReport(models.TransientModel):
    _name = "deferred.expenses.report"
    _description = "Deferred Expense Report"

    datas = fields.Binary('File')
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')

    def prepare_data(self, date_from, date_to):
        data_dict_lst = []
        move_ids = self.env['account.move']
        asset_ids = self.env['account.asset'].search([
            ('asset_type', '=', 'expense'), ('parent_id', '=', False),
            ('state', '!=', 'model'), ('acquisition_date', '<=', date_to)])

        for asset in asset_ids:
            moves = asset.depreciation_move_ids.filtered(
                lambda mv: mv.date <= date_to or mv.asset_id.acquisition_date <= date_to)
            if moves:
                move_ids |= moves[0]

        for move in move_ids:
            beg_accum_amort = period_amort = 0.00
            asset_id = move.asset_id
            currency = move.asset_id.currency_id

            if move.asset_id.method_period == '12':
                prior_month_move_ids = asset_id.depreciation_move_ids.filtered(
                    lambda mv: mv.date.year <= date_to.year and mv.date < date_from)
            else:
                prior_month_move_ids = move.asset_id.depreciation_move_ids.filtered(
                    lambda mv: mv.date < date_from)

            if prior_month_move_ids:
                beg_accum_amort = prior_month_move_ids[0].asset_depreciated_value
            beg_accum_amort = float_round(
                beg_accum_amort, precision_rounding=currency.rounding)

            if move.asset_id.method_period == '12':
                current_month_move_id = move.asset_id.depreciation_move_ids.filtered(
                    lambda
                        mv: mv.date.year == date_to.year and mv.date >= date_from and mv.date <= date_to)
            else:
                current_month_move_id = move.asset_id.depreciation_move_ids.filtered(
                    lambda mv: mv.date >= date_from and mv.date <= date_to)

            if current_month_move_id:
                period_amort = float_round(sum(
                    current_month_move_id.mapped('amount_total')),
                    precision_rounding=currency.rounding)

            ending_accum_amort = beg_accum_amort + period_amort
            ending_accum_amort = float_round(
                ending_accum_amort, precision_rounding=currency.rounding)

            remaining_balance = asset_id.original_value - ending_accum_amort
            remaining_balance = float_round(
                remaining_balance, precision_rounding=currency.rounding)

            method_period = int(asset_id.method_period)
            if method_period == 12:
                method_number = asset_id.method_number * method_period
            else:
                method_number = asset_id.method_number

            if (remaining_balance == 0.00 and period_amort > 0) or remaining_balance > 0:
                data_dict = {
                    'date': asset_id.acquisition_date,  # move.date
                    'name': asset_id.name,
                    'original_value': asset_id.original_value or 0.00,
                    'expense_account': asset_id.account_depreciation_expense_id.display_name or '',
                    'amort_period': method_number,
                    'beg_accum_amort': beg_accum_amort,
                    'period_amort': period_amort,
                    'ending_accum_amort': ending_accum_amort,
                    'remaining_balance': remaining_balance
                }
                data_dict_lst.append(data_dict)
        return sorted(data_dict_lst, key=lambda i: i['date'])

    def print_deferred_expenses_xls_report(self):
        from_date_year = self.date_from.strftime("%Y")
        to_date_year = self.date_to.strftime("%Y")
        if from_date_year != to_date_year:
            raise UserError(
                _("Date Range should be in same year."))
        if self.date_to < self.date_from:
            raise UserError(_('End date should be greater than start date.'))

        tmp = tempfile.NamedTemporaryFile(prefix="xlsx", delete=False)
        file_path = tmp.name

        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet(
            'Deferred Expense Report', cell_overwrite_ok=True)

        # Set title
        title_style = xlwt.easyxf(
            "font: bold on, height 200; alignment: horiz centre")
        worksheet.write_merge(
            1, 2, 3, 5, 'Deferred Expense Report', title_style)

        # Prepare Headers
        header_bold = xlwt.easyxf(
            "font: bold on; alignment: horiz centre;pattern: pattern solid, fore_colour cyan_ega;")
        header_title = {'date': "Date", 'name': "Name",
                        'expense_account': 'Expense Account',
                        'amort_period': 'Amort. Period',
                        'orignal_value': 'Original value',
                        'beg_accum_amort': 'Beg. Accum Amort',
                        'period_amort': 'Period Amort',
                        'ending_accum_amort': 'Ending Accum. Amort',
                        'remaining_balance': 'Remaining Balance'}

        headers = ['date', 'name', 'expense_account', 'amort_period',
                   'orignal_value', 'beg_accum_amort', 'period_amort',
                   'ending_accum_amort', 'remaining_balance']

        # Set headers
        column_counter = 0
        for header in headers:
            worksheet.col(column_counter).width = 256 * 18
            worksheet.write(
                5, column_counter, header_title.get(header), header_bold)
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

        total_original_value = total_beg_accum_amort = 0.00
        total_period_amort = total_ending_accum_amort = 0.00
        total_remaining_balance = 0.00

        row = 6
        line_col = 0
        data_dict_lst = self.prepare_data(self.date_from, self.date_to)
        for data in data_dict_lst:
            line_col = 0
            worksheet.write(row, line_col, str(data.get('date')))
            line_col += 1

            worksheet.write(row, line_col, data.get('name'))
            line_col += 1

            worksheet.write(row, line_col, data.get('expense_account'))
            line_col += 1

            worksheet.write(row, line_col, data.get('amort_period'))
            line_col += 1

            worksheet.write(row, line_col, data.get('original_value'),
                            currency_style)
            total_original_value += data.get('original_value')
            line_col += 1

            worksheet.write(row, line_col, data.get('beg_accum_amort'),
                            currency_style)
            total_beg_accum_amort += data.get('beg_accum_amort')
            line_col += 1

            worksheet.write(row, line_col, data.get('period_amort'),
                            currency_style)
            total_period_amort += data.get('period_amort')
            line_col += 1

            worksheet.write(row, line_col, data.get('ending_accum_amort'),
                            currency_style)
            total_ending_accum_amort += data.get('ending_accum_amort')
            line_col += 1

            worksheet.write(row, line_col, data.get('remaining_balance'),
                            currency_style)
            total_remaining_balance += data.get('remaining_balance')
            line_col += 1
            row += 1

        line_col = 3
        row += 1
        worksheet.write(row, line_col, 'Total', xlwt.easyxf("font: bold on;"))
        line_col += 1
        worksheet.write(row, line_col, total_original_value, total_style)
        line_col += 1

        worksheet.write(row, line_col, total_beg_accum_amort, total_style)
        line_col += 1

        worksheet.write(row, line_col, total_period_amort, total_style)
        line_col += 1

        worksheet.write(row, line_col, total_ending_accum_amort, total_style)
        line_col += 1

        worksheet.write(row, line_col, total_remaining_balance, total_style)

        workbook.save(file_path + ".xlsx")
        buffer_data = base64.encodestring(open(
            file_path + '.xlsx', 'rb').read())
        if buffer_data:
            self.write({'datas': buffer_data})
            filename = 'Deferred Expense Report ' + str(
                self.date_from) + ' TO ' + str(self.date_to) + '.xls'
            return {
                'name': 'Deferred Expense Report',
                'type': 'ir.actions.act_url',
                'url': "web/content/?model=deferred.expenses.report&id=" + str(
                    self.id) + "&filename_field=filename&field=datas&download=true&filename=" + filename,
                'target': 'self',
            }
        return True

    def print_deferred_expenses_pdf_report(self):
        from_date_year = self.date_from.strftime("%Y")
        to_date_year = self.date_to.strftime("%Y")
        if from_date_year != to_date_year:
            raise UserError(
                _("Date Range should be in same year."))
        if self.date_to < self.date_from:
            raise UserError(_('End date should be greater than start date.'))
        return self.env.ref(
            'deferred_expenses_rpt.action_download_pdf_deferred_expenses').report_action(self)
