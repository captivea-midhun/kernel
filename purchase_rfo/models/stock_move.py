# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    quant_id = fields.Many2one('stock.quant', string='Quant')
    qty_adjust = fields.Boolean('Quantity Adjustment')
