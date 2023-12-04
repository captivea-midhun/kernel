# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, _
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # Manufacturing traceability report code
    def mrp_update_lot_serial(self, new_lot_sr):
        """
        # Check if serial no exist for new_sr_no and product_id
        # if yes then create stockmove line for old_sr_no and new_sr_no
            # old_sr_no = from_location -> to_loction, to_location -> from_location
            # state = done
            # new_sr_no = from_location, to_location
            # move_id = self.move_id

            # return stock_move_line id
        # else raise
        """
        new_lot_id = self.lot_id.search([('name', '=', new_lot_sr),
                                         ('product_id', '=', self.product_id.id)], limit=1).sudo()
        if not new_lot_id.exists():
            raise UserError(_('%s lot/serial number is not available.') % (new_lot_sr))

        # Check if serial no exist for new_sr_no and product_id
        stock_quant = new_lot_id.quant_ids.filtered(
            lambda x: x.product_id == self.product_id)
        if not stock_quant:
            raise UserError(_('There is zero quantity for lot/serial %s of Product: %s.') % (
                new_lot_id.name, self.product_id.display_name))

        # When lot serial is reserved in another MO
        stock_quant_reserved = new_lot_id.quant_ids.filtered(
            lambda x: x.product_id == self.product_id and x.reserved_quantity == 1)
        if stock_quant_reserved:
            move_line = self.env['stock.move.line'].search(
                [('lot_id', '=', new_lot_id.id),
                 ('product_id', '=', self.product_id.id),
                 ('state', '=', 'assigned')], limit=1)
            production_reference = move_line.production_id.display_name
            if not production_reference:
                production_reference = move_line.move_id.raw_material_production_id.display_name
            raise UserError(_('The lot/serial %s is already reserved in the %s.') % (
                new_lot_id.name, production_reference))

        # When lot serial no is located in another location
        stock_quant_unreserved = new_lot_id.quant_ids.filtered(
            lambda x: x.reserved_quantity == 0 and x.quantity >= 1 and
                      x.product_id == self.product_id)
        stock_quant_in_location = False
        if stock_quant_unreserved:
            stock_quant = self.env['stock.quant'].search([
                ('location_id', 'child_of', self.move_id.location_id.id),
                ('id', 'in', stock_quant_unreserved.ids)])
            stock_quant_in_location = stock_quant.mapped('location_id').filtered(
                lambda x: x.usage == 'internal')
            if not stock_quant_in_location:
                raise UserError(_('Lot/Serial %s of the %s is not in %s location.') % (
                    new_lot_id.name, self.product_id.display_name,
                    self.move_id.location_id.display_name))

        if stock_quant and not stock_quant_reserved and stock_quant_in_location:
            quants = new_lot_id.mapped('quant_ids')
            quant = quants.filtered(lambda x: x.quantity == 1 and x.reserved_quantity == 0 and
                                              x.location_id.usage == 'internal')
            if len(quant) > 1:
                raise UserError(_('The lot/serials %s cannot be reserved.') % (new_lot_id.name))

        self.write({'lot_id': new_lot_id.id})
        return {'new_lot_id': new_lot_id.id,
                'new_lot_name': new_lot_id.name}
