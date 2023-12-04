# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    production_id = fields.Many2one('mrp.production', string="Source Document")

    @api.model
    def create(self, vals):
        context = self._context

        # Condition for manufacturing order
        if vals.get('stock_move_id', False):
            stock_move_id = self.env['stock.move'].browse(vals['stock_move_id'])
            production_id = stock_move_id.production_id
            if not production_id:
                production_id = stock_move_id.raw_material_production_id
            vals.update({'production_id': production_id and production_id.id or False})

        return super(AccountMove, self).create(vals)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    production_id = fields.Many2one('mrp.production', string="Source Document",
                                    compute="_compute_mo_source_document", store=True)

    @api.depends('move_id')
    def _compute_mo_source_document(self):
        for line in self:
            production_id = line.move_id.stock_move_id.production_id
            if not production_id:
                production_id = line.move_id.stock_move_id.raw_material_production_id
            line.production_id = production_id and production_id.id or False
