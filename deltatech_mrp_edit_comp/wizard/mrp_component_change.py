# -*- coding: utf-8 -*-
# ©  2015-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _


class MRPComponentChange(models.TransientModel):
    _name = 'mrp.component.change'
    _description = "MRP Component Change "

    product_id = fields.Many2one('product.product')
    product_uom_qty = fields.Float('Quantity', default=1.0,
                                   digits='Unit of Measure', required=True)
    mrp_component_lot_ids = fields.One2many('mrp.component.lot', 'component_id',
                                            string='Components')

    @api.model
    def default_get(self, fields_list):
        defaults = super(MRPComponentChange, self).default_get(fields_list)
        active_id = self.env.context.get('active_id', False)
        move = self.env['stock.move'].browse(active_id)
        if move.state == 'done':
            raise UserError(_('The stock movement status does not allow modification'))
        defaults['product_id'] = move.product_id.id
        defaults['product_uom_qty'] = move.product_uom_qty
        move_lines = self.env['stock.move.line'].search([('move_id', '=', move.id)])
        mv_lines = []
        for each in move_lines:
            if each.lot_id:
                line = (0, 0, {'lot_id': each.lot_id.id,
                               'product_uom_qty': each.product_uom_qty,
                               'qty_done': each.qty_done})
                mv_lines.append(line)
        defaults['mrp_component_lot_ids'] = mv_lines
        return defaults

    def do_change(self):
        active_id = self.env.context.get('active_id', False)
        move = self.env['stock.move'].browse(active_id)

        # List of serials that were reserved previously
        old_serial_id_list = move.move_line_ids.mapped('lot_id').mapped('name')

        # daca la cantitatea move.product_uom_qty factorul este de move.unit_factor
        # self.product_uom_qty  factorul este
        production_id = move.raw_material_production_id
        if production_id and production_id.state in ['to_close', 'done', 'cancel']:
            state = dict(production_id._fields['state'].selection).get(
                production_id.state)
            raise ValidationError(
                "The record should not be in %s state." % (state))
        else:
            move._do_unreserve()
        if move.product_uom_qty != 0:
            unit_factor = self.product_uom_qty * move.unit_factor / move.product_uom_qty
        else:
            unit_factor = 0
        move.write({
            'product_id': self.product_id.id,
            'product_uom_qty': self.product_uom_qty,
            'unit_factor': unit_factor,
            'state': 'confirmed'
        })

        # ------------------ change serial no ------------------

        if self.product_id.tracking == 'serial' and self.mrp_component_lot_ids:

            # Unreserve the move lines
            move.filtered(lambda x: x.state not in ('done', 'cancel'))._do_unreserve()

            # Check if the lot serial no. selected can be reserved
            # else return a UserError
            lot_id_changed_list = self.mrp_component_lot_ids.mapped('lot_id')

            for lot in lot_id_changed_list:

                # When lot serial does not have quantity for the product
                stock_quant = lot.quant_ids.filtered(
                    lambda x: x.product_id == self.product_id)
                if not stock_quant:
                    raise UserError(_(
                        'There is zero quantity for lot/serial %s of product %s.')
                        % (lot.name, self.product_id.name))

                # When lot serial is reserved in another MO
                stock_quant_reserved = lot.quant_ids.filtered(
                    lambda x: x.product_id == self.product_id and
                    x.reserved_quantity == 1)
                if stock_quant_reserved:
                    move_line = self.env['stock.move.line'].search(
                        [('lot_id', '=', lot.id),
                         ('product_id', '=', self.product_id.id),
                         ('state', '=', 'assigned')], limit=1)
                    production_reference = move_line.production_id.name
                    if not production_reference:
                        production_reference = move_line.move_id\
                            .raw_material_production_id.name
                    raise UserError(_(
                        'The lot/serial %s is already reserved in the %s.')
                        % (lot.name, production_reference))

                # When lot serial no is located in another location
                stock_quant_unreserved = lot.quant_ids.filtered(
                    lambda x: x.reserved_quantity == 0 and x.quantity == 1
                    and x.product_id == self.product_id)
                stock_quant_in_location = False
                if stock_quant_unreserved:
                    stock_quant = self.env['stock.quant'].search([
                        ('location_id', 'child_of', move.location_id.id),
                        ('id', 'in', stock_quant_unreserved.ids)])
                    stock_quant_in_location = stock_quant.mapped('location_id')\
                        .filtered(lambda x: x.usage == 'internal')
                    if not stock_quant_in_location:
                        raise UserError(_(
                            'Lot/Serial %s of %s is not in location %s.')
                            % (lot.name, self.product_id.name,
                                move.location_id.display_name))

            # Retrieve quants that can be reserved
            quant_recs = self.env['stock.quant'].search([
                ('product_id', '=', self.product_id.id),
                ('location_id', 'child_of', move.location_id.id),
                ('reserved_quantity', '=', 0),
                ('quantity', '=', 1)])
            lot_recs = quant_recs.mapped('lot_id')

            for move in move.filtered(lambda m: m.state in
                                      ['confirmed', 'waiting', 'partially_available']):

                # Check available qty for product
                available_quantity = self.env['stock.quant']._get_available_quantity(
                    move.product_id, move.location_id, package_id=None)
                if available_quantity <= 0:
                    continue

                # Reserve stock quant and prepare move lines
                for lot in lot_id_changed_list:
                    if lot in lot_recs:
                        quants = lot.mapped('quant_ids')
                        quant = quants.filtered(lambda x: x.quantity == 1 and
                                                x.reserved_quantity == 0 and
                                                x.location_id.usage == 'internal')
                        if len(quant) > 1:
                            raise UserError(_('The lot/serials %s cannot be reserved.')
                                            % (lot.name))
                        quant.sudo().write({'reserved_quantity': 1})
                        # Fix For Ticket Number: 4,518: Issue: Products Reserved in Unknown Process
                        # Added Production id in stock move line
                        sml_vals = move._prepare_move_line_vals(quantity=1, reserved_quant=quant)
                        sml_vals['production_id'] = move.raw_material_production_id and \
                                                    move.raw_material_production_id.id or False
                        self.env['stock.move.line'].create(sml_vals)
                if move.reserved_availability == move.product_uom_qty:
                    move.write({'state': 'assigned'})

                    # List of serials that are reserved currently
                    new_serial_id_list = self.mrp_component_lot_ids\
                        .mapped('lot_id').mapped('name')

                    # Adds a lognote for changed serials
                    combined_list = list(zip(old_serial_id_list, new_serial_id_list))
                    for elm1, elm2 in combined_list:
                        if elm1 != elm2:
                            content = "  \u2022 " + self.product_id.name +\
                                "<br/>" + "Lot/Serial No: " + str(elm1) +\
                                " \u2794 " + str(elm2) + "<br/>"
                            production_id.message_post(body=content)
                else:
                    move.write({'state': 'confirmed'})


class MRPComponentLot(models.TransientModel):
    _name = 'mrp.component.lot'
    _description = "MRP Component Lot"

    component_id = fields.Many2one('mrp.component.change')
    lot_id = fields.Many2one('stock.production.lot', string='Lot/Serial Number')
    product_uom_qty = fields.Float('Reserved')
    qty_done = fields.Float('Done')
