# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = "product.category"

    categ_receive_route_id = fields.Many2one(
        'stock.location.route', string="Receiving Route",)
