# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################
"""Purchasing Summary Report excel."""
import base64
import time
from datetime import datetime, timedelta

import numpy as np
import pytz
import xlsxwriter

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class WizardPurchaseOrderCustomReport(models.TransientModel):
    """TransientModel For Purchasing Summary Report."""

    _name = 'wizard.purchase.order.custom.report'
    _description = "Purchase Order Custom Report."

    name = fields.Char(string='File Name')
    file_download = fields.Binary('File to Download')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    details = fields.Selection([('vendor', 'Vendor'),
                                ('requestor', 'Requestor'),
                                ('purpose', 'Purpose')], string='Details')
    received_order = fields.Selection([('yes', 'Yes'),
                                       ('no', 'No')], string='Only Received Orders', default='no')
    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env.company)
    state = fields.Selection([('init', 'init'),
                              ('done', 'done')], string='Status', readonly=True, default='init')

    @api.constrains('start_date', 'end_date')
    def check_date(self):
        """
        Check start date is not grater than end date.

        :raise: Raise Validation Error
        """
        if self.start_date and self.end_date and (self.start_date > self.end_date):
            raise ValidationError(_('End date should be greater than start date.'))

    def _get_report_data(self, purchase_order_ids):
        """
        Get Data for Report from purchase order.

        :param purchase_order_ids: Browsable  purchase.order Records
        :returns:
            - po_count(Integer): Count of Purchase Order
            - po_order_price(Float): Total Price Of Purchase Order in $
            - avg_day(Float): Average Day to receive purchase order
            - return_po_count(Integer): Total Return Purchase Order count
            - len(escalation_count)(Integer): Escalation po Count
        """
        po_order_price, cal_amt = 0.0, 0.0
        return_po_count = 0
        avg_time_list = []

        # Get Purchase Order Count
        po_count = len(purchase_order_ids)

        # Get Escalation Count
        escalation_count = purchase_order_ids.filtered(
            lambda po_id: po_id.escalation in ['level_two', 'level_three'])

        usd_currency_id = self.env['res.currency'].search([('name', '=', 'USD')])
        date = fields.Date.today()
        for po_rec in purchase_order_ids:
            # Get Purchase Order Total Amount(Price)
            if po_rec.currency_id.id != usd_currency_id.id:
                amount = po_rec.currency_id._convert(po_rec.amount_total, usd_currency_id,
                                                     po_rec.company_id, date)
            else:
                amount = po_rec.amount_total
            po_order_price += amount

            # Get Average Time
            po_confirm_date = datetime.strptime(str(po_rec.date_approve), '%Y-%m-%d %H:%M:%S')
            po_confirm_date = po_confirm_date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(
                self.env.user.tz or 'UTC'))
            po_confirm_date = po_confirm_date.strftime("%m-%d-%Y %H:%M:%S")
            po_confirm_date = datetime.strptime(po_confirm_date, "%m-%d-%Y %H:%M:%S")

            receive_date = []
            picking_domain = [('picking_type_id.code', '=', 'incoming'),
                              ('purchase_id', '=', po_rec.id)]
            if self.received_order == 'yes':
                picking_domain += [('state', '=', 'done')]
            for picking_rec in self.env['stock.picking'].search(picking_domain):
                if picking_rec.state == 'done' and picking_rec.date_done:
                    shipment_done_date = datetime.strptime(
                        str(picking_rec.date_done), '%Y-%m-%d %H:%M:%S')
                    shipment_done_date = shipment_done_date.replace(tzinfo=pytz.utc).astimezone(
                        pytz.timezone(self.env.user.tz or 'UTC'))
                    receive_date.append(shipment_done_date.strftime("%m-%d-%Y %H:%M:%S"))
            if receive_date:
                sec = [time.mktime(datetime.strptime(d, "%m-%d-%Y %H:%M:%S").timetuple()) for d in
                       receive_date]
                effective_date = datetime.fromtimestamp(np.mean(sec))
                sec_to_receive = (effective_date - po_confirm_date).total_seconds()
                days_to_receive = sec_to_receive / 86400
                avg_time_list.append(days_to_receive * po_rec.amount_total)
                cal_amt += days_to_receive * po_rec.amount_total

            # Return Purchase order count
            if po_rec.picking_ids.filtered(
                    lambda p: p.picking_type_id.code == 'outgoing' and p.state == 'done'):
                return_po_count += 1

        # Average Day to received
        if cal_amt > 0.0 and po_order_price > 0.0:
            avg_day = cal_amt / po_order_price
        else:
            avg_day = 0.0
        return po_count, po_order_price, avg_day, return_po_count, len(escalation_count)

    def create_po_report(self):
        """
        Create excel Report.

        :return: wizard with excel file
        """
        xls_file_name = 'Purchasing Summary Report.xlsx'
        workbook = xlsxwriter.Workbook('/tmp/' + xls_file_name)
        title_format = workbook.add_format({'bold': True,
                                            'align': 'center',
                                            'valign': 'vcenter',
                                            'font_size': 14,
                                            'border': 1,
                                            'text_wrap': True})
        header_format = workbook.add_format({'bold': True,
                                             'align': 'center',
                                             'valign': 'vcenter',
                                             'font_size': 12,
                                             'border': 1,
                                             'text_wrap': True})
        header_content_format = workbook.add_format({'font_size': 12,
                                                     'border': 1,
                                                     'text_wrap': True})
        header_content_format.set_align('center')
        header_content_format.set_align('vcenter')

        content_text_format = workbook.add_format({'align': 'left',
                                                   'valign': 'vcenter',
                                                   'font_size': 12, 'border': 1,
                                                   'text_wrap': True})
        content_format = workbook.add_format({'align': 'right',
                                              'valign': 'vcenter',
                                              'font_size': 12,
                                              'border': 1,
                                              'text_wrap': True})
        content_format.set_num_format(4)
        content_format_integer = workbook.add_format({'align': 'right',
                                                      'valign': 'vcenter',
                                                      'font_size': 12,
                                                      'border': 1,
                                                      'text_wrap': True})
        content_format_integer.set_num_format(3)

        total_title_format = workbook.add_format({'bold': True,
                                                  'align': 'center',
                                                  'valign': 'vcenter',
                                                  'font_size': 12,
                                                  'border': 1,
                                                  'text_wrap': True})
        total_content_format = workbook.add_format({'bold': True,
                                                    'align': 'right',
                                                    'valign': 'vcenter',
                                                    'font_size': 12,
                                                    'border': 1,
                                                    'text_wrap': True})
        total_content_format.set_num_format(4)
        total_content_format_integer = workbook.add_format({'bold': True,
                                                            'align': 'right',
                                                            'valign': 'vcenter',
                                                            'font_size': 12,
                                                            'border': 1,
                                                            'text_wrap': True})
        total_content_format_integer.set_num_format(3)

        worksheet = workbook.add_worksheet('MOQ')
        raw = 5
        col = 0
        worksheet.set_column(col, col + 9, 21)
        worksheet.set_default_row(22)
        title_text = 'Purchasing Summary Report'
        if self.details:
            worksheet.merge_range('A1:G1', title_text, title_format)
        else:
            worksheet.merge_range('A1:F1', title_text, title_format)
        worksheet.merge_range('A3:B3', 'Date', header_format)
        worksheet.merge_range('C3:D3', 'Only Received Orders', header_format)
        worksheet.merge_range('E3:F3', 'Details', header_format)

        date_str = self.start_date.strftime("%Y-%m-%d") + ' to ' + \
                   self.end_date.strftime("%Y-%m-%d")
        worksheet.merge_range('A4:B4', date_str, header_content_format)

        if self.received_order == 'yes':
            received_order = 'Yes'
        else:
            received_order = 'No'
        worksheet.merge_range('C4:D4', received_order, header_content_format)

        if self.details:
            details = dict(self._fields['details'].selection).get(self.details)
        else:
            details = 'None'
        worksheet.merge_range('E4:F4', details, header_content_format)

        worksheet.write(raw, col, 'Project', header_format)
        if self.details:
            if self.details == 'vendor':
                worksheet.write(raw, col + 1, 'Vendor', header_format)
            elif self.details == 'requestor':
                worksheet.write(raw, col + 1, 'Requestor', header_format)
            elif self.details == 'purpose':
                worksheet.write(raw, col + 1, 'Purpose', header_format)
            worksheet.write(raw, col + 2, 'No. of Orders', header_format)
            worksheet.write(raw, col + 3, 'Order Amount', header_format)
            worksheet.write(raw, col + 4, 'Average time to Receive', header_format)
            worksheet.write(raw, col + 5, 'Order with Returns', header_format)
            worksheet.write(raw, col + 6, 'Escalation', header_format)
        else:
            worksheet.write(raw, col + 1, 'No. of Orders', header_format)
            worksheet.write(raw, col + 2, 'Order Amount', header_format)
            worksheet.write(raw, col + 3, 'Average time to Receive', header_format)
            worksheet.write(raw, col + 4, 'Order with Returns', header_format)
            worksheet.write(raw, col + 5, 'Escalation', header_format)
        raw += 1
        start_date = self.start_date
        end_date = self.end_date

        # Get Start Date With User Timezone
        min_time = datetime.min.time().strftime('%H:%M:%S')
        min_time = datetime.strptime(min_time, "%H:%M:%S")
        min_time = min_time.time()
        start_date = datetime.combine(start_date, min_time)
        start_date = datetime.strptime(str(start_date), '%Y-%m-%d %H:%M:%S')
        start_date = pytz.timezone(self.env.user.tz or 'UTC').localize(start_date)
        start_date = start_date.astimezone(pytz.timezone('UTC'))
        start_date = start_date.strftime("%m-%d-%Y %H:%M:%S")
        start_date = datetime.strptime(start_date, "%m-%d-%Y %H:%M:%S")

        # Get End Date With User Timezone
        max_time = datetime.max.time().strftime('%H:%M:%S')
        max_time = datetime.strptime(max_time, "%H:%M:%S")
        max_time = max_time.time()
        end_date = datetime.combine(end_date, max_time)
        end_date = end_date + timedelta(seconds=1)
        end_date = datetime.strptime(str(end_date), '%Y-%m-%d %H:%M:%S')
        end_date = pytz.timezone(self.env.user.tz or 'UTC').localize(end_date)
        end_date = end_date.astimezone(pytz.timezone('UTC'))
        end_date = end_date.strftime("%m-%d-%Y %H:%M:%S")
        end_date = datetime.strptime(end_date, "%m-%d-%Y %H:%M:%S")

        purchase_order_obj = self.env["purchase.order"]
        purchase_ids = purchase_order_obj.search([('state', 'in', ['purchase', 'done']),
                                                  ('company_id', '=', self.company_id.id),
                                                  ('date_approve', '>=', start_date),
                                                  ('date_approve', '<=', end_date)])

        if self.received_order == 'yes':
            po_ids = purchase_ids.filtered(lambda po_id: po_id.picking_count == 0 or (
                    po_id.picking_count > 0 and
                    all([x.product_type != 'service' and x.product_qty <= x.qty_received or
                         x.product_type == 'service' for x in po_id.order_line])) or (
                                                                 po_id.picking_count > 0 and
                                                                 all([x.state in [
                                                                     'done'] and x.picking_type_code == 'incoming'
                                                                      for x in po_id.picking_ids])))
        else:
            po_ids = purchase_ids.filtered(lambda po_id: po_id.state != 'cancel')

        department_ids = po_ids.mapped('department_id')
        total_po_count, total_po_order_price, total_avg_time, total_po_return_qty, \
        total_escalation_count = 0.0, 0.0, 0.0, 0.0, 0.0
        for department_id in department_ids:
            department_po_ids = po_ids.filtered(lambda po_id, dept_id=department_id:
                                                po_id.department_id.id == dept_id.id)
            if self.details:
                if self.details == 'vendor':
                    partner_ids = department_po_ids.mapped('partner_id')
                    for partner_id in partner_ids:
                        worksheet.write(raw, 0, department_id.name, content_text_format)
                        worksheet.write(raw, 1, partner_id.name, content_text_format)
                        partner_po_ids = department_po_ids.filtered(
                            lambda po_id, ptr_id=partner_id: po_id.partner_id.id == ptr_id.id)
                        po_count, po_order_price, avg_time, po_return_qty, escalation_count = \
                            self._get_report_data(partner_po_ids)
                        total_po_count += po_count
                        total_po_order_price += po_order_price
                        total_avg_time += avg_time
                        total_po_return_qty += po_return_qty
                        total_escalation_count += escalation_count
                        worksheet.write(raw, 2, po_count, content_format_integer)
                        worksheet.write(raw, 3, po_order_price, content_format)
                        worksheet.write(raw, 4, avg_time, content_format)
                        worksheet.write(raw, 5, po_return_qty, content_format_integer)
                        worksheet.write(raw, 6, escalation_count, content_format_integer)
                        raw += 1
                elif self.details == 'requestor':
                    user_ids = department_po_ids.mapped('user_id')
                    for user_id in user_ids:
                        worksheet.write(raw, 0, department_id.name, content_text_format)
                        worksheet.write(raw, 1, user_id.name, content_text_format)
                        user_po_ids = department_po_ids.filtered(
                            lambda po_id, usr_id=user_id: po_id.user_id.id == usr_id.id)
                        po_count, po_order_price, avg_time, po_return_qty, escalation_count = \
                            self._get_report_data(user_po_ids)
                        total_po_count += po_count
                        total_po_order_price += po_order_price
                        total_avg_time += avg_time
                        total_po_return_qty += po_return_qty
                        total_escalation_count += escalation_count
                        worksheet.write(raw, 2, po_count, content_format_integer)
                        worksheet.write(raw, 3, po_order_price, content_format)
                        worksheet.write(raw, 4, avg_time, content_format)
                        worksheet.write(raw, 5, po_return_qty, content_format_integer)
                        worksheet.write(raw, 6, escalation_count, content_format_integer)
                        raw += 1
                elif self.details == 'purpose':
                    purpose_type_ids = department_po_ids.mapped('purpose_type')
                    for purpose_type_id in purpose_type_ids:
                        worksheet.write(raw, 0, department_id.name, content_text_format)
                        worksheet.write(raw, 1, purpose_type_id.name, content_text_format)
                        purpose_po_ids = department_po_ids.filtered(
                            lambda po_id, pps_typ_id=purpose_type_id: po_id.purpose_type.id ==
                                                                      pps_typ_id.id)
                        po_count, po_order_price, avg_time, po_return_qty, escalation_count = \
                            self._get_report_data(purpose_po_ids)
                        total_po_count += po_count
                        total_po_order_price += po_order_price
                        total_avg_time += avg_time
                        total_po_return_qty += po_return_qty
                        total_escalation_count += escalation_count
                        worksheet.write(raw, 2, po_count, content_format_integer)
                        worksheet.write(raw, 3, po_order_price, content_format)
                        worksheet.write(raw, 4, avg_time, content_format)
                        worksheet.write(raw, 5, po_return_qty, content_format_integer)
                        worksheet.write(raw, 6, escalation_count, content_format_integer)
                        raw += 1
            else:
                worksheet.write(raw, 0, department_id.name, content_text_format)
                po_count, po_order_price, avg_time, po_return_qty, escalation_count = \
                    self._get_report_data(department_po_ids)
                total_po_count += po_count
                total_po_order_price += po_order_price
                total_avg_time += avg_time
                total_po_return_qty += po_return_qty
                total_escalation_count += escalation_count
                worksheet.write(raw, col + 1, po_count, content_format_integer)
                worksheet.write(raw, col + 2, po_order_price, content_format)
                worksheet.write(raw, col + 3, avg_time or 0, content_format)
                worksheet.write(raw, col + 4, po_return_qty, content_format_integer)
                worksheet.write(raw, col + 5, escalation_count, content_format_integer)
                raw += 1

        # Undefined Department
        undefined_dep_po_ids = po_ids.filtered(lambda po_id: not po_id.department_id)
        if undefined_dep_po_ids:
            if self.details:
                if self.details == 'vendor':
                    partner_ids = undefined_dep_po_ids.mapped('partner_id')
                    for partner_id in partner_ids:
                        worksheet.write(raw, 0, 'Undefined', content_text_format)
                        worksheet.write(raw, 1, partner_id.name, content_text_format)
                        partner_po_ids = undefined_dep_po_ids.filtered(
                            lambda po_id: po_id.partner_id.id == partner_id.id)
                        po_count, po_order_price, avg_time, po_return_qty, escalation_count = \
                            self._get_report_data(partner_po_ids)
                        total_po_count += po_count
                        total_po_order_price += po_order_price
                        total_avg_time += avg_time
                        total_po_return_qty += po_return_qty
                        total_escalation_count += escalation_count
                        worksheet.write(raw, 2, po_count, content_format_integer)
                        worksheet.write(raw, 3, po_order_price, content_format)
                        worksheet.write(raw, 4, avg_time, content_format)
                        worksheet.write(raw, 5, po_return_qty, content_format_integer)
                        worksheet.write(raw, 6, escalation_count, content_format_integer)
                        raw += 1
                elif self.details == 'requestor':
                    user_ids = undefined_dep_po_ids.mapped('user_id')
                    for user_id in user_ids:
                        worksheet.write(raw, 0, 'Undefined', content_text_format)
                        worksheet.write(raw, 1, user_id.name, content_text_format)
                        user_po_ids = undefined_dep_po_ids.filtered(
                            lambda po_id: po_id.user_id.id == user_id.id)
                        po_count, po_order_price, avg_time, po_return_qty, escalation_count = \
                            self._get_report_data(user_po_ids)
                        total_po_count += po_count
                        total_po_order_price += po_order_price
                        total_avg_time += avg_time
                        total_po_return_qty += po_return_qty
                        total_escalation_count += escalation_count
                        worksheet.write(raw, 2, po_count, content_format_integer)
                        worksheet.write(raw, 3, po_order_price, content_format)
                        worksheet.write(raw, 4, avg_time, content_format)
                        worksheet.write(raw, 5, po_return_qty, content_format_integer)
                        worksheet.write(raw, 6, escalation_count, content_format_integer)
                        raw += 1
                elif self.details == 'purpose':
                    purpose_type_ids = undefined_dep_po_ids.mapped('purpose_type')
                    for purpose_type_id in purpose_type_ids:
                        worksheet.write(raw, 0, 'Undefined', content_text_format)
                        worksheet.write(raw, 1, purpose_type_id.name, content_text_format)
                        purpose_po_ids = undefined_dep_po_ids.filtered(
                            lambda po_id: po_id.purpose_type.id == purpose_type_id.id)
                        po_count, po_order_price, avg_time, po_return_qty, escalation_count = \
                            self._get_report_data(purpose_po_ids)
                        total_po_count += po_count
                        total_po_order_price += po_order_price
                        total_avg_time += avg_time
                        total_po_return_qty += po_return_qty
                        total_escalation_count += escalation_count
                        worksheet.write(raw, 2, po_count, content_format_integer)
                        worksheet.write(raw, 3, po_order_price, content_format)
                        worksheet.write(raw, 4, avg_time, content_format)
                        worksheet.write(raw, 5, po_return_qty, content_format_integer)
                        worksheet.write(raw, 6, escalation_count, content_format_integer)
                        raw += 1
            else:
                worksheet.write(raw, 0, 'Undefined', content_text_format)
                po_count, po_order_price, avg_time, po_return_qty, escalation_count = \
                    self._get_report_data(undefined_dep_po_ids)
                total_po_count += po_count
                total_po_order_price += po_order_price
                total_avg_time += avg_time
                total_po_return_qty += po_return_qty
                total_escalation_count += escalation_count
                worksheet.write(raw, col + 1, po_count, content_format_integer)
                worksheet.write(raw, col + 2, po_order_price, content_format)
                worksheet.write(raw, col + 3, avg_time or 0, content_format)
                worksheet.write(raw, col + 4, po_return_qty, content_format_integer)
                worksheet.write(raw, col + 5, escalation_count, content_format_integer)
                raw += 1

        if self.details:
            merge_range = 'A' + str(raw + 1) + ':' + 'B' + str(raw + 1)
            worksheet.merge_range(merge_range, 'Total', total_title_format)
            worksheet.write(raw, 2, total_po_count, total_content_format_integer)
            worksheet.write(raw, 3, total_po_order_price, total_content_format)
            worksheet.write(raw, 4, total_avg_time, total_content_format)
            worksheet.write(raw, 5, total_po_return_qty, total_content_format_integer)
            worksheet.write(raw, 6, total_escalation_count, total_content_format_integer)
        else:
            worksheet.write(raw, 0, 'Total', total_title_format)
            worksheet.write(raw, 1, total_po_count, total_content_format_integer)
            worksheet.write(raw, 2, total_po_order_price, total_content_format)
            worksheet.write(raw, 3, total_avg_time, total_content_format)
            worksheet.write(raw, 4, total_po_return_qty, total_content_format_integer)
            worksheet.write(raw, 5, total_escalation_count, total_content_format_integer)
        workbook.close()
        self.write(
            {'file_download': base64.b64encode(open('/tmp/' + xls_file_name, 'rb').read()),
             'name': xls_file_name, 'state': 'done'})
        return {'name': 'Purchasing Summary Report',
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'view_mode': 'form',
                'res_id': self.id,
                'target': 'new'}

    def do_go_back(self):
        """
        For back to Selection Wizard.

        :return: selection wizard with existing
        """
        self.state = 'init'
        return {'name': 'Purchasing Summary Report',
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'target': 'new'}
