# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields, api


class QualityCheck(models.Model):
    _inherit = "quality.check"

    purchase_line_id = fields.Many2one('purchase.order.line', string="Purchase Order Line")
    qty = fields.Float(string="Quantity")
    comments = fields.Char()

    @api.model
    def create(self, vals):
        if not vals.get('purchase_line_id'):
            if vals.get('picking_id'):
                picking_id = self.env['stock.picking'].browse(
                    vals['picking_id'])
                move_id = picking_id.move_lines.filtered(
                    lambda mv: mv.product_id.id == vals['product_id'])[0]
                if move_id:
                    vals.update(
                        {'purchase_line_id': move_id.purchase_line_id and
                                             move_id.purchase_line_id.id or False,
                         'qty': move_id.product_uom_qty
                         if move_id.purchase_line_id.product_id.tracking in ('lot', 'none') else 1})
        return super(QualityCheck, self).create(vals)
