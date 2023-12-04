# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import api, models, fields


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    product_type = fields.Selection(
        'Product Type', related='product_tmpl_id.type', store=True)
    categ_id = fields.Many2one(
        'product.category', string='Product Category',
        related='product_tmpl_id.categ_id', store=True)
    description = fields.Text('Description', translate=True)
    accounting_date = fields.Date('Accounting Date',
                                  help="Date at which the accounting entries will be created"
                                       " in case of automated inventory valuation."
                                       " If empty, the inventory date will be used.")
    created_by = fields.Many2one('res.users', string='Last Updated By')

    @api.model
    def create(self, vals):
        vals['created_by'] = self.env.user.id
        return super(StockQuant, self).create(vals)

    def write(self, vals):
        """
        Override write method to create an IA record on updating qty from product
        """
        vals['created_by'] = self.env.user.id
        if vals.get('inventory_quantity', False) or vals.get('inventory_quantity') == 0:
            accounting_date = vals.get('accounting_date', False) and \
                              vals['accounting_date'] or self.accounting_date
            description = vals.get('description', False) and \
                          vals['description'] or self.description
            ia_rec = self.env['stock.inventory'].create({
                'name': "IA created for " + self.product_id.name,
                'create_uid': self.env.user.id,
                'accounting_date': accounting_date,
                'description': description,
                'product_ids': [(6, 0, [self.product_id.id])]})
            res = super(StockQuant, self).write(vals)
            stock_move_rec = self.env['stock.move'].search([
                ('quant_id', '=', self.id), ('inventory_id', '=', False)])
            ia_rec.action_start()
            ia_rec.action_validate()
            ia_rec.write({'move_ids': stock_move_rec})
            return res
        return super(StockQuant, self).write(vals)

    @api.model
    def _get_inventory_fields_create(self):
        """ Returns a list of fields user can edit when he
            want to create a quant in `inventory_mode`.
        """
        return ['product_id', 'location_id', 'lot_id', 'package_id', 'owner_id',
                'inventory_quantity', 'description', 'accounting_date', 'created_by']

    @api.model
    def _get_inventory_fields_write(self):
        """ Returns a list of fields user can edit when
            he want to edit a quant in `inventory_mode`.
        """
        return ['inventory_quantity', 'description', 'accounting_date', 'created_by']

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        res = super(StockQuant, self)._get_inventory_move_values(
            qty=qty, location_id=location_id, location_dest_id=location_dest_id, out=out)
        for quant in self:
            if quant.description and quant.accounting_date:
                res['quant_id'] = quant.id
                res['qty_adjust'] = True
        return res
