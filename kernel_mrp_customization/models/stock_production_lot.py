# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import api, models


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.model
    def default_get(self, fields):
        res = super(StockProductionLot, self).default_get(fields)
        if not res.get('company_id', False):
            res.update({'company_id': self.env.user.company_id.id})
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        ctx = dict(self.env.context) or {}
        company_id = self.env.user.company_id
        product_id = ctx.get('finish_product_id') or ctx.get(
            'component_product_id') or False
        # for workorders
        if product_id:
            domain = [('product_id', '=', product_id), ('name', operator, name),
                      ('company_id', '=', company_id.id)]
            if ctx.get('finish_product'):
                domain += [('quant_ids', '=', False)]
            if ctx.get('component_product_id'):
                domain += [('quant_ids', '!=', False)]

            lot_ids = self.env['stock.production.lot'].search(domain)
            if ctx.get('component_product_id'):
                quant_ids = lot_ids.mapped('quant_ids').filtered(
                    lambda quant: quant.location_id.usage in (
                        'internal', 'transit') and quant.quantity > 0.00)
                lot_ids = quant_ids.mapped('lot_id')
            return lot_ids.name_get()

        return super(StockProductionLot, self).name_search(
            name=name, args=args, operator=operator, limit=limit)
