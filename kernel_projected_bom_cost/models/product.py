# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    lowest_vendor_price = fields.Float(
        compute='_get_proposed_cost', readonly=False, store=True, string="Lowest Vendor Price",
        digits='Product Price')

    @api.depends('seller_ids')
    def _get_proposed_cost(self):
        for pt_id in self:
            if pt_id.seller_ids.mapped('price'):
                pt_id.lowest_vendor_price = \
                    min(pt_id.seller_ids.mapped('price')) or 0.0
            else:
                pt_id.lowest_vendor_price = 0.0
