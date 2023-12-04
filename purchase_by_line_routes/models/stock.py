# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    purchase_picking_id = fields.Many2one('purchase.order')

    def _update_picking_location(self, location, picking_type_id):
        """
        Method to update destination location into picking.
        """
        for rec in self:
            rec.location_dest_id = location
            if picking_type_id:
                rec.picking_type_id = picking_type_id
        return True


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        """
        Method to update purchase order into picking.
        """
        vals = super(StockMove, self)._get_new_picking_values()
        purchase_ids = self.move_orig_ids.mapped('purchase_line_id').mapped('order_id')
        if len(purchase_ids.ids) > 0:
            vals['purchase_picking_id'] = purchase_ids[0].id or False,
        return vals
