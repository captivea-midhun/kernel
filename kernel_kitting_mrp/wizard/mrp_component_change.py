# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields, api


class MRPComponentChange(models.TransientModel):
    _inherit = 'mrp.component.change'

    slot = fields.Char(string='Slot')

    @api.model
    def default_get(self, fields_list):
        defaults = super(MRPComponentChange, self).default_get(fields_list)
        active_id = self.env.context.get('active_id', False)
        move = self.env['stock.move'].browse(active_id)
        defaults['slot'] = move.slot
        return defaults

    def do_change(self):
        res = super(MRPComponentChange, self).do_change()
        active_id = self.env.context.get('active_id', False)
        move = self.env['stock.move'].browse(active_id)
        # daca la cantitatea move.product_uom_qty factorul este de move.unit_factor
        # self.product_uom_qty  factorul este
        move.write({'slot': self.slot})
        return res
