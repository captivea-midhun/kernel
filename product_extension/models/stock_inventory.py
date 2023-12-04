# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import fields, models


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    description = fields.Text('Description', translate=True)

    def _get_inventory_lines_values(self):
        res = super(StockInventory, self)._get_inventory_lines_values()
        new_res = []
        for rec in res:
            product_id = self.env['product.product'].browse(rec['product_id'])
            if product_id.type == 'product':
                new_res.append(rec)
        return new_res
