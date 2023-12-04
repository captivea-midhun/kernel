# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import fields, models, api


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    state = fields.Selection(selection_add=[('cancel', 'Cancel')])
    cancel_move_id = fields.Many2one('stock.move', 'Scrap Move', readonly=True, check_company=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = {}
        if self.product_id:
            if self.tracking == 'serial':
                self.scrap_qty = 1
            self.product_uom_id = self.product_id.uom_id.id
            # Check if we can get a more precise location instead of
            # the default location (a location corresponding to where the
            # reserved product is stored)
            if self.picking_id:
                for move_line in self.picking_id.move_line_ids:
                    if move_line.product_id == self.product_id:
                        self.location_id = move_line.location_id \
                            if move_line.state != 'done' \
                            else move_line.location_dest_id
                        break
            if self.production_id and self.production_id.state not in ['done', 'cancel']:
                for move_id in self.production_id.move_raw_ids:
                    if move_id.product_id == self.product_id and \
                            move_id.reserved_availability == 1:
                        move_ids = move_id.move_line_ids and move_id.move_line_ids[0]
                        self.lot_id = move_ids and move_ids.lot_id and \
                                      move_ids.lot_id.id or False
                        break
            elif self.production_id.state == 'done' and self.production_id.product_qty == 1:
                move_ids = self.production_id.finished_move_line_ids.filtered(
                    lambda x: x.state == 'done')
                self.lot_id = move_ids and move_ids[0] and move_ids[0].lot_id and \
                              move_ids[0].lot_id.id or False

            # Add domain to search only those location that has quantities.
            location_ids = self.env['stock.quant'].search([
                ('product_id', '=', self.product_id.id),
                ('location_id.usage', '=', 'internal')]).mapped('location_id').ids
            if location_ids:
                if len(location_ids) == 1:
                    self.location_id = location_ids[0]
                res['domain'] = {'location_id': [('id', 'in', location_ids)]}
            return res

    def action_get_stock_move_lines(self):
        res = super(StockScrap, self).action_get_stock_move_lines()
        res['domain'] = ['|', ('move_id', '=', self.move_id.id),
                         ('move_id', '=', self.cancel_move_id.id)]
        return res

    def _prepare_cancel_scrap_move_values(self):
        self.ensure_one()
        location_id = self.location_id.id
        if self.picking_id and self.picking_id.picking_type_code == 'incoming':
            location_id = self.picking_id.location_dest_id.id
        vals = {
            'name': self.name,
            'origin': self.origin or self.picking_id.name or self.name,
            'company_id': self.company_id.id,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'state': 'draft',
            'product_uom_qty': self.scrap_qty,
            'location_id': self.scrap_location_id.id,
            'scrapped_return': True,
            'location_dest_id': location_id,
            'move_line_ids': [(0, 0, {'product_id': self.product_id.id,
                                      'product_uom_id': self.product_uom_id.id,
                                      'qty_done': self.scrap_qty,
                                      'location_id': self.scrap_location_id.id,
                                      'location_dest_id': location_id,
                                      'package_id': self.package_id.id,
                                      'owner_id': self.owner_id.id,
                                      'lot_id': self.lot_id.id, })],
            'picking_id': self.picking_id.id}

        if self.production_id:
            vals['origin'] = self.production_id.name or vals['origin']
            if self.product_id in self.production_id.move_finished_ids.mapped('product_id'):
                vals.update({'production_id': self.production_id.id})
            else:
                vals.update({'raw_material_production_id': self.production_id.id})
        return vals

    def action_cancel(self):
        for scrapped_id in self:
            move = self.env['stock.move'].create(scrapped_id._prepare_cancel_scrap_move_values())
            move.with_context(is_scrap=True)._action_done()
            scrapped_id.write({'cancel_move_id': move.id, 'state': 'cancel'})
        return True
