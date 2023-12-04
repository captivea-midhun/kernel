# -*- encoding: utf-8 -*-
##############################################################################
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2021 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import fields, models


class StockMove(models.Model):
    """
    Inherited StockMove class for
    calculate Net On Hand Qty.
    """

    _inherit = "stock.move"
    net_on_hand_qty = fields.Float(compute='_get_net_on_hand_qty', string='Net On Hand')

    def _get_net_on_hand_qty(self):
        """
        Calculate Net on Hand Quantity
        Calculation :
        Net on Hand Quantity = On Hand Quantity - Total Reserved Quantity in Manufacturing Order
        :return: None
        """
        for order in self:            
            qty_detail, total_reserve_qty = order.product_id._get_mo_qty_details()
            qty_detail_picking, picking_reserved_qty = \
                order.product_id._get_picking_qty_details()
            order.net_on_hand_qty = order.product_id.qty_available - total_reserve_qty - picking_reserved_qty
            # order.net_on_hand_qty = order.product_id.x_studio_stock_qty - total_reserve_qty - picking_reserved_qty
