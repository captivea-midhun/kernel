# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _svl_empty_stock_am(self, stock_valuation_layers):
        """
        Sets adjustment account in journal entry - debit account when changing
        product type from inventory to consumable
        """
        move_vals_list = super(ProductProduct, self)._svl_empty_stock_am(stock_valuation_layers)
        default_adjustment_account_id = self.env['ir.config_parameter'].sudo() \
            .get_param('inventory_adjustment_extended.default_adjustment_account_id')

        if default_adjustment_account_id:
            for each in move_vals_list:
                first_line = each.get('line_ids')[0][2]
                if first_line.get('debit') > 0:
                    first_line.update({'account_id': int(default_adjustment_account_id)})

        return move_vals_list
