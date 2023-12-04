# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################
"""Contain Production Modification"""
from odoo import models


class MrpProduction(models.Model):
    """Inherited Class"""
    _inherit = 'mrp.production'

    def button_scrap(self):
        """
        Inherit Method for modify product ids.
        Removed product ids from list which contain 0 to consume quantity in component line
        :return: updated res(Dict)
        """
        self.ensure_one()
        res = super(MrpProduction, self).button_scrap()
        ctx = res.get('context', False)
        if ctx:
            product_ids = ctx.get('product_ids', False)
            if product_ids:
                to_rmv_product_ids = self.move_raw_ids.filtered(
                    lambda raw_id: raw_id.product_uom_qty == 0).mapped('product_id').ids
                final_product_ids = list(set(product_ids) - set(to_rmv_product_ids))
                res['context']['product_ids'] = final_product_ids
        return res
