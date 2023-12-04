# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, api, _
from odoo.exceptions import ValidationError


class MrpUnbuild(models.Model):
    _inherit = 'mrp.unbuild'

    @api.constrains('product_qty', 'product_id')
    def _check_product_qty(self):
        if self.product_qty > 1 and self.product_id.tracking == 'serial':
            raise ValidationError(_(
                'Unbuild Order product quantity has to be 1 for product with unique serial.'))

    @api.onchange('mo_id')
    def _onchange_mo_id(self):
        res = super(MrpUnbuild, self)._onchange_mo_id()
        move_line_ids = self.mo_id.finished_move_line_ids.filtered(
            lambda l: l.product_id.id == self.mo_id.product_id.id)
        lot_ids = move_line_ids.mapped('lot_id')
        if len(lot_ids) == 1:
            self.lot_id = lot_ids.id
        return res

    @api.onchange('product_id', 'lot_id')
    def _onchange_product_lot(self):
        if self.product_id and self.lot_id:
            move_line_ids = self.env['stock.move.line'].search(
                [('product_id', '=', self.product_id.id),
                 ('lot_id', '=', self.lot_id.id)])
            mo_ids = move_line_ids.mapped('production_id')
            if len(mo_ids) == 1:
                self.mo_id = mo_ids.id


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        product_id = self._context.get('default_product_id')
        manufacturing_id = self._context.get('default_manufacturing_id')
        if product_id and manufacturing_id:
            sml_ids = self.env['stock.move.line'].search(
                [('product_id', '=', product_id),
                 ('production_id', '=', manufacturing_id)])
            lot_ids = sml_ids.mapped('lot_id')
            args += [('id', 'in', lot_ids.ids)]
        return super(StockProductionLot, self)._search(
            args, offset=offset, limit=limit, order=order, count=count,
            access_rights_uid=access_rights_uid)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        product_id = self._context.get('default_product_id')
        lot_id = self._context.get('default_lot_id')
        if product_id and lot_id:
            sml_ids = self.env['stock.move.line'].search(
                [('product_id', '=', product_id), ('lot_id', '=', lot_id)])
            mo_ids = sml_ids.mapped('production_id')
            args += [('id', 'in', mo_ids.ids)]
        return super(MrpProduction, self)._search(
            args, offset=offset, limit=limit, order=order, count=count,
            access_rights_uid=access_rights_uid)
