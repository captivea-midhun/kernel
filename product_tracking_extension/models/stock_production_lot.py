# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    pressure_broadening = fields.Float(string='Pressure Broadening',
                                       digits='Product Unit of Measure')
    display_pressure_broadening = fields.Boolean(string='Hide Pressure Broadening',
                                                 compute='_compute_display_pressure_broadening')

    @api.depends('product_id')
    def _compute_display_pressure_broadening(self):
        for rec in self:
            rec.display_pressure_broadening = True if rec.product_id.default_code == '50-0016-01' else False

    @api.constrains('pressure_broadening')
    def _check_pressure_broadening(self):
        for record in self.filtered(lambda x: x.product_id.default_code == '50-0016-01'):
            exist = self.search(['&', ('pressure_broadening', '=', record.pressure_broadening), '&',
                                 ('product_id.id', '=', record.product_id.id),
                                 ('id', '!=', record.id,),
                                 ('company_id', '=', record.company_id.id)], count=True)
            if exist > 0:
                raise ValidationError("Pressure Broadening must be unique per lot across company")

    @api.model
    def create(self, vals):
        product_id = self.env['product.product'].browse(vals.get('product_id'))
        if product_id.tracking == 'lot_serial' and vals.get('name').find('-') == -1:
            raise UserError(_(
                'Lot/Serial Number must start with prefix XXX-Number for product %s.'
            ) % product_id.display_name)
        return super(StockProductionLot, self).create(vals)

    def write(self, vals):
        res = super(StockProductionLot, self).write(vals)
        if self.product_id.tracking == 'lot_serial' and self.name.find('-') == -1:
            raise UserError(
                _('Lot/Serial Number must start with prefix XXX-Number %s.'
                  ) % self.product_id.display_name)
        return res
