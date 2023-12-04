# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

import binascii
import io
import logging
import tempfile
from datetime import datetime
from operator import itemgetter

import xlrd

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class WizardImportQualityCheck(models.TransientModel):
    _name = "wizard.import.quality.check"
    _description = 'Import Quality Check'

    file = fields.Binary(string="Select File", required=True)
    file_type = fields.Selection(
        [('xls', 'XLS File'), ('csv', 'CSV File')], string='Select', default='xls')
    filename = fields.Char(string="File Name")

    def update_qc_and_create_move_line(self, picking_id, values):
        flag = True
        quality_check_obj = self.env['quality.check']
        lot_obj = self.env['stock.production.lot']
        product_id = self.env['product.product'].browse(values.get('product_id'))
        company_id = self.env.user.company_id
        for move in picking_id.move_lines.filtered(
                lambda m: m.product_id.id == product_id.id and
                          m.product_uom_qty != m.quantity_done and
                          m.state not in ('done', 'cancel')):
            if not flag:
                continue
            lot_id = False

            # Find Quality Check
            quality_check_id = picking_id.check_ids.filtered(
                lambda qc: qc.product_id.id == product_id.id and
                           qc.purchase_line_id.id == move.purchase_line_id.id
                           and qc.quality_state == 'none' and not qc.lot_id)
            if values.get('serial_no', '') and product_id.tracking != 'none':
                lot_id = lot_obj.search(
                    [('product_id', '=', product_id.id),
                     ('company_id', '=', company_id.id),
                     ('name', '=', values.get('serial_no'))], limit=1)
                if not lot_id:
                    lot_id = lot_obj.create({'product_id': product_id.id,
                                             'company_id': company_id.id,
                                             'name': values.get('serial_no')})

            if quality_check_id:
                quality_check_id[0].update({
                    'quality_state': values.get('qc_status'),
                    'control_date': datetime.now(),
                    'lot_id': lot_id and lot_id.id or False,
                    'user_id': self.env.user,
                    'comments': values.get('comments')})
                if product_id.tracking == 'none' and (
                        move.quantity_done + values.get('qty')) != move.product_uom_qty:
                    quality_check_id[0].update({'qty': values.get('qty')})
                    if move.quantity_done:
                        done_qty = move.quantity_done + values.get('qty')
                    else:
                        done_qty = sum(picking_id.check_ids.filtered(
                            lambda check: check.quality_state != 'none'
                                          and check.product_id.id == product_id.id).mapped('qty'))
                    rem_qty = move.product_uom_qty - done_qty
                    copy_check_id = quality_check_id[0].copy()
                    copy_check_id.update({'qty': rem_qty, 'lot_id': False, 'comments': False})
                quality_check_obj |= quality_check_id

            # Create Move Line
            move.update(
                {'move_line_ids': [(0, 0, {
                    'lot_id': lot_id and lot_id.id or False,
                    'lot_name': lot_id and lot_id.name or False,
                    'qty_done': 1 if product_id.tracking not in ('lot', 'none') else values.get(
                        'qty'),
                    'product_id': product_id.id,
                    'product_uom_id': product_id.uom_id.id,
                    'location_id': move.location_id.id,
                    'location_dest_id': values.get('location_dest_id'),
                    'picking_id': picking_id.id})]})
            flag = False
        return quality_check_obj

    def check_values(self, rows_data, picking_id, product_ids):
        # Search Products
        if not rows_data.get('product_code'):
            raise UserError(_('Please define product SKU code in file.'))
        product_id = self.env['product.product'].search(
            [('default_code', '=', rows_data.get('product_code'))], limit=1)
        if not product_id:
            raise UserError(_('%s product is not found.') % rows_data.get('product_code'))
        if product_id.id not in product_ids:
            return {}

        # Search Destination Location
        if not rows_data.get('location_name'):
            raise UserError(_('Please define destination location in file.'))
        location_dest_id = self.env['stock.location'].search(
            [('complete_name', '=', rows_data.get('location_name'))], limit=1)
        if not location_dest_id:
            raise UserError(_('%s Location not found.') % rows_data.get('location_name'))

        warehouse_id = picking_id.location_dest_id.get_warehouse()
        location_dest_ids = warehouse_id.view_location_id.child_ids.filtered(
            lambda location: location.usage == 'internal')
        child_loc_ids = self.env['stock.location'].search(
            [('id', 'child_of', location_dest_ids.ids), ('usage', '=', 'internal')])
        if location_dest_id.id not in child_loc_ids.ids:
            raise UserError(_('Location must be belong from %s')
                            % picking_id.location_dest_id.complete_name)

        # Quality Check status
        if rows_data.get('qc_status').lower() == 'pass':
            qc_status = 'pass'
        elif rows_data.get('qc_status').lower() == 'fail':
            qc_status = 'fail'
        else:
            raise UserError(
                _('Set Quality Check status for %s product.') % product_id.display_name)

        # serial number
        serial_no = rows_data.get('serial_no', '')
        if not serial_no and product_id.tracking != 'none':
            raise UserError(_(
                'You need to supply a Lot/Serial number for product %s.'
            ) % product_id.display_name)

        if product_id.tracking in ('serial', 'lot_serial') and float(
                rows_data.get('qty')) > 1.00:
            raise UserError(_(
                'You need to pass only 1 quantity for unique serial product %s.'
            ) % product_id.display_name)

        if isinstance(serial_no, float):
            serial_no = str(int(serial_no))
        elif isinstance(serial_no, int):
            serial_no = str(serial_no)

        return {'product_id': product_id.id,
                'qty': float(rows_data.get('qty')),
                'qc_status': qc_status,
                'serial_no': serial_no,
                'location_dest_id': location_dest_id.id,
                'comments': rows_data.get('comments')}

    def group_by_products(self, files_data):
        data_dict = {}
        for data in filter(None, files_data):
            if not data.get('product_id') in data_dict:
                data_dict.update({data.get('product_id'): [data]})
            else:
                data_dict[data.get('product_id')].append(data)
        return data_dict

    def action_import_qc(self):
        context = dict(self.env.context) or {}
        picking_id = self.env['stock.picking'].browse(context.get('active_ids'))
        imported_qc = self.env['imported.qc']
        quality_checks_ids = self.env['quality.check']
        file_data = []
        prod_obj = self.env['product.product']
        lot_obj = self.env['stock.production.lot']
        quant_obj = self.env['stock.quant']
        company_id = self.env.user.company_id
        product_ids = picking_id.move_ids_without_package.mapped(
            'product_id').ids
        if self.file_type == 'xls':
            if self.filename.split(".")[-1] not in ('xls', 'xlsx'):
                raise Warning(_('Unsupported file format or corrupted file'))
            try:
                fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                fp.write(binascii.a2b_base64(self.file))
                fp.seek(0)
                workbook = xlrd.open_workbook(fp.name)
                worksheet = workbook.sheet_by_index(0)
                num_rows = worksheet.nrows - 1
                current_row = 0

                while current_row < num_rows:
                    current_row += 1
                    row = worksheet.row(current_row)
                    rows_data = {'product_code': row[1].value.strip(),
                                 'qty': float(row[2].value),
                                 'location_name': row[3].value.strip(),
                                 'qc_status': str(row[5].value).strip(),
                                 'serial_no': row[4] and row[4].value.strip(),
                                 'comments': row[6] and str(
                                     row[6].value).strip() or ''}
                    vals = self.check_values(rows_data, picking_id, product_ids)
                    file_data.append(vals)
            except Exception as e:
                raise Warning(_(e))

        elif self.file_type == 'csv':
            if not self.filename.lower().strip().endswith('.csv'):
                raise Warning(_('Unsupported file format or corrupted file'))

            keys = ['product_name', 'product_code', 'qty', 'location_name',
                    'serial_no', 'qc_status', 'comments']
            try:
                csv_data = base64.b64decode(self.file)
                data_file = io.StringIO(csv_data.decode("utf-8"))
                data_file.seek(0)
                file_reader = []
                csv_reader = csv.reader(data_file, delimiter=',')
                file_reader.extend(csv_reader)
                for row in range(len(file_reader)):
                    field = list(map(str, file_reader[row]))
                    value = dict(zip(keys, field))
                    if row > 0:
                        vals = self.check_values(
                            value, picking_id, product_ids)
                        file_data.append(vals)
            except Exception as e:
                raise Warning(_(e))

        # Group By Product
        data_dict = self.group_by_products(file_data)

        try:
            for key, value in data_dict.items():
                product_id = prod_obj.browse(key)
                move_ids = picking_id.move_ids_without_package.filtered(
                    lambda mv: mv.product_id.id == product_id.id)
                ordered_qty = sum(move_ids.mapped('product_uom_qty'))
                total_qty = sum(map(itemgetter('qty'), value))
                if product_id.tracking == 'none' and total_qty > ordered_qty:
                    raise UserError(_(
                        'You can not define more than ordered quantity for no tracking product %s.'
                    ) % product_id.display_name)
                if product_id.tracking == 'lot' and total_qty != ordered_qty:
                    raise UserError(_(
                        'Quantity should be same as ordered quantity for Lot product %s.'
                    ) % product_id.display_name)
                serial_no_lst = []
                for vals in value:
                    if product_id.tracking in (
                            'serial', 'lot_serial') and vals.get('serial_no'):
                        if vals['serial_no'] not in serial_no_lst:
                            serial_no_lst.append(vals['serial_no'])
                        else:
                            raise UserError(_(
                                'You can not choose two same serial number %s.'
                            ) % product_id.display_name)
                        lot_id = lot_obj.search(
                            [('product_id', '=', product_id.id),
                             ('company_id', '=', company_id.id),
                             ('name', '=', vals['serial_no'])], limit=1)
                        if lot_id:
                            quant_domain = [('product_id', '=', product_id.id),
                                            ('company_id', '=', company_id.id),
                                            ('location_id', '=', vals.get('location_dest_id')),
                                            ('lot_id', '=', lot_id.id)]
                            quant_count = quant_obj.search_count(quant_domain)
                            if quant_count:
                                raise UserError(_(
                                    'The combination of serial number and %s product must be unique'
                                    ' across a stock location!.') % (product_id.display_name))

                    res = self.update_qc_and_create_move_line(picking_id, vals)
                    quality_checks_ids |= res
        except Exception as e:
            raise Warning(_(e))

        product_lst = quality_checks_ids.mapped('product_id').mapped('name')
        product_lst = list(dict.fromkeys(product_lst))
        imported_qc.create({
            'total_imported_qc': len(product_lst),
            'imported_products': product_lst,
            'is_imported': True if len(product_lst) > 0 else False, })

        return {'name': _('Quality Checks'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'imported.qc',
                'view_id': self.env.ref('receipt_qc_import.imported_qc_wizard_view').id,
                'type': 'ir.actions.act_window',
                'target': 'new'}


class ImportedQC(models.TransientModel):
    _name = "imported.qc"
    _description = 'Imported Quality Check Wizard'

    total_imported_qc = fields.Integer(string="Total Imported QC")
    imported_products = fields.Text()
    is_imported = fields.Boolean(string="Is QC Imported")

    @api.model
    def default_get(self, fields):
        res = super(ImportedQC, self).default_get(fields)
        imported_qc_id = self.env['imported.qc'].sudo().search(
            [], order="id desc", limit=1)
        if imported_qc_id:
            res.update({'total_imported_qc': imported_qc_id.total_imported_qc,
                        'imported_products': imported_qc_id.imported_products,
                        'is_imported': imported_qc_id.is_imported})
        return res
