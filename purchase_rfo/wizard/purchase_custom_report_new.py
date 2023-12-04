# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################
"""Purchasing Summary Report excel."""
import base64
from datetime import datetime, timedelta

import pytz
import xlsxwriter

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PurchaseOrderCustomReport(models.TransientModel):
    """TransientModel For Purchasing Summary Report."""

    _name = 'purchase.order.custom.report'
    _description = "Purchase Order Custom Report."

    name = fields.Char(string='File Name')
    file_download = fields.Binary('File to Download')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    purpose = fields.Boolean(string='Purpose')
    expected_date = fields.Boolean(string='Expected Date')
    confirm_date = fields.Boolean(string='Confirmation Date')
    desired_date = fields.Boolean(string='Desired Date')
    days_to_maj_dis = fields.Boolean(string='Days to Major Disruption')
    alt_ven_days_to_receive = fields.Boolean(string='Alternative Vendor Days to Receive')
    track_no = fields.Boolean(string='Tracking Number')
    hr_department_ids = fields.Many2many('hr.department', string='Projects')
    report_type = fields.Selection([
        ('received', 'Products Received'),
        ('unreceived', 'Products Unreceived'),
        ('all', 'All Products')], string='Report Type', default='all')
    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env.company)
    state = fields.Selection([('init', 'init'),
                              ('done', 'done')], string='Status', readonly=True, default='init')

    @api.constrains('start_date', 'end_date')
    def check_date(self):
        """
        Check start date is not greater than end date.

        :raise: Raise Validation Error
        """
        if self.start_date and self.end_date and (self.start_date > self.end_date):
            raise ValidationError(_('End date should be greater than start date.'))

    def create_po_report(self):
        """
        Create excel Report.

        :return: wizard with excel file
        """
        xls_file_name = 'Purchase Custom Report.xlsx'
        workbook = xlsxwriter.Workbook('/tmp/' + xls_file_name)
        report_type = self.report_type
        department_ids = self.hr_department_ids.ids
        if report_type in ('received', 'all'):
            received_title_format = workbook.add_format({'bold': True,
                                                         'align': 'center',
                                                         'valign': 'vcenter',
                                                         'font_size': 14,
                                                         'border': 1,
                                                         'text_wrap': True,
                                                         'bg_color': '#C3D69B'})
        if report_type in ('unreceived', 'all'):
            unreceived_title_format = workbook.add_format({'bold': True,
                                                           'align': 'center',
                                                           'valign': 'vcenter',
                                                           'font_size': 14,
                                                           'border': 1,
                                                           'text_wrap': True,
                                                           'bg_color': '#FAC090'})
        header_format = workbook.add_format({'bold': True,
                                             'align': 'center',
                                             'valign': 'vcenter',
                                             'font_size': 12,
                                             'border': 1,
                                             'text_wrap': True})
        header_content_format = workbook.add_format({'align': 'center',
                                                     'valign': 'vcenter',
                                                     'font_size': 12,
                                                     'border': 1,
                                                     'text_wrap': True})

        content_text_format = workbook.add_format({'align': 'left',
                                                   'valign': 'vcenter',
                                                   'font_size': 12, 'border': 1,
                                                   'text_wrap': True})

        total_title_format = workbook.add_format({'bold': True,
                                                  'align': 'center',
                                                  'valign': 'vcenter',
                                                  'font_size': 12,
                                                  'border': 1,
                                                  'text_wrap': True})
        total_content_format_integer = workbook.add_format({'bold': True,
                                                            'align': 'right',
                                                            'valign': 'vcenter',
                                                            'font_size': 12,
                                                            'border': 1,
                                                            'text_wrap': True})
        total_content_format_integer.set_num_format(2)
        if report_type in ('received', 'all'):
            worksheet = workbook.add_worksheet('Product Received')
        else:
            worksheet = workbook.add_worksheet('Product UnReceived')
        raw = 5
        col = 0
        worksheet.set_column(col, col + 16, 23)
        worksheet.set_default_row(23)
        if report_type in ('received', 'all'):
            received_title_text = 'Products Received Report'
        if report_type in ('unreceived', 'all'):
            unreceived_title_text = 'Products UnReceived Report'
        # if report_type == 'all':
        #     title_text = 'All Products Report'
        if report_type in ('received', 'all'):
            worksheet.merge_range('A1:G1', received_title_text, received_title_format)
        else:
            worksheet.merge_range('A1:G1', unreceived_title_text, unreceived_title_format)
        worksheet.merge_range('A3:B3', 'Date', header_format)
        date_str = self.start_date.strftime("%Y-%m-%d") + ' to ' + \
                   self.end_date.strftime("%Y-%m-%d")

        worksheet.merge_range('A4:B4', date_str, header_content_format)
        worksheet.write(raw, col, 'Project', header_format)
        worksheet.write(raw, col + 1, 'Requestor', header_format)
        worksheet.write(raw, col + 2, 'Vendor', header_format)
        worksheet.write(raw, col + 3, 'PO', header_format)
        worksheet.write(raw, col + 4, 'SKU', header_format)
        worksheet.write(raw, col + 5, 'Product', header_format)
        worksheet.write(raw, col + 6, 'Received By', header_format)
        worksheet.write(raw, col + 7, 'Value Received', header_format)
        worksheet.write(raw, col + 8, 'Quantity Received', header_format)
        worksheet.write(raw, col + 9, 'Total Ordered', header_format)
        worksheet.write(raw, col + 10, 'Received Date', header_format)
        col = col + 10
        if self.track_no:
            col += 1
            worksheet.write(raw, col, 'Tracking Number', header_format)
        if self.purpose:
            col += 1
            worksheet.write(raw, col, 'Purpose', header_format)
        if self.expected_date:
            col += 1
            worksheet.write(raw, col, 'Expected Date', header_format)
        if self.confirm_date:
            col += 1
            worksheet.write(raw, col, 'Confirmation Date', header_format)
        if self.desired_date:
            col += 1
            worksheet.write(raw, col, 'Desired Date', header_format)
        if self.days_to_maj_dis:
            col += 1
            worksheet.write(raw, col, 'Days to Major Disruption', header_format)
        if self.alt_ven_days_to_receive:
            col += 1
            worksheet.write(raw, col, 'Alternative Vendor Days to Receive', header_format)

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
        if report_type in ('all', 'unreceived'):
            if department_ids:
                domain = [('state', '!=', 'cancel'),
                          ('company_id', '=', self.company_id.id),
                          ('date_approve', '>=', start_date),
                          ('date_approve', '<=', end_date),
                          ('department_id', 'in', department_ids)]
            else:
                domain = [('state', '!=', 'cancel'),
                          ('company_id', '=', self.company_id.id),
                          ('date_approve', '>=', start_date),
                          ('date_approve', '<=', end_date)]
        if report_type == 'received':
            if department_ids:
                domain = [('state', 'in', ['purchase', 'done']),
                          ('company_id', '=', self.company_id.id),
                          ('date_approve', '>=', start_date),
                          ('date_approve', '<=', end_date),
                          ('department_id', 'in', department_ids)]
            else:
                domain = [('state', 'in', ['purchase', 'done']),
                          ('company_id', '=', self.company_id.id),
                          ('date_approve', '>=', start_date),
                          ('date_approve', '<=', end_date)]
        purchase_ids = purchase_order_obj.search(domain)
        if report_type in ('received', 'all'):
            received_po_ids = purchase_ids.order_line.filtered(
                lambda line: line.product_type in ('consu', 'product'))
        if report_type in ('unreceived', 'all'):
            unreceived_po_ids = purchase_ids.order_line.filtered(
                lambda line: line.product_type in ('consu', 'product'))
        if report_type in ('received', 'all'):
            if not received_po_ids:
                raise ValidationError(_('This is no data to print.'))
        if report_type in ('unreceived', 'all'):
            if not unreceived_po_ids:
                raise ValidationError(_('This is no data to print.'))
        if report_type in ('received', 'unreceived', 'all'):
            sku_count, total_value_received = 0.0, 0.0
            total_qty_received, total_ordered_qty = 0.0, 0.0
            po_received_list = []
            if report_type in ('received', 'all'):
                po_ids = received_po_ids
            if report_type == 'unreceived':
                po_ids = unreceived_po_ids
            if po_ids:
                for move in po_ids.order_id.picking_ids.move_ids_without_package:
                    if move.product_uom_qty == move.quantity_done and move.state in ['done'] \
                            and move.picking_id.state in ['done'] and \
                            move.picking_id.picking_type_code == 'incoming':
                        project = move.purchase_line_id.order_id.department_id.name
                        requestor = move.purchase_line_id.order_id.user_id.name
                        po = move.purchase_line_id.order_id.name
                        vendor = move.purchase_line_id.order_id.partner_id.name
                        sku = move.purchase_line_id.product_id.default_code
                        product = move.purchase_line_id.product_id.name
                        received_by = move.picking_id.create_uid.name
                        value_received = (move.purchase_line_id.price_unit * move.quantity_done)
                        qty_received = move.quantity_done
                        ordered_qty = move.product_uom_qty
                        if sku:
                            sku_count += len(move.purchase_line_id.product_id)
                        total_value_received += value_received
                        total_qty_received += qty_received
                        total_ordered_qty += ordered_qty
                        received_date = move.picking_id.date_done.strftime("%m-%d-%Y")
                        row = 0
                        worksheet.write(raw, row, project, content_text_format)
                        worksheet.write(raw, row + 1, requestor, content_text_format)
                        worksheet.write(raw, row + 2, vendor, content_text_format)
                        worksheet.write(raw, row + 3, po, content_text_format)
                        worksheet.write(raw, row + 4, sku, content_text_format)
                        worksheet.write(raw, row + 5, product, content_text_format)
                        worksheet.write(raw, row + 6, received_by, content_text_format)
                        worksheet.write(raw, row + 7, value_received, content_text_format)
                        worksheet.write(raw, row + 8, qty_received, content_text_format)
                        worksheet.write(raw, row + 9, ordered_qty, content_text_format)
                        worksheet.write(raw, row + 10, received_date, content_text_format)
                        row = row + 10
                        if self.track_no:
                            row += 1
                            tracking_no = move.purchase_line_id.order_id.tracking_number
                            worksheet.write(raw, row, tracking_no, content_text_format)
                        if self.purpose:
                            row += 1
                            purpose = move.purchase_line_id.order_id.purpose_type.name
                            worksheet.write(raw, row, purpose, content_text_format)
                        if self.expected_date:
                            row += 1
                            expected_date = move.purchase_line_id.order_id.expected_date.strftime(
                                "%m-%d-%Y")
                            worksheet.write(raw, row, expected_date, content_text_format)
                        if self.confirm_date:
                            row += 1
                            confirmation_date = move.purchase_line_id.order_id.expected_date. \
                                strftime("%m-%d-%Y")
                            worksheet.write(raw, row, confirmation_date, content_text_format)
                        if self.desired_date:
                            row += 1
                            desired_date = move.purchase_line_id.order_id.expected_date.strftime(
                                "%m-%d-%Y")
                            worksheet.write(raw, row, desired_date, content_text_format)
                        if self.days_to_maj_dis:
                            row += 1
                            days_to_major_disruption = move.purchase_line_id.order_id.days_disruption
                            worksheet.write(raw, row, days_to_major_disruption, content_text_format)
                        if self.alt_ven_days_to_receive:
                            row += 1
                            alt_vendor_days_to_receive = move.purchase_line_id.order_id.vendor_days_receive
                            worksheet.write(raw, row, alt_vendor_days_to_receive,
                                            content_text_format)
                        raw += 1
                        po_received_list.append(po)

                po_count = len(list(dict.fromkeys(po_received_list)))
                sku_count = sku_count
                merge_range = 'A' + str(raw + 3) + ':' + 'B' + str(raw + 3)
                worksheet.merge_range(merge_range, 'Total', total_title_format)
                worksheet.write(raw + 2, 3, po_count, total_content_format_integer)
                worksheet.write(raw + 2, 4, sku_count, total_content_format_integer)
                worksheet.write(raw + 2, 7, total_value_received, total_content_format_integer)
                worksheet.write(raw + 2, 8, total_qty_received, total_content_format_integer)
                worksheet.write(raw + 2, 9, total_ordered_qty, total_content_format_integer)
        if report_type == 'all':
            worksheet = workbook.add_worksheet('Product UnReceived')
            raw = 5
            col = 0
            worksheet.set_column(col, col + 16, 23)
            worksheet.set_default_row(23)
            worksheet.merge_range('A1:G1', unreceived_title_text, unreceived_title_format)
            worksheet.merge_range('A3:B3', 'Date', header_format)
            worksheet.merge_range('A4:B4', date_str, header_content_format)
            worksheet.write(raw, col, 'Project', header_format)
            worksheet.write(raw, col + 1, 'Requestor', header_format)
            worksheet.write(raw, col + 2, 'Vendor', header_format)
            worksheet.write(raw, col + 3, 'PO', header_format)
            worksheet.write(raw, col + 4, 'SKU', header_format)
            worksheet.write(raw, col + 5, 'Product', header_format)
            worksheet.write(raw, col + 6, 'Received By', header_format)
            worksheet.write(raw, col + 7, 'Value Received', header_format)
            worksheet.write(raw, col + 8, 'Quantity Received', header_format)
            worksheet.write(raw, col + 9, 'Total Ordered', header_format)
            worksheet.write(raw, col + 10, 'Scheduled Date', header_format)
            col = col + 10
            if self.track_no:
                col += 1
                worksheet.write(raw, col, 'Tracking Number', header_format)
            if self.purpose:
                col += 1
                worksheet.write(raw, col, 'Purpose', header_format)
            if self.expected_date:
                col += 1
                worksheet.write(raw, col, 'Expected Date', header_format)
            if self.confirm_date:
                col += 1
                worksheet.write(raw, col, 'Confirmation Date', header_format)
            if self.desired_date:
                col += 1
                worksheet.write(raw, col, 'Desired Date', header_format)
            if self.days_to_maj_dis:
                col += 1
                worksheet.write(raw, col, 'Days to Major Disruption', header_format)
            if self.alt_ven_days_to_receive:
                col += 1
                worksheet.write(raw, col, 'Alternative Vendor Days to Receive', header_format)
            raw += 1
            sku_count, total_value_received = 0.0, 0.0
            total_qty_received, total_ordered_qty = 0.0, 0.0
            po_unreceived_list = []
            for move in unreceived_po_ids.order_id.picking_ids.move_ids_without_package:
                if move.product_uom_qty != move.quantity_done and move.state not in ['done'] \
                        and move.picking_id.state not in ['done'] and \
                        move.picking_id.picking_type_code == 'incoming':
                    project = move.purchase_line_id.order_id.department_id.name
                    requestor = move.purchase_line_id.order_id.user_id.name
                    po = move.purchase_line_id.order_id.name
                    vendor = move.purchase_line_id.order_id.partner_id.name
                    sku = move.purchase_line_id.product_id.default_code
                    product = move.purchase_line_id.product_id.name
                    received_by = move.picking_id.create_uid.name
                    value_received = (move.purchase_line_id.price_unit * move.quantity_done)
                    qty_received = move.quantity_done
                    ordered_qty = move.product_uom_qty
                    if sku:
                        sku_count += len(move.purchase_line_id.product_id)
                    total_value_received += value_received
                    total_qty_received += qty_received
                    total_ordered_qty += ordered_qty
                    scheduled_date = move.picking_id.scheduled_date.strftime("%m-%d-%Y")
                    row = 0
                    worksheet.write(raw, row, project, content_text_format)
                    worksheet.write(raw, row + 1, requestor, content_text_format)
                    worksheet.write(raw, row + 2, vendor, content_text_format)
                    worksheet.write(raw, row + 3, po, content_text_format)
                    worksheet.write(raw, row + 4, sku, content_text_format)
                    worksheet.write(raw, row + 5, product, content_text_format)
                    worksheet.write(raw, row + 6, received_by, content_text_format)
                    worksheet.write(raw, row + 7, value_received, content_text_format)
                    worksheet.write(raw, row + 8, qty_received, content_text_format)
                    worksheet.write(raw, row + 9, ordered_qty, content_text_format)
                    worksheet.write(raw, row + 10, scheduled_date, content_text_format)
                    row = row + 10
                    if self.track_no:
                        row += 1
                        tracking_no = move.purchase_line_id.order_id.tracking_number
                        worksheet.write(raw, row, tracking_no, content_text_format)
                    if self.purpose:
                        row += 1
                        purpose = move.purchase_line_id.order_id.purpose_type.name
                        worksheet.write(raw, row, purpose, content_text_format)
                    if self.expected_date:
                        row += 1
                        expected_date = move.purchase_line_id.order_id.expected_date.strftime(
                            "%m-%d-%Y")
                        worksheet.write(raw, row, expected_date, content_text_format)
                    if self.confirm_date:
                        row += 1
                        confirmation_date = move.purchase_line_id.order_id.expected_date.strftime(
                            "%m-%d-%Y")
                        worksheet.write(raw, row, confirmation_date, content_text_format)
                    if self.desired_date:
                        row += 1
                        desired_date = move.purchase_line_id.order_id.expected_date.strftime(
                            "%m-%d-%Y")
                        worksheet.write(raw, row, desired_date, content_text_format)
                    if self.days_to_maj_dis:
                        row += 1
                        days_to_major_disruption = move.purchase_line_id.order_id.days_disruption
                        worksheet.write(raw, row, days_to_major_disruption, content_text_format)
                    if self.alt_ven_days_to_receive:
                        row += 1
                        alt_vendor_days_to_receive = move.purchase_line_id.order_id.vendor_days_receive
                        worksheet.write(raw, row, alt_vendor_days_to_receive, content_text_format)
                    raw += 1
                    po_unreceived_list.append(po)

            po_count = len(list(dict.fromkeys(po_unreceived_list)))
            sku_count = sku_count
            merge_range = 'A' + str(raw + 3) + ':' + 'B' + str(raw + 3)
            worksheet.merge_range(merge_range, 'Total', total_title_format)
            worksheet.write(raw + 2, 3, po_count, total_content_format_integer)
            worksheet.write(raw + 2, 4, sku_count, total_content_format_integer)
            worksheet.write(raw + 2, 7, total_value_received, total_content_format_integer)
            worksheet.write(raw + 2, 8, total_qty_received, total_content_format_integer)
            worksheet.write(raw + 2, 9, total_ordered_qty, total_content_format_integer)
        workbook.close()
        self.write(
            {'file_download': base64.b64encode(open('/tmp/' + xls_file_name, 'rb').read()),
             'name': xls_file_name, 'state': 'done'})
        return {'name': 'Purchase Custom Report',
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
        return {'name': 'Purchase Custom Report',
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'target': 'new'}
