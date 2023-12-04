# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import fields, api, models


class StockPutawayRule(models.Model):
    _inherit = 'stock.putaway.rule'

    product_tmpl_id = fields.Many2one('product.template')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if not self.product_id:
            self.product_tmpl_id = False
        self.product_tmpl_id = self.product_id.product_tmpl_id.id
