# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = 'stock.move'

    slot = fields.Char(string='Slot')


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    slot = fields.Char(string='Slot')


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    is_slot = fields.Boolean(string='Is Slot', related='bom_id.is_slot')

    def unbuild_and_draft(self):
        unbuild_obj = self.env['mrp.unbuild']
        for rec in self.finished_move_line_ids:
            lot_id = rec.lot_id and rec.lot_id.id
        unbuild_mo_id = unbuild_obj.create({'product_id': self.product_id.id,
                                            'product_uom_id': self.product_uom_id.id,
                                            'bom_id': self.bom_id.id,
                                            'company_id': self.company_id.id,
                                            'product_qty': self.product_qty,
                                            'location_id': self.location_src_id.id,
                                            'location_dest_id': self.location_dest_id.id,
                                            'lot_id': lot_id,
                                            'mo_id': self.id})
        unbuild_mo_id.action_validate()
        new_mo = self.copy()
        for moves in new_mo.move_raw_ids:
            for move_line in moves.move_line_ids:
                move_line.copy()
        new_mo.action_confirm()
        new_mo.action_assign()
        return {'name': _('New MO'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env.ref('mrp.mrp_production_form_view').id,
                'res_model': 'mrp.production',
                'res_id': new_mo.id,
                'target': 'current'}


class MrpAbstractWorkorderLine(models.AbstractModel):
    _inherit = "mrp.abstract.workorder.line"

    def _create_extra_move_lines(self):
        res = super(MrpAbstractWorkorderLine, self)._create_extra_move_lines()
        if self.slot:
            for rec in res:
                rec.update({'slot': self.slot})
        return res

    def _update_move_lines(self):
        """ update a move line to save the workorder line data"""
        self.ensure_one()
        if self.lot_id:
            move_lines = self.move_id.move_line_ids.filtered(
                lambda ml: ml.lot_id == self.lot_id and not ml.lot_produced_ids)
        else:
            move_lines = self.move_id.move_line_ids.filtered(
                lambda ml: not ml.lot_id and not ml.lot_produced_ids)

        # Sanity check: if the product is a serial number and `lot` is already present in the other
        # consumed move lines, raise.
        if self.product_id.tracking != 'none' and not self.lot_id:
            raise UserError(
                _('Please enter a lot or serial number for %s !' % self.product_id.display_name))

        if self.lot_id and self.product_id.tracking == 'serial' and \
                self.lot_id in self.move_id.move_line_ids.filtered(
                lambda ml: ml.qty_done).mapped('lot_id'):
            raise UserError(
                _('You cannot consume the same serial number twice. Please correct the serial '
                  'numbers encoded.'))

        # Update reservation and quantity done
        for ml in move_lines:
            rounding = ml.product_uom_id.rounding
            if float_compare(self.qty_done, 0, precision_rounding=rounding) <= 0:
                break
            quantity_to_process = min(self.qty_done, ml.product_uom_qty - ml.qty_done)
            self.qty_done -= quantity_to_process
            if self.slot:
                ml.write({'slot': self.slot})

            new_quantity_done = (ml.qty_done + quantity_to_process)
            # if we produce less than the reserved quantity to produce the finished products
            # in different lots,
            # we create different component_move_lines to record which one was used
            # on which lot of finished product
            if float_compare(new_quantity_done, ml.product_uom_qty,
                             precision_rounding=rounding) >= 0:
                ml.write({
                    'qty_done': new_quantity_done,
                    'lot_produced_ids': self._get_produced_lots(),
                    'slot': self.slot
                })
            else:
                new_qty_reserved = ml.product_uom_qty - new_quantity_done
                default = {
                    'product_uom_qty': new_quantity_done,
                    'qty_done': new_quantity_done,
                    'lot_produced_ids': self._get_produced_lots(),
                    'slot': self.slot
                }
                ml.copy(default=default)
                ml.with_context(bypass_reservation_update=True).write({
                    'product_uom_qty': new_qty_reserved,
                    'qty_done': 0,
                })
