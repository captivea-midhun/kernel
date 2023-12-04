
import xlsxwriter
import base64
import datetime

from odoo import models, fields, api

class PurchaseTransactionReport(models.TransientModel):
    
    _name = "purchase.transaction.report"
    
    name = fields.Char(string='File Name')
    file_download = fields.Binary('File to Download')
    start_date = fields.Date(string='Start Date', default=datetime.datetime.strptime('01/07/2021', "%d/%m/%Y"))
    end_date = fields.Date(string='End Date')
    product_type = fields.Selection([
       ('product','Inventory Product'),
       ('consu', 'Consumable'),
       ('service', 'Service')], 
       string='Product Type',
       )
    state = fields.Selection([('init', 'init'),
                              ('done', 'done')], string='Status', readonly=True, default='init')

    def create_purchase_trans_report(self):
        xls_file_name = 'Purchase Transaction Report.xlsx'
        workbook = xlsxwriter.Workbook('/tmp/' + xls_file_name)
        worksheet = workbook.add_worksheet('Detailed Transactions')
        header_format = workbook.add_format({'bold': True,
                                             'align': 'center',
                                             'valign': 'vcenter',
                                             'font_size': 12,
                                             'border': 1,
                                             })
        content_text_format = workbook.add_format({'align': 'left',
                                                   'valign': 'vcenter',
                                                   'font_size': 12, 'border': 1,
                                                   })
        blank_content_text_format = workbook.add_format({'align': 'left',
                                                   'valign': 'vcenter',
                                                   'font_size': 12, 'border': 0,
                                                   })
        total_title_format = workbook.add_format({'bold': True,
                                                  'align': 'center',
                                                  'valign': 'vcenter',
                                                  'font_size': 12,
                                                  'border': 1,
                                                  })
        total_content_format_integer = workbook.add_format({'bold': True,
                                                            'align': 'right',
                                                            'valign': 'vcenter',
                                                            'font_size': 12,
                                                            'border': 1,
                                                            })
        money = workbook.add_format({'num_format':'$#,##0.00','border': 1})
        total_content_format_integer.set_num_format('$#,##0.00')
        worksheet.write(0, 0, 'Date Range', header_format)
        worksheet.write(2, 0, 'Start Date', header_format)
        worksheet.write(2, 1, 'End Date', header_format)
        worksheet.write(3, 0, str(self.start_date), content_text_format)
        worksheet.write(3, 1, str(self.end_date), content_text_format)
        row = 5
        col = 0
        worksheet.write(row, col, 'PO Number', header_format)
        worksheet.write(row, col + 1, 'PO Date', header_format)
        worksheet.write(row, col + 2, 'Subcontracted', header_format)
        worksheet.write(row, col + 3, 'Transfer Reference', header_format)
        worksheet.write(row, col + 4, 'Received Date', header_format)
        worksheet.write(row, col + 5, 'Vendor Bill', header_format)
        worksheet.write(row, col + 6, 'Accounting Date', header_format)
        worksheet.write(row, col + 7, 'Billed Date', header_format)
        worksheet.write(row, col + 8, 'Product', header_format)
        worksheet.write(row, col + 9, 'Product Type', header_format)
        worksheet.write(row, col + 10, 'Product Category', header_format)
        worksheet.write(row, col + 11, 'Quantity Ordered', header_format)
        worksheet.write(row, col + 12, 'Quantity Received', header_format)
        worksheet.write(row, col + 13, 'Quantity Billed', header_format)
        worksheet.write(row, col + 14, 'Unit Price', header_format)
        worksheet.write(row, col + 15, 'Price Total Received', header_format)
        worksheet.write(row, col + 16, 'Price Total Billed', header_format)
        worksheet.write(row, col + 17, 'Difference', header_format)
        row +=1
        po_ids = self.env['purchase.order'].search([('state','=','purchase'),('date_approve','>=',self.start_date),('date_approve','<=',self.end_date)])
        vendor_bill_ids = self.env['account.move'].search([('type','in',['in_invoice','in_refund']),('invoice_date','>=',self.start_date),('invoice_date','<=',self.end_date)])
        vendor_bill_po_list = []
        stock_move_po_list = []
        for bill in vendor_bill_ids:
            if bill.invoice_origin:
                po_id = self.env['purchase.order'].search([('name','=',bill.invoice_origin), ('hide_po','=',False)])
                vendor_bill_po_list.append(po_id)
        stock_move_ids = self.env['stock.move'].search([('picking_code','in',['incoming','outgoing']),('picking_id.date_done','>=',self.start_date),('picking_id.date_done','<=',self.end_date)])
        for move in stock_move_ids:
            if move.origin:
                po_id = self.env['purchase.order'].search([('name','=',move.origin), ('hide_po','=',False)])
                stock_move_po_list.append(po_id)
        vendor_bill_po_list = list(set(vendor_bill_po_list))
        stock_move_po_list = list(set(stock_move_po_list))
        po_final_list = vendor_bill_po_list + stock_move_po_list
        po_final_list = list(set(po_final_list))
        price_total_receive, price_total_bill = 0.0, 0.0
        for po in po_final_list:
            if self.product_type:
                po_order_lines = po.order_line.filtered(lambda ol: ol.product_id.type == self.product_type)
                for order_line in po_order_lines:
                    for mv in order_line.move_ids.filtered(lambda mv: mv.product_id.id == order_line.product_id.id and mv.state == 'done'):
                        if mv.picking_id.date_done.date() >= self.start_date and mv.picking_id.date_done.date() <= self.end_date:
                            worksheet.write(row, col, po.name, content_text_format)
                            worksheet.write(row, col + 1, str(po.date_approve), content_text_format)
                            worksheet.write(row, col + 2, "Yes" if po.bista_subcontracted_ids else "No", content_text_format)
                            worksheet.write(row, col + 3, mv.reference , content_text_format)
                            worksheet.write(row, col + 4, str(mv.picking_id.date_done), content_text_format)
                            worksheet.write(row, col + 5, None, content_text_format)
                            worksheet.write(row, col + 6, None, content_text_format)
                            worksheet.write(row, col + 7, None, content_text_format)
                            worksheet.write(row, col + 8, '[' + str(order_line.product_id.default_code) +'] ' + order_line.product_id.name, content_text_format)
                            worksheet.write(row, col + 9, order_line.product_type, content_text_format)
                            worksheet.write(row, col + 10, order_line.product_id.categ_id.name, content_text_format)
                            worksheet.write(row, col + 11, order_line.product_qty, content_text_format)
                            worksheet.write(row, col + 12, mv.quantity_done, content_text_format)
                            worksheet.write(row, col + 13, float(0.0), content_text_format)
                            worksheet.write(row, col + 14, order_line.price_unit, money)
                            price_total_received = 0.0
                            if mv.picking_code == 'incoming':
                                price_total_received = mv.quantity_done * order_line.price_unit
                            elif mv.picking_code == 'outgoing':
                                price_total_received = -(mv.quantity_done * order_line.price_unit)
                                worksheet.write(row, col + 12, -(mv.quantity_done), content_text_format)
                            worksheet.write(row, col + 15, price_total_received, money)
                            worksheet.write(row, col + 16, float(0.0), money)
                            worksheet.write(row, col + 17, price_total_received - float(0.0), money)
                            row +=1
                    
                    for inv in order_line.invoice_lines.filtered(lambda invl: invl.product_id.id == order_line.product_id.id and invl.move_id.state == 'posted'):
                        if inv.move_id.date >= self.start_date and inv.move_id.date <= self.end_date:
                            worksheet.write(row, col, po.name, content_text_format)
                            worksheet.write(row, col + 1, str(po.date_approve), content_text_format)
                            worksheet.write(row, col + 2, "Yes" if po.bista_subcontracted_ids else "No", content_text_format)
                            worksheet.write(row, col + 3, None, content_text_format)
                            worksheet.write(row, col + 4, None, content_text_format)
                            worksheet.write(row, col + 5, inv.move_id.name, content_text_format)
                            worksheet.write(row, col + 6, str(inv.move_id.date), content_text_format)
                            worksheet.write(row, col + 7, str(inv.move_id.invoice_date), content_text_format)
                            worksheet.write(row, col + 8, '[' + str(order_line.product_id.default_code) +'] ' + order_line.product_id.name, content_text_format)
                            worksheet.write(row, col + 9, order_line.product_type, content_text_format)
                            worksheet.write(row, col + 10, order_line.product_id.categ_id.name, content_text_format)
                            worksheet.write(row, col + 11, order_line.product_qty, content_text_format)
                            worksheet.write(row, col + 12, float(0.0), content_text_format)
                            worksheet.write(row, col + 13, inv.quantity, content_text_format)
                            worksheet.write(row, col + 14, order_line.price_unit, money)
                            worksheet.write(row, col + 15, float(0.0), money)
                            price_total_billed = 0.0
                            if inv.move_id.type == 'in_invoice':
                                price_total_billed = inv.quantity * order_line.price_unit
                            elif inv.move_id.type == 'in_refund':
                                price_total_billed = -(inv.quantity * order_line.price_unit)
                                worksheet.write(row, col + 13, -(inv.quantity), content_text_format)
                            worksheet.write(row, col + 16, price_total_billed, money)
                            worksheet.write(row, col + 17, float(0.0) - (price_total_billed), money)
                            row +=1
                    price_total_receive += (order_line.qty_received * order_line.price_unit)
                    price_total_bill += (order_line.qty_invoiced * order_line.price_unit)
            elif not self.product_type:
                po_order_lines = po.order_line
                for order_line in po_order_lines:
                    for mv in order_line.move_ids.filtered(lambda mv: mv.product_id.id == order_line.product_id.id and mv.state == 'done'):
                        if mv.picking_id.date_done.date() >= self.start_date and mv.picking_id.date_done.date() <= self.end_date:
                            worksheet.write(row, col, po.name, content_text_format)
                            worksheet.write(row, col + 1, str(po.date_approve), content_text_format)
                            worksheet.write(row, col + 2, "Yes" if po.bista_subcontracted_ids else "No", content_text_format)
                            worksheet.write(row, col + 3, mv.reference , content_text_format)
                            worksheet.write(row, col + 4, str(mv.picking_id.date_done), content_text_format)
                            worksheet.write(row, col + 5, None, content_text_format)
                            worksheet.write(row, col + 6, None, content_text_format)
                            worksheet.write(row, col + 7, None, content_text_format)
                            worksheet.write(row, col + 8, '[' + str(order_line.product_id.default_code) +'] ' + order_line.product_id.name, content_text_format)
                            worksheet.write(row, col + 9, order_line.product_type, content_text_format)
                            worksheet.write(row, col + 10, order_line.product_id.categ_id.name, content_text_format)
                            worksheet.write(row, col + 11, order_line.product_qty, content_text_format)
                            worksheet.write(row, col + 12, mv.quantity_done, content_text_format)
                            worksheet.write(row, col + 13, float(0.0), content_text_format)
                            worksheet.write(row, col + 14, order_line.price_unit, money)
                            price_total_received = 0.0
                            if mv.picking_code == 'incoming':
                                price_total_received = mv.quantity_done * order_line.price_unit
                            elif mv.picking_code == 'outgoing':
                                price_total_received = -(mv.quantity_done * order_line.price_unit)
                                worksheet.write(row, col + 12, -(mv.quantity_done), content_text_format)
                            worksheet.write(row, col + 15, price_total_received, money)
                            worksheet.write(row, col + 16, float(0.0), money)
                            worksheet.write(row, col + 17, price_total_received - float(0.0), money)
                            row +=1
                    
                    for inv in order_line.invoice_lines.filtered(lambda invl: invl.product_id.id == order_line.product_id.id and invl.move_id.state == 'posted'):
                        if inv.move_id.date >= self.start_date and inv.move_id.date <= self.end_date:
                            worksheet.write(row, col, po.name, content_text_format)
                            worksheet.write(row, col + 1, str(po.date_approve), content_text_format)
                            worksheet.write(row, col + 2, "Yes" if po.bista_subcontracted_ids else "No", content_text_format)
                            worksheet.write(row, col + 3, None, content_text_format)
                            worksheet.write(row, col + 4, None, content_text_format)
                            worksheet.write(row, col + 5, inv.move_id.name, content_text_format)
                            worksheet.write(row, col + 6, str(inv.move_id.date), content_text_format)
                            worksheet.write(row, col + 7, str(inv.move_id.invoice_date), content_text_format)
                            worksheet.write(row, col + 8, '[' + str(order_line.product_id.default_code) +'] ' + order_line.product_id.name, content_text_format)
                            worksheet.write(row, col + 9, order_line.product_type, content_text_format)
                            worksheet.write(row, col + 10, order_line.product_id.categ_id.name, content_text_format)
                            worksheet.write(row, col + 11, order_line.product_qty, content_text_format)
                            worksheet.write(row, col + 12, float(0.0), content_text_format)
                            worksheet.write(row, col + 13, inv.quantity, content_text_format)
                            worksheet.write(row, col + 14, order_line.price_unit, money)
                            worksheet.write(row, col + 15, float(0.0), money)
                            price_total_billed = 0
                            if inv.move_id.type == 'in_invoice':
                                price_total_billed = inv.quantity * order_line.price_unit
                            elif inv.move_id.type == 'in_refund':
                                price_total_billed = -(inv.quantity * order_line.price_unit)
                                worksheet.write(row, col + 13, -(inv.quantity), content_text_format)
                            worksheet.write(row, col + 16, price_total_billed, money)
                            worksheet.write(row, col + 17, float(0.0) - (price_total_billed), money)
                            row +=1
                    price_total_receive += (order_line.qty_received * order_line.price_unit)
                    price_total_bill += (order_line.qty_invoiced * order_line.price_unit)
        worksheet.write(row + 1, col + 11, 'Grand Total', total_title_format)
        price_total_receive = '=SUM(O7:O'+ str(row) + ')'
        worksheet.write(row + 1, 14, price_total_receive, total_content_format_integer)
        price_total_bill = '=SUM(P7:P'+ str(row) + ')'
        worksheet.write(row + 1, 15, price_total_bill, total_content_format_integer)
        final_total_difference = '=SUM(Q7:Q'+ str(row) + ')'
        worksheet.write(row + 1, 16, final_total_difference, total_content_format_integer)
        worksheet.set_column(col, col + 16, 23)
        worksheet.set_default_row(23)

        # summary sheet
        summary_worksheet = workbook.add_worksheet("Summary")
        summary_worksheet.write(0, 0, 'Date Range', header_format)
        summary_worksheet.write(2, 0, 'Start Date', header_format)
        summary_worksheet.write(2, 1, 'End Date', header_format)
        summary_worksheet.write(3, 0, str(self.start_date), content_text_format)
        summary_worksheet.write(3, 1, str(self.end_date), content_text_format)

        row = 5
        col = 0
        summary_worksheet.write(row, col, 'PO Number', header_format)
        summary_worksheet.write(row, col + 1, 'PO Date', header_format)
        summary_worksheet.write(row, col + 2, 'Total Quantity Received', header_format)
        summary_worksheet.write(row, col + 3, 'Total Quantity Billed', header_format)
        summary_worksheet.write(row, col + 4, 'Price Total Received', header_format)
        summary_worksheet.write(row, col + 5, 'Price Total Billed', header_format)
        summary_worksheet.write(row, col + 6, 'Total Difference ', header_format)
        row +=1
        po_order = self.env['purchase.order']
        for po in po_final_list:
            po_order |= po
        print ("po_order --->>", po_order)
        po_order = po_order.sorted(key=lambda l: l.name)
        po_final_list = po_order
        for po in po_final_list.filtered(lambda po: not po.bista_subcontracted_ids):
            if self.product_type:
                summary_worksheet.write(row, col, po.name, content_text_format)
                summary_worksheet.write(row, col + 1, str(po.date_approve), content_text_format)
                po_order_lines = po.order_line.filtered(lambda ol: ol.product_id.type == self.product_type)
                total_qty_received, total_qty_billed = 0.0, 0.0
                price_total_received, price_total_billed = 0.0, 0.0
                total_difference = 0.0
                for order_line in po_order_lines:
                    for mv in order_line.move_ids.filtered(lambda mv: mv.product_id.id == order_line.product_id.id and mv.state == 'done' and mv.product_id.categ_id.name == "Production Parts"):
                        if mv.picking_id.date_done.date() >= self.start_date and mv.picking_id.date_done.date() <= self.end_date:
                            total_qty_received += mv.quantity_done
                            if mv.picking_code == 'incoming':
                                price_total_received += mv.quantity_done * order_line.price_unit
                            elif mv.picking_code == 'outgoing':
                                price_total_received += -(mv.quantity_done * order_line.price_unit)
                    
                    for inv in order_line.invoice_lines.filtered(lambda invl: invl.product_id.id == order_line.product_id.id and invl.move_id.state == 'posted' and invl.product_id.categ_id.name == "Production Parts"):
                        if inv.move_id.date >= self.start_date and inv.move_id.date <= self.end_date:
                            total_qty_billed += inv.quantity
                            if inv.move_id.type == 'in_invoice':
                                price_total_billed += inv.quantity * order_line.price_unit
                            elif inv.move_id.type == 'in_refund':
                                price_total_billed += -(inv.quantity * order_line.price_unit)
                summary_worksheet.write(row, col + 2, total_qty_received, content_text_format)
                summary_worksheet.write(row, col + 3, total_qty_billed, content_text_format)
                summary_worksheet.write(row, col + 4, price_total_received, money)
                summary_worksheet.write(row, col + 5, price_total_billed, money)
                total_difference = price_total_received - price_total_billed
                summary_worksheet.write(row, col + 6, total_difference, money)
                if total_difference == 0 or 0.0:
                    summary_worksheet.write(row, col, None, blank_content_text_format)
                    summary_worksheet.write(row, col + 1, None, blank_content_text_format)
                    summary_worksheet.write(row, col + 2, None, blank_content_text_format)
                    summary_worksheet.write(row, col + 3, None, blank_content_text_format)
                    summary_worksheet.write(row, col + 4, None, blank_content_text_format)
                    summary_worksheet.write(row, col + 5, None, blank_content_text_format)
                    summary_worksheet.write(row, col + 6, None, blank_content_text_format)
                    row -=1
                row +=1
            elif not self.product_type:
                summary_worksheet.write(row, col, po.name, content_text_format)
                summary_worksheet.write(row, col + 1, str(po.date_approve), content_text_format)
                po_order_lines = po.order_line
                total_qty_received, total_qty_billed = 0.0, 0.0
                price_total_received, price_total_billed = 0.0, 0.0
                for order_line in po_order_lines:
                    for mv in order_line.move_ids.filtered(lambda mv: mv.product_id.id == order_line.product_id.id and mv.state == 'done' and mv.product_id.categ_id.name == "Production Parts"):
                        if mv.picking_id.date_done.date() >= self.start_date and mv.picking_id.date_done.date() <= self.end_date:
                            total_qty_received += mv.quantity_done
                            if mv.picking_code == 'incoming':
                                price_total_received += mv.quantity_done * order_line.price_unit
                            elif mv.picking_code == 'outgoing':
                                price_total_received += -(mv.quantity_done * order_line.price_unit)
                    
                    for inv in order_line.invoice_lines.filtered(lambda invl: invl.product_id.id == order_line.product_id.id and invl.move_id.state == 'posted' and invl.product_id.categ_id.name == "Production Parts"):
                        if inv.move_id.date >= self.start_date and inv.move_id.date <= self.end_date:
                            total_qty_billed += inv.quantity
                            if inv.move_id.type == 'in_invoice':
                                price_total_billed += inv.quantity * order_line.price_unit
                            elif inv.move_id.type == 'in_refund':
                                price_total_billed += -(inv.quantity * order_line.price_unit)
                summary_worksheet.write(row, col + 2, total_qty_received, content_text_format)
                summary_worksheet.write(row, col + 3, total_qty_billed, content_text_format)
                summary_worksheet.write(row, col + 4, price_total_received, money)
                summary_worksheet.write(row, col + 5, price_total_billed, money)
                total_difference = price_total_received - price_total_billed
                summary_worksheet.write(row, col + 6, total_difference, money)
                if total_difference == 0 or 0.0:
                    summary_worksheet.write(row, col, None, blank_content_text_format)
                    summary_worksheet.write(row, col + 1, None, blank_content_text_format)
                    summary_worksheet.write(row, col + 2, None, blank_content_text_format)
                    summary_worksheet.write(row, col + 3, None, blank_content_text_format)
                    summary_worksheet.write(row, col + 4, None, blank_content_text_format)
                    summary_worksheet.write(row, col + 5, None, blank_content_text_format)
                    summary_worksheet.write(row, col + 6, None, blank_content_text_format)
                    row -=1
                row +=1
        summary_worksheet.write(row + 1, col + 2, 'Grand Total', total_title_format)
        sum_price_total_receive = '=SUM(E7:E'+ str(row) + ')'
        summary_worksheet.write_formula(row + 1, 4, sum_price_total_receive, total_content_format_integer)
        sum_price_total_bill = '=SUM(F7:F'+ str(row) + ')'
        summary_worksheet.write(row + 1, 5, sum_price_total_bill, total_content_format_integer)
        final_total_difference = '=SUM(G7:G'+ str(row) + ')'
        summary_worksheet.write(row + 1, 6, final_total_difference, total_content_format_integer)
        summary_worksheet.set_column(col, col + 16, 23)
        summary_worksheet.set_default_row(23)
        
        
        # Summary - Subcontracting
        summary_subcontract_worksheet = workbook.add_worksheet("Summary - Subcontracting")
        summary_subcontract_worksheet.write(0, 0, 'Date Range', header_format)
        summary_subcontract_worksheet.write(2, 0, 'Start Date', header_format)
        summary_subcontract_worksheet.write(2, 1, 'End Date', header_format)
        summary_subcontract_worksheet.write(3, 0, str(self.start_date), content_text_format)
        summary_subcontract_worksheet.write(3, 1, str(self.end_date), content_text_format)
        
        row = 5
        col = 0
        summary_subcontract_worksheet.write(row, col, 'PO Number', header_format)
        summary_subcontract_worksheet.write(row, col + 1, 'PO Date', header_format)
        summary_subcontract_worksheet.write(row, col + 2, 'Total Quantity Received', header_format)
        summary_subcontract_worksheet.write(row, col + 3, 'Total Quantity Billed', header_format)
        summary_subcontract_worksheet.write(row, col + 4, 'Price Total Received', header_format)
        summary_subcontract_worksheet.write(row, col + 5, 'Price Total Billed', header_format)
        summary_subcontract_worksheet.write(row, col + 6, 'Total Difference ', header_format)
        row +=1
        po_order = self.env['purchase.order']
        for po in po_final_list:
            po_order |= po
        print ("po_order --->>", po_order)
        po_order = po_order.sorted(key=lambda l: l.name)
        po_final_list = po_order
        for po in po_final_list.filtered(lambda po: po.bista_subcontracted_ids):
            if self.product_type:
                summary_subcontract_worksheet.write(row, col, po.name, content_text_format)
                summary_subcontract_worksheet.write(row, col + 1, str(po.date_approve), content_text_format)
                po_order_lines = po.order_line.filtered(lambda ol: ol.product_id.type == self.product_type)
                total_qty_received, total_qty_billed = 0.0, 0.0
                price_total_received, price_total_billed = 0.0, 0.0
                total_difference = 0.0
                for order_line in po_order_lines:
                    for mv in order_line.move_ids.filtered(lambda mv: mv.product_id.id == order_line.product_id.id and mv.state == 'done' and mv.product_id.categ_id.name == "Production Parts"):
                        if mv.picking_id.date_done.date() >= self.start_date and mv.picking_id.date_done.date() <= self.end_date:
                            total_qty_received += mv.quantity_done
                            if mv.picking_code == 'incoming':
                                price_total_received += mv.quantity_done * order_line.price_unit
                            elif mv.picking_code == 'outgoing':
                                price_total_received += -(mv.quantity_done * order_line.price_unit)
                    
                    for inv in order_line.invoice_lines.filtered(lambda invl: invl.product_id.id == order_line.product_id.id and invl.move_id.state == 'posted' and invl.product_id.categ_id.name == "Production Parts"):
                        if inv.move_id.date >= self.start_date and inv.move_id.date <= self.end_date:
                            total_qty_billed += inv.quantity
                            if inv.move_id.type == 'in_invoice':
                                price_total_billed += inv.quantity * order_line.price_unit
                            elif inv.move_id.type == 'in_refund':
                                price_total_billed += -(inv.quantity * order_line.price_unit)
                summary_subcontract_worksheet.write(row, col + 2, total_qty_received, content_text_format)
                summary_subcontract_worksheet.write(row, col + 3, total_qty_billed, content_text_format)
                summary_subcontract_worksheet.write(row, col + 4, price_total_received, money)
                summary_subcontract_worksheet.write(row, col + 5, price_total_billed, money)
                total_difference = price_total_received - price_total_billed
                summary_subcontract_worksheet.write(row, col + 6, total_difference, money)
                if total_difference == 0 or 0.0:
                    summary_subcontract_worksheet.write(row, col, None, blank_content_text_format)
                    summary_subcontract_worksheet.write(row, col + 1, None, blank_content_text_format)
                    summary_subcontract_worksheet.write(row, col + 2, None, blank_content_text_format)
                    summary_subcontract_worksheet.write(row, col + 3, None, blank_content_text_format)
                    summary_subcontract_worksheet.write(row, col + 4, None, blank_content_text_format)
                    summary_subcontract_worksheet.write(row, col + 5, None, blank_content_text_format)
                    summary_subcontract_worksheet.write(row, col + 6, None, blank_content_text_format)
                    row -=1
                row +=1
            elif not self.product_type:
                summary_subcontract_worksheet.write(row, col, po.name, content_text_format)
                summary_subcontract_worksheet.write(row, col + 1, str(po.date_approve), content_text_format)
                po_order_lines = po.order_line
                total_qty_received, total_qty_billed = 0.0, 0.0
                price_total_received, price_total_billed = 0.0, 0.0
                for order_line in po_order_lines:
                    for mv in order_line.move_ids.filtered(lambda mv: mv.product_id.id == order_line.product_id.id and mv.state == 'done' and mv.product_id.categ_id.name == "Production Parts"):
                        if mv.picking_id.date_done.date() >= self.start_date and mv.picking_id.date_done.date() <= self.end_date:
                            total_qty_received += mv.quantity_done
                            if mv.picking_code == 'incoming':
                                price_total_received += mv.quantity_done * order_line.price_unit
                            elif mv.picking_code == 'outgoing':
                                price_total_received += -(mv.quantity_done * order_line.price_unit)
                    
                    for inv in order_line.invoice_lines.filtered(lambda invl: invl.product_id.id == order_line.product_id.id and invl.move_id.state == 'posted' and invl.product_id.categ_id.name == "Production Parts"):
                        if inv.move_id.date >= self.start_date and inv.move_id.date <= self.end_date:
                            total_qty_billed += inv.quantity
                            if inv.move_id.type == 'in_invoice':
                                price_total_billed += inv.quantity * order_line.price_unit
                            elif inv.move_id.type == 'in_refund':
                                price_total_billed += -(inv.quantity * order_line.price_unit)
                summary_subcontract_worksheet.write(row, col + 2, total_qty_received, content_text_format)
                summary_subcontract_worksheet.write(row, col + 3, total_qty_billed, content_text_format)
                summary_subcontract_worksheet.write(row, col + 4, price_total_received, money)
                summary_subcontract_worksheet.write(row, col + 5, price_total_billed, money)
                total_difference = price_total_received - price_total_billed
                summary_subcontract_worksheet.write(row, col + 6, total_difference, money)
                if total_difference == 0 or 0.0:
                    summary_subcontract_worksheet.write(row, col, None, blank_content_text_format)
                    summary_subcontract_worksheet.write(row, col + 1, None, blank_content_text_format)
                    summary_subcontract_worksheet.write(row, col + 2, None, blank_content_text_format)
                    summary_subcontract_worksheet.write(row, col + 3, None, blank_content_text_format)
                    summary_subcontract_worksheet.write(row, col + 4, None, blank_content_text_format)
                    summary_subcontract_worksheet.write(row, col + 5, None, blank_content_text_format)
                    summary_subcontract_worksheet.write(row, col + 6, None, blank_content_text_format)
                    row -=1
                row +=1
        summary_subcontract_worksheet.write(row + 1, col + 2, 'Grand Total', total_title_format)
        sum_price_total_receive = '=SUM(E7:E'+ str(row) + ')'
        summary_subcontract_worksheet.write_formula(row + 1, 4, sum_price_total_receive, total_content_format_integer)
        sum_price_total_bill = '=SUM(F7:F'+ str(row) + ')'
        summary_subcontract_worksheet.write(row + 1, 5, sum_price_total_bill, total_content_format_integer)
        final_total_difference = '=SUM(G7:G'+ str(row) + ')'
        summary_subcontract_worksheet.write(row + 1, 6, final_total_difference, total_content_format_integer)
        summary_subcontract_worksheet.set_column(col, col + 16, 23)
        summary_subcontract_worksheet.set_default_row(23)
        
        workbook.worksheets_objs.sort(key = lambda x: x.name, reverse=True)
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
        self.state = 'init'
        return {'name': 'Purchase Custom Report',
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'target': 'new'}



        