# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    receiving_route_id = fields.Many2one(
        'stock.location.route', string="Receiving Route")

    @api.onchange('categ_id')
    def onchange_categ_id(self):
        """
        Method to update route into purchase order line.
        """
        for each in self:
            if each.categ_id.categ_receive_route_id:
                each.receiving_route_id = each.categ_id.categ_receive_route_id
            else:
                each.receiving_route_id = False


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('categ_id')
    def onchange_categ_id(self):
        """
        Method to update route into purchase order line.
        """
        for each in self:
            if each.categ_id.categ_receive_route_id:
                each.receiving_route_id = each.categ_id.categ_receive_route_id
            else:
                each.receiving_route_id = False
