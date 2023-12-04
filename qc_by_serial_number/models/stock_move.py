# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _create_quality_checks(self):
        res = super(StockMove, self)._create_quality_checks()
        quality_point_obj = self.env['quality.point'].sudo()
        for moves in self:
            picking = moves.picking_id
            quality_points = quality_point_obj.search(
                [('picking_type_id', '=', picking.picking_type_id.id),
                 '|', ('product_id', 'in', moves.mapped('product_id').ids),
                 '&', ('product_id', '=', False),
                 ('product_tmpl_id', 'in',
                  moves.mapped('product_id').mapped('product_tmpl_id').ids)])
            for point in quality_points:
                if not point.product_id:
                    continue
                quality_check_count = self.env['quality.check'].search_count(
                    [('product_id', '=', point.product_id.id),
                     ('picking_id', '=', picking.id),
                     ('purchase_line_id', '=', moves.purchase_line_id.id),
                     ('point_id', '=', point.id)])
                if point.product_id.tracking in ('lot', 'none'):
                    quality_check_count = int(moves.product_uom_qty)
                if quality_check_count == int(moves.product_uom_qty):
                    continue
                for line in range(int(moves.product_uom_qty) - quality_check_count):
                    self.env['quality.check'].sudo().create({
                        'picking_id': picking.id,
                        'point_id': point.id,
                        'team_id': point.team_id.id,
                        'product_id': point.product_id.id,
                        'company_id': picking.company_id.id,
                        'qty': moves.product_uom_qty if point.product_id.tracking in (
                            'lot', 'none') else 1,
                        'purchase_line_id': moves.purchase_line_id.id})
        return res
