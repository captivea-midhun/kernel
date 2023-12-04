# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

import binascii
import logging
import tempfile

import xlrd

from odoo import models, fields, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class MrpSerialImport(models.TransientModel):
    _name = 'mrp.serial.import'
    _description = 'Import Serial'

    product_file = fields.Binary(string='Product File')
    product_filename = fields.Char(string="Product File Name")

    def action_import(self):
        context = dict(self.env.context) or {}
        production_id = self.env['mrp.production'].browse(
            context.get('active_ids'))
        bom_dict = {}
        for comp in production_id.bom_id.bom_line_ids:
            if comp.slot:
                bom_dict.update({comp.product_id.id: comp.slot})
        lot_obj = self.env['stock.production.lot']
        company_id = self.env.user.company_id
        component_product_lst = []
        [component_product_lst.append(comp_rec.product_id.id)
         for comp_rec in production_id.move_raw_ids]
        assert len(
            self) == 1, 'This option should only be used for a single id at a time.'
        file_data = []

        if self.product_file:
            fp = tempfile.NamedTemporaryFile(delete=False,
                                             suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.product_file))
            fp.seek(0)
            workbook = xlrd.open_workbook(fp.name)
            worksheet = workbook.sheet_by_index(0)
            num_rows = worksheet.nrows - 1
            current_row = 0
            finished_serial_no_dict = {}
            component_dict = {}
            f_lot_sr_no_list = []
            if production_id and production_id.unreserve_visible:
                production_id.button_unreserve()
            while current_row < num_rows:
                serialized_qty = 0.0
                non_serialized_qty = 0.0
                quantity = 0.0
                current_row += 1
                row = worksheet.row(current_row)
                row_3 = row[3].value
                if isinstance(row_3, float):
                    row_3 = int(row_3)
                row_5 = row[5].value
                if isinstance(row_5, float):
                    row_5 = int(row_5)
                if row[0].value and not row[1].value:
                    raise ValidationError(_('Please add Finished product SKU.'))
                finished_product = self.env['product.product'].search([
                    ('id', '=', production_id.product_id.id),
                    ('default_code', '=', str(row[0].value)),
                    ('tracking', '=', 'serial')])
                if not finished_product:
                    raise ValidationError(_(
                        "Finished Product SKU: %s doesn't match to the finished product" % row[
                            0].value))
                if row[1].value:
                    row_1 = row[1].value
                    if isinstance(row_1, float):
                        row_1 = int(row_1)
                    finished_lot = lot_obj.search([
                        ('product_id', '=', production_id.product_id.id),
                        ('company_id', '=', company_id.id),
                        ('name', '=', row_1)])
                    if finished_lot:
                        sml_rec = self.env['stock.move.line'].search([
                            ('lot_id', '=', finished_lot.id),
                            ('state', 'in', ('done', 'cancel')),
                            ('production_id', '!=', production_id.id),
                            ('product_id', '=', finished_lot.product_id.id)])
                        if sml_rec:
                            raise ValidationError(_(
                                'Lot %s is used in Manufacturing Order: %s!' % (
                                    sml_rec.lot_id.name, sml_rec.production_id.name)))
                    if row_1 not in f_lot_sr_no_list:
                        f_lot_sr_no_list.append(row_1)
                if row[2].value:
                    row_2 = (str(row[2].value).strip())
                    if not row[4].value:
                        raise ValidationError(
                            _('Quantity is not listed for Component SKU: %s' % row_2))
                    component_product = self.env['product.product'].search(
                        [('default_code', '=', row_2)])
                    if not component_product:
                        raise ValidationError(_('Component SKU %s is not in system' % row_2))
                    else:
                        if component_product_lst and component_product and \
                                component_product.id not in component_product_lst:
                            raise ValidationError(_(
                                "Components SKU: %s doesn't match to the Components in BOM" % row_2))
                        if component_product.tracking not in ['serial', 'lot'] and row_3:
                            raise ValidationError(
                                _('Serial Number not required for component_sku %s' % row_2))
                        if production_id.is_slot:
                            if row_5 and component_product.id not in bom_dict:
                                raise ValidationError(
                                    _('Slot: %s for Component Sku: %s is not mentioned in BOM.' % (
                                        row_5, component_product.default_code)))
                            if component_product.id in bom_dict and (
                                    component_product.id, str(row_5)) not in bom_dict.items():
                                raise ValidationError(_(
                                    "Slot: %s for Component Sku: %s doesn't match to Slot "
                                    "mentioned in BOM." % (row_5, component_product.default_code)))
                        if component_product.type == 'product':
                            if component_product.tracking in ['serial', 'lot']:
                                if 'serialized_dict' not in component_dict:
                                    component_dict.update(
                                        {'serialized_dict': {row_2: {row_3: row[4].value}}})
                                elif row_2 not in component_dict['serialized_dict']:
                                    component_dict['serialized_dict'].update(
                                        {row_2: {row_3: row[4].value}})
                                elif row_2 in component_dict['serialized_dict'] and \
                                        not row_3 in component_dict['serialized_dict'][row_2]:
                                    component_dict['serialized_dict'][row_2].update(
                                        {row_3: row[4].value})
                                elif component_product.tracking == 'lot':
                                    if row_3 in component_dict['serialized_dict'][row_2]:
                                        serialized_qty = component_dict['serialized_dict'][row_2][
                                            row_3]
                                    component_dict['serialized_dict'][row_2][
                                        row_3] = serialized_qty + row[4].value
                                if not row_3 and row_2:
                                    raise ValidationError(_('Please enter serial number for '
                                                            'Component SKU %s. ' % row_2))
                                if component_product.tracking == 'serial':
                                    if row_3 and row[4].value != 1:
                                        raise ValidationError(
                                            _('Serialize component SKU %s seria'
                                              'l number: %s quantity should be'
                                              '1.' % (row_2, row_3)))
                                if row_3:
                                    comp_serial_lot = self.env['stock.production.lot'].search(
                                        [('product_id', '=', component_product.id),
                                         ('name', '=', row_3)])
                                    if not comp_serial_lot:
                                        raise ValidationError(
                                            _('Serial number: %s of component %s is not available '
                                              'in system' % (row_3, row_2)))
                                    if row_1 and row_1 not in finished_serial_no_dict:
                                        finished_serial_no_dict[row_1] = {'serialize_dict': {
                                            row_2: {'slot': {row_5: {row_3: row[4].value}}}}}
                                    elif 'serialize_dict' not in finished_serial_no_dict[row_1]:
                                        finished_serial_no_dict[row_1]['serialize_dict'] = {
                                            row_2: {'slot': {row_5: {row_3: row[4].value}}}}

                                    elif row_2 not in finished_serial_no_dict[row_1][
                                        'serialize_dict']:
                                        finished_serial_no_dict[row_1]['serialize_dict'].update(
                                            {row_2: {'slot': {row_5: {row_3: row[4].value}}}})
                                    elif row_2 in finished_serial_no_dict[row_1]['serialize_dict']:
                                        if row_5 not in \
                                                finished_serial_no_dict[row_1]['serialize_dict'][
                                                    row_2]['slot']:
                                            finished_serial_no_dict[row_1]['serialize_dict'][row_2][
                                                'slot'].update(
                                                {row_5: {row_3: row[4].value}})
                                        elif row_3 not in \
                                                finished_serial_no_dict[row_1]['serialize_dict'][
                                                    row_2]['slot'][row_5]:
                                            finished_serial_no_dict[row_1]['serialize_dict'][row_2][
                                                'slot'][row_5].update({row_3: row[4].value})
                                        # need to discuss
                                        elif row_3 in \
                                                finished_serial_no_dict[row_1]['serialize_dict'][
                                                    row_2]['slot'][row_5]:
                                            quantity = \
                                                finished_serial_no_dict[row_1]['serialize_dict'][
                                                    row_2]['slot'][row_5][row_3]
                                            finished_serial_no_dict[row_1]['serialize_dict'][row_2][
                                                'slot'][row_5][row_3] = quantity + row[4].value
                                else:
                                    if row_1 and row_1 not in finished_serial_no_dict:
                                        finished_serial_no_dict[row_1] = {
                                            'serialize_dict': {row_2: {row_3: row[4].value}}}
                                    elif 'serialize_dict' not in finished_serial_no_dict[row_1]:
                                        finished_serial_no_dict[row_1]['serialize_dict'] = {
                                            row_2: {row_3: row[4].value}}
                                    elif row_2 not in finished_serial_no_dict[row_1][
                                        'serialize_dict']:
                                        finished_serial_no_dict[row_1]['serialize_dict'].update(
                                            {row_2: {row_3: row[4].value}})
                                    elif row_2 in finished_serial_no_dict[row_1]['serialize_dict']:
                                        if row_3 not in \
                                                finished_serial_no_dict[row_1]['serialize_dict'][
                                                    row_2]:
                                            finished_serial_no_dict[row_1]['serialize_dict'][
                                                row_2].update({row_3: row[4].value})
                                        elif row_3 in \
                                                finished_serial_no_dict[row_1]['serialize_dict'][
                                                    row_2]:
                                            quantity = \
                                                finished_serial_no_dict[row_1]['serialize_dict'][
                                                    row_2][row_3]
                                            finished_serial_no_dict[row_1]['serialize_dict'][row_2][
                                                row_3] = quantity + row[4].value
                            elif component_product.tracking == 'none':
                                if 'non_serialize_dict' not in component_dict:
                                    component_dict.update(
                                        {'non_serialize_dict': {row_2: row[4].value}})
                                elif row_2 not in component_dict['non_serialize_dict']:
                                    component_dict['non_serialize_dict'].update(
                                        {row_2: row[4].value})
                                elif row_2 in component_dict['non_serialize_dict']:
                                    non_serialized_qty = component_dict['non_serialize_dict'][row_2]
                                    component_dict['non_serialize_dict'][
                                        row_2] = non_serialized_qty + row[4].value
                                if production_id.is_slot:
                                    if row_1 and row_1 not in finished_serial_no_dict:
                                        finished_serial_no_dict[row_1] = {
                                            'non_serialize_dict': {
                                                row_2: {'slot': {row_5: row[4].value}}}}
                                    elif 'non_serialize_dict' not in finished_serial_no_dict[row_1]:
                                        finished_serial_no_dict[row_1]['non_serialize_dict'] = {
                                            row_2: {'slot': {row_5: row[4].value}}}
                                    elif row_2 not in finished_serial_no_dict[row_1][
                                        'non_serialize_dict']:
                                        finished_serial_no_dict[row_1]['non_serialize_dict'].update(
                                            {row_2: {'slot': {row_5: row[4].value}}})
                                    elif row_2 in finished_serial_no_dict[row_1][
                                        'non_serialize_dict']:
                                        if row_5 not in finished_serial_no_dict[row_1][
                                            'non_serialize_dict'][row_2]['slot']:
                                            finished_serial_no_dict[row_1]['non_serialize_dict'][
                                                row_2]['slot'].update({row_5: row[4].value})
                                        elif row_5 in finished_serial_no_dict[row_1][
                                            'non_serialize_dict'][row_2]['slot']:
                                            quantity = finished_serial_no_dict[row_1][
                                                'non_serialize_dict'][row_2]['slot']
                                            finished_serial_no_dict[row_1]['non_serialize_dict'][
                                                row_2]['slot'] = quantity + row[4].value
                                else:
                                    if row_1 and row_1 not in finished_serial_no_dict:
                                        finished_serial_no_dict[row_1] = {
                                            'non_serialize_dict': {row_2: row[4].value}}
                                    elif 'non_serialize_dict' not in finished_serial_no_dict[row_1]:
                                        finished_serial_no_dict[row_1]['non_serialize_dict'] = {
                                            row_2: row[4].value}
                                    elif row_2 not in finished_serial_no_dict[row_1][
                                        'non_serialize_dict']:
                                        finished_serial_no_dict[row_1]['non_serialize_dict'].update(
                                            {row_2: row[4].value})
                                    elif row_2 in finished_serial_no_dict[row_1][
                                        'non_serialize_dict']:
                                        qty = finished_serial_no_dict[row_1]['non_serialize_dict'][
                                            row_2]
                                        finished_serial_no_dict[row_1]['non_serialize_dict'][
                                            row_2] = qty + row[4].value
                        elif component_product.type == 'consu':
                            if 'non_serialize_dict' not in component_dict:
                                component_dict.update({'non_serialize_dict': {row_2: row[4].value}})
                            elif row_2 not in component_dict['non_serialize_dict']:
                                component_dict['non_serialize_dict'].update({row_2: row[4].value})
                            elif row_2 in component_dict['non_serialize_dict']:
                                non_serialized_qty = component_dict['non_serialize_dict'][row_2]
                                component_dict['non_serialize_dict'][row_2] = \
                                    non_serialized_qty + row[4].value
                            if production_id.is_slot:
                                if row_1 and row_1 not in finished_serial_no_dict:
                                    finished_serial_no_dict[row_1] = {
                                        'non_serialize_dict': {
                                            row_2: {'slot': {row_5: row[4].value}}}}
                                elif 'non_serialize_dict' not in finished_serial_no_dict[row_1]:
                                    finished_serial_no_dict[row_1]['non_serialize_dict'] = {
                                        row_2: {'slot': {row_5: row[4].value}}}
                                elif row_2 not in finished_serial_no_dict[row_1][
                                    'non_serialize_dict']:
                                    finished_serial_no_dict[row_1]['non_serialize_dict'].update(
                                        {row_2: {'slot': {row_5: row[4].value}}})
                                elif row_2 in finished_serial_no_dict[row_1]['non_serialize_dict']:
                                    if row_5 not in \
                                            finished_serial_no_dict[row_1]['non_serialize_dict'][
                                                row_2]['slot']:
                                        finished_serial_no_dict[row_1]['non_serialize_dict'][row_2][
                                            'slot'].update({row_5: row[4].value})
                                    elif row_5 in \
                                            finished_serial_no_dict[row_1]['non_serialize_dict'][
                                                row_2]['slot']:
                                        quantity = \
                                            finished_serial_no_dict[row_1]['non_serialize_dict'][
                                                row_2]['slot']
                                        finished_serial_no_dict[row_1]['non_serialize_dict'][row_2][
                                            'slot'] = quantity + row[4].value
                            else:
                                if row_1 and row_1 not in finished_serial_no_dict:
                                    finished_serial_no_dict[row_1] = {
                                        'non_serialize_dict': {row_2: row[4].value}}
                                elif 'non_serialize_dict' not in finished_serial_no_dict[row_1]:
                                    finished_serial_no_dict[row_1]['non_serialize_dict'] = {
                                        row_2: row[4].value}
                                elif row_2 not in finished_serial_no_dict[row_1][
                                    'non_serialize_dict']:
                                    finished_serial_no_dict[row_1]['non_serialize_dict'].update(
                                        {row_2: row[4].value})
                                elif row_2 in finished_serial_no_dict[row_1]['non_serialize_dict']:
                                    qty = finished_serial_no_dict[row_1]['non_serialize_dict'][
                                        row_2]
                                    finished_serial_no_dict[row_1]['non_serialize_dict'][
                                        row_2] = qty + row[4].value
            finished_product_row_dict = {
                (str(row[0].value).strip()): finished_serial_no_dict}
            if f_lot_sr_no_list and len(f_lot_sr_no_list) != production_id.product_qty:
                raise ValidationError(
                    _('Total Serial number provided for Finished Product SKU %s is %s expected '
                      'serial number is %s' % (str(row[0].value), len(f_lot_sr_no_list),
                                               production_id.product_qty)))

            for comp_key, comp_vals in component_dict.items():
                if comp_key == 'serialized_dict':
                    for serial_key, serial_vals in comp_vals.items():
                        serialized_lot_qty = 0.0
                        component_product = self.env['product.product'].search([
                            ('default_code', '=', serial_key)])
                        if component_product:
                            if component_product.tracking in ['serial', 'lot']:
                                for serial_lot_key, serial_lot_vals in serial_vals.items():
                                    slot_qty = 0.0
                                    serial_qty = 0.0
                                    lot_qty = 0.0
                                    slot_diff_qty = 0.0
                                    comp_serial_lot = lot_obj.search([
                                        ('product_id', '=', component_product.id),
                                        ('company_id', '=', company_id.id),
                                        ('name', '=', serial_lot_key)])
                                    if comp_serial_lot:
                                        serialized_lot_qty += round(serial_lot_vals, 3)
                                        serial_qty = round(serial_lot_vals, 3)
                                        quants = self.env['stock.quant'].search(
                                            [('product_id', '=', component_product.id),
                                             ('lot_id', '=', comp_serial_lot.id),
                                             ('location_id.usage', '=', 'internal')])
                                        quants_on_hand_qty = quants.mapped('quantity')
                                        quants_reserve_qty = quants.mapped('reserved_quantity')
                                        quants_qty = sum(
                                            quants_on_hand_qty) - sum(quants_reserve_qty)
                                        if quants and quants_qty < round(serial_lot_vals, 3):
                                            raise ValidationError(
                                                _("Insufficient Quantity avail"
                                                  "able for Serial Number : %s of "
                                                  "Component SKU: %s." % (
                                                      serial_lot_key, serial_key)))
                                        if not quants:
                                            raise ValidationError(
                                                _('No quantity available for S'
                                                  'erial Number : %s of Compon'
                                                  'ent SKU: %s ' % (serial_lot_key, serial_key)))
                                        if component_product.tracking == 'serial':
                                            sml_ids = self.env['stock.move.line'].search([
                                                ('product_id', '=', component_product.id),
                                                ('lot_id', '=', comp_serial_lot.id),
                                                ('state', '!=', 'cancel'),
                                                ('picking_code', 'in',
                                                 ['outgoing', 'mrp_operation'])])
                                            for sml_rec in sml_ids:
                                                if sml_rec.production_id and \
                                                        sml_rec.move_id.raw_material_production_id:
                                                    slot_qty += sml_rec.qty_done
                                            if quants_qty - slot_qty < serial_qty:
                                                raise ValidationError(
                                                    _('Lots/Serial Number: %s for Component SKU: %s'
                                                      ' is not available.' %
                                                      (comp_serial_lot.name,
                                                       component_product.default_code)))
                                        elif component_product.tracking == 'lot':
                                            sml_ids = self.env['stock.move.line'].search([
                                                ('product_id', '=', component_product.id),
                                                ('lot_id', '=', comp_serial_lot.id),
                                                ('state', '!=', 'cancel')])
                                            for sml_rec in sml_ids:
                                                if sml_rec.production_id and \
                                                        sml_rec.move_id.raw_material_production_id:
                                                    lot_qty += sml_rec.qty_done
                                            if sml_ids and quants_qty - lot_qty < serial_qty:
                                                raise ValidationError(
                                                    _('Lots/Serial Number: %s for Component SKU: %s'
                                                      ' is not available.' % (
                                                        comp_serial_lot.name,
                                                        component_product.default_code)))
                                for raw_move in production_id.move_raw_ids.search(
                                        [('raw_material_production_id', '=', production_id.id),
                                         ('product_id', '=', component_product.id)]):
                                    if serialized_lot_qty != raw_move.product_uom_qty:
                                        raise ValidationError(
                                            _("Total quantity provided for serialized component sku"
                                              " %s is %s expected quantity is %s" % (
                                                  serial_key, serialized_lot_qty,
                                                  raw_move.product_uom_qty)))
                elif comp_key == 'non_serialize_dict':
                    for non_serial_key, non_serial_vals in comp_vals.items():
                        component_product = self.env['product.product'].search([
                            ('default_code', '=', non_serial_key)])
                        if component_product:
                            if component_product.type == 'product' and \
                                    component_product.tracking == 'none':
                                non_serialized_lot_qty = round(non_serial_vals, 3)
                                quants = self.env['stock.quant'].search(
                                    [('product_id', '=', component_product.id),
                                     ('location_id.usage', '=', 'internal')])
                                quants_on_hand_qty = quants.mapped('quantity')
                                quants_reserve_qty = quants.mapped(
                                    'reserved_quantity')
                                quants_qty = sum(
                                    quants_on_hand_qty) - sum(quants_reserve_qty)
                                if quants and quants_qty < non_serial_vals:
                                    raise ValidationError(
                                        _("Insufficient Quantity available for Component SKU: %s."
                                          % component_product.default_code))
                                if not quants:
                                    raise ValidationError(
                                        _('No quantity available for Component SKU:'
                                          ' %s.' % non_serial_key))
                                for raw_move in production_id.move_raw_ids.search(
                                        [('raw_material_production_id', '=', production_id.id),
                                         ('product_id', '=', component_product.id)]):
                                    if non_serialized_lot_qty != raw_move.product_uom_qty:
                                        raise ValidationError(
                                            _("Total quantity provided for component sku %s is %s "
                                              "expected quantity is %s" % (
                                                  non_serial_key, non_serialized_lot_qty,
                                                  raw_move.product_uom_qty)))
                            elif component_product.type == 'consu':
                                non_serialized_lot_qty = round(non_serial_vals, 3)
                                for raw_move in production_id.move_raw_ids.search(
                                        [('raw_material_production_id', '=', production_id.id),
                                         ('product_id', '=', component_product.id)]):
                                    if non_serialized_lot_qty != raw_move.product_uom_qty:
                                        raise ValidationError(
                                            _("Total quantity provided for component sku %s is %s "
                                              "expected quantity is %s" % (
                                                  non_serial_key, non_serialized_lot_qty,
                                                  raw_move.product_uom_qty)))

            if production_id and production_id.product_id and \
                    production_id.product_id.tracking == 'serial':
                for key, value in finished_product_row_dict.items():
                    finished_product = self.env['product.product'].search([
                        ('id', '=', production_id.product_id.id),
                        ('default_code', '=', key),
                        ('tracking', '=', 'serial')])
                    if finished_product:
                        for f_key, vals in value.items():
                            finished_lot = lot_obj.search(
                                [('product_id', '=', production_id.product_id.id),
                                 ('company_id', '=', company_id.id),
                                 ('name', '=', f_key)])
                            if not finished_lot:
                                finished_lot = lot_obj.create(
                                    {'product_id': production_id.product_id.id,
                                     'company_id': company_id.id,
                                     'name': f_key})
                            for finished_move in production_id.move_finished_ids:
                                finished_move_vals = {
                                    'move_id': finished_move.id,
                                    'product_id': finished_move.product_id.id,
                                    'location_id': finished_move.location_id.id,
                                    'location_dest_id': finished_move.location_dest_id.id,
                                    'product_uom_id': finished_move.product_id.uom_id.id,
                                    'qty_done': 1 if finished_move.product_id.tracking == 'serial' else
                                    finished_move.product_qty,
                                    'lot_id': finished_lot.id or False,
                                    'production_id': production_id.id,
                                }
                                finsihed_move_lines = self.env['stock.move.line'].create(
                                    finished_move_vals)
                            for comp_prod_key, comp_prod_val in vals.items():
                                for comp_key, comp_vals in comp_prod_val.items():
                                    component_product = self.env['product.product'].search([
                                        ('default_code', '=', comp_key)])
                                    if component_product:
                                        comp_sml_rec = self.env['stock.move.line'].search([
                                            ('state', 'in', ('done', 'cancel')),
                                            ('production_id', '!=',
                                             production_id.id),
                                            ('product_id', '=',
                                             component_product.id)])
                                        component_rec = production_id.move_raw_ids.search([
                                            ('product_id', '=',
                                             component_product.id),
                                            ('raw_material_production_id',
                                             '=', production_id.id)])
                                        if component_rec and comp_prod_key == 'non_serialize_dict':
                                            # Added quants
                                            quants = self.env['stock.quant'].search(
                                                [('product_id', '=', component_product.id),
                                                 ('location_id.usage', '=', 'internal')])
                                            quant_info = []
                                            for quant in quants:
                                                location = quant.location_id.complete_name
                                                qty = quant.quantity - quant.reserved_quantity
                                                quant_info.append(str([location, qty]))
                                            formatted_quant_info = "\n".join(quant_info)
                                            component_rec._action_assign()

                                            if component_rec.reserved_availability == \
                                                    component_rec.product_uom_qty:
                                                move_line_recs = self.env['stock.move.line'].search(
                                                    [('move_id', '=', component_rec.id),
                                                     ('qty_done', '=', 0)])

                                                if len(move_line_recs) > 1:
                                                    raise ValidationError(
                                                        _('The total qty for the component [%s] '
                                                          'reqired to be consumed in MO should be '
                                                          'located in a single location only. '
                                                          'Please perform an internal transfer '
                                                          'first.\n %s' % (
                                                              component_product.name,
                                                              str(formatted_quant_info))))
                                                sml_rec = self.env['stock.move.line'].create(
                                                    {'move_id': move_line_recs.move_id.id,
                                                     'product_id': move_line_recs.product_id.id,
                                                     'location_id': move_line_recs.location_id.id,
                                                     'location_dest_id':
                                                         move_line_recs.location_dest_id.id,
                                                     'product_uom_id':
                                                         move_line_recs.product_id.uom_id.id,
                                                     'qty_done': comp_vals,
                                                     'production_id':
                                                         move_line_recs.production_id.id})
                                                sml_rec.write({'lot_produced_ids': [
                                                    (4, finished_lot.id or False)], })
                                                component_rec.write(
                                                    {'move_line_ids': [(4, sml_rec.id or False)]})

                                        elif component_rec and comp_prod_key == 'serialize_dict':
                                            for comp_lot_key, comp_lot_val in comp_vals.items():
                                                if comp_lot_key == 'slot':
                                                    for comp_val_key, comp_val_vals in comp_lot_val.items():
                                                        for serial_slot_key, serial_slot_val in comp_val_vals.items():
                                                            component_lot = lot_obj.search([
                                                                ('product_id', '=',
                                                                 component_product.id),
                                                                ('company_id', '=',
                                                                 company_id.id),
                                                                ('name', '=', serial_slot_key)])

                                                            # Added quants
                                                            quants = self.env['stock.quant'].search(
                                                                [('product_id', '=',
                                                                  component_product.id), (
                                                                     'lot_id', '=',
                                                                     component_lot.id), (
                                                                     'location_id.usage', '=',
                                                                     'internal')])
                                                            quant_info = []
                                                            for quant in quants:
                                                                location = quant.location_id.complete_name
                                                                qty = quant.quantity - quant.reserved_quantity
                                                                quant_info.append(
                                                                    str([location, qty]))
                                                            formatted_quant_info = "\n".join(
                                                                quant_info)
                                                            if len(quants) > 1:
                                                                raise ValidationError(
                                                                    _('The total qty for the '
                                                                      'component [%s] reqired to be'
                                                                      ' consumed in MO should be'
                                                                      ' located in a single '
                                                                      'location only. Please '
                                                                      'perform an internal transfer'
                                                                      ' first.\n %s' %
                                                                      (component_product.name,
                                                                       str(formatted_quant_info))))
                                                            if component_lot:
                                                                lot_comp_sml_rec = self.env[
                                                                    'stock.move.line'].search([
                                                                    ('lot_id', '=',
                                                                     component_lot.id),
                                                                    ('state', 'in',
                                                                     ('done', 'cancel')),
                                                                    ('production_id', '!=',
                                                                     production_id.id),
                                                                    ('product_id', '=',
                                                                     component_product.id),
                                                                ])
                                                            component_prod_vals = {
                                                                'move_id': component_rec.id,
                                                                'product_id': component_rec.product_id.id,
                                                                'location_id': quants.location_id.id,
                                                                'location_dest_id': component_rec.location_dest_id.id,
                                                                'product_uom_id': component_rec.product_id.uom_id.id,
                                                                'qty_done': serial_slot_val,
                                                                'lot_id': component_lot.id or False,
                                                                # for serialize lot
                                                                'production_id': production_id.id,
                                                            }
                                                            stock_move_rec = self.env[
                                                                'stock.move.line'].create(
                                                                component_prod_vals)
                                                            stock_move_rec.write(
                                                                {'slot': comp_val_key,
                                                                 'lot_produced_ids': [(4,
                                                                                       finished_lot.id or False)]})
                                                            #                                                             stock_move_rec.write({'slot': comp_lot_key,})
                                                            component_rec.write({'move_line_ids': [
                                                                (4, stock_move_rec.id or False)]})
                                                else:
                                                    component_lot = lot_obj.search([
                                                        ('product_id', '=',
                                                         component_product.id),
                                                        ('company_id', '=',
                                                         company_id.id),
                                                        ('name', '=', comp_lot_key)])
                                                    if component_lot:
                                                        lot_comp_sml_rec = self.env[
                                                            'stock.move.line'].search([
                                                            ('lot_id', '=',
                                                             component_lot.id),
                                                            ('state', 'in',
                                                             ('done', 'cancel')),
                                                            ('production_id', '!=',
                                                             production_id.id),
                                                            ('product_id', '=',
                                                             component_product.id),
                                                        ])
                                                    component_prod_vals = {
                                                        'move_id': component_rec.id,
                                                        'product_id': component_rec.product_id.id,
                                                        'location_id': quants.location_id.id,
                                                        'location_dest_id': component_rec.location_dest_id.id,
                                                        'product_uom_id': component_rec.product_id.uom_id.id,
                                                        'qty_done': comp_lot_val,
                                                        'lot_id': component_lot.id or False,
                                                        # for serialize lot
                                                        'production_id': production_id.id,
                                                    }
                                                    stock_move_rec = self.env[
                                                        'stock.move.line'].create(
                                                        component_prod_vals)
                                                    stock_move_rec.write(
                                                        {'lot_produced_ids': [
                                                            (4, finished_lot.id or False)]})
                                                    component_rec.write({'move_line_ids': [
                                                        (4, stock_move_rec.id or False)]})

            production_id.write({'is_import_serial': True})
            return {'name': _('Import Serial'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'mrp.production'}
