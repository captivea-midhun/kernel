from odoo import models, fields, api


class Picking(models.Model):
    _inherit = "stock.picking"

    def _create_backorder(self):
        orders = super(Picking, self)._create_backorder()
        for order in orders:
            order.do_unreserve()
        return orders
