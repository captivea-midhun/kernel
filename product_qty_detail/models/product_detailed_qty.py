# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields


class ProductDetailedQty(models.TransientModel):
    _name = 'product.detailed.qty'
    _description = 'Contain quantity details of product'

    name = fields.Char(string='Name', default="Net On Hand Qty")
    product_tmpl_id = fields.Many2one('product.template', string='Product')
    product_id = fields.Many2one('product.product', string='Product')
    on_hand_qty = fields.Float(string='Quantity On Hand')
    po_qty_ids = fields.One2many('po.qty', 'detailed_qty_id', 'Purchase Quantity')
    po_qty_rec_ids = fields.One2many('po.qty', 'detailed_qty_rec_id', 'Purchase Quantity Received')
    mo_qty_ids = fields.One2many('mo.qty', 'detailed_qty_id', 'Manufacturing Quantity')
    mo_qty_rec_ids = fields.One2many('mo.qty', 'detailed_qty_rec_id',
                                     'Manufacturing Quantity Received')
    picking_qty_ids = fields.One2many('picking.qty', 'detailed_qty_id',
                                      'Quantity in Delivery Orders')
    picking_qty_rec_ids = fields.One2many('picking.qty', 'detailed_qty_rec_id',
                                          'Received Quantity in Delivery Orders')
    total_remaining_qty = fields.Float(string='Total Remaining Quantity',
                                       help='Total of remaining to receive in Purchase Order')
    total_reserve_qty = fields.Float(string='Total Reserve Quantity',
                                     help='Total Quantity Reserve in Manufacturing Order')
    net_qty = fields.Float(string='Net On Hand Quantity',
                           help='Net On Hand Quantity = Quantity On Hand - Total Reserve Quantity')
    forecast_qty = fields.Float(string='Forecasted Qty',
                                help='Forecasted Qty = Quantity On Hand + Purchased Not Received')


class PoQty(models.TransientModel):
    _name = 'po.qty'
    _description = 'Purchase order incoming quantity'

    detailed_qty_id = fields.Many2one('product.detailed.qty')
    detailed_qty_rec_id = fields.Many2one('product.detailed.qty')
    po_id = fields.Many2one('purchase.order', string='Purchase Order')
    expected_date = fields.Datetime('Expected Date')
    qty = fields.Float(string='Remaining Quantity',
                       help='Remaining receive quantity in Purchase Order '
                            '(Quantity = Ordered Quantity - Received Quantity)')


class MoQty(models.TransientModel):
    _name = 'mo.qty'
    _description = 'Manufacturing order reserve quantity'

    detailed_qty_id = fields.Many2one('product.detailed.qty')
    detailed_qty_rec_id = fields.Many2one('product.detailed.qty')
    mo_id = fields.Many2one('mrp.production', string='Manufacturing Order')
    qty = fields.Float('Reserved Quantity', help='Reserved Quantity in Manufacturing Order')


class PickingQty(models.TransientModel):
    _name = 'picking.qty'
    _description = 'Quantities reserved in pickings'

    detailed_qty_id = fields.Many2one('product.detailed.qty')
    detailed_qty_rec_id = fields.Many2one('product.detailed.qty')
    qty_reserved = fields.Float('Reserved Quantity', help='Reserved Quantities in Deliveries')
    picking_id = fields.Many2one('stock.picking', string='Deliveries')
