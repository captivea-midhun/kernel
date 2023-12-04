# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import api, models, fields


class StockLocation(models.Model):
    _inherit = 'stock.location'

    positive_stock_quant_ids = fields.One2many(
        'stock.quant', "location_id", string=None, domain=[('quantity', '>', 0)])
    negative_stock_quant_ids = fields.One2many(
        'stock.quant', "location_id", string=None, domain=[('quantity', '<', 0)])
    product_ids = fields.Many2many(
        'product.product', string='Products', compute='products_at_location')
    product_category_ids = fields.Many2many(
        'product.category', string='Product Category', compute='product_category_at_location')

    @api.depends('quant_ids')
    def products_at_location(self):
        for rec in self:
            rec.product_ids = rec.quant_ids.mapped('product_id')[:3]

    @api.depends('quant_ids')
    def product_category_at_location(self):
        for rec in self:
            rec.product_category_ids = rec.quant_ids.mapped('product_id.categ_id')

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        context = dict(self.env.context) or {}
        if context.get('location_dest_id', False):
            location_dest_id = self.env['stock.location'].browse(
                context['location_dest_id'])
            warehouse = location_dest_id.get_warehouse()
            internal_loc_ids = warehouse.view_location_id.child_ids.filtered(
                lambda location: location.usage == 'internal')
            args = (args or []) + [('id', 'child_of', internal_loc_ids.ids),
                                   ('usage', '=', 'internal')]
        return super(StockLocation, self)._name_search(
            name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        context = dict(self.env.context) or {}
        if context.get('location_dest_id', False):
            location_dest_id = self.env['stock.location'].browse(context['location_dest_id'])
            warehouse = location_dest_id.get_warehouse()
            internal_loc_ids = warehouse.view_location_id.child_ids.filtered(
                lambda location: location.usage == 'internal')
            domain += [('id', 'child_of', internal_loc_ids.ids), ('usage', '=', 'internal')]
        return super(StockLocation, self).search_read(
            domain=domain, fields=fields, offset=offset, limit=limit, order=order)
