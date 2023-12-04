# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields, api


class MrpProductProduceLine(models.TransientModel):
    _inherit = "mrp.product.produce.line"

    slot = fields.Char(string='Slot')

    @api.model
    def default_get(self, fields):
        res = super(MrpProductProduceLine, self).default_get(fields)
        bom_line_ids = self.raw_product_produce_id.production_id and \
                       self.raw_product_produce_id.production_id.bom_id and \
                       self.raw_product_produce_id.production_id.bom_id.bom_line_ids
        for bom_line in bom_line_ids:
            if bom_line and bom_line.is_slot and bom_line.product_id and \
                    bom_line.product_id.id == self.product_id.id:
                res['slot'] = bom_line.slot
                break
        return res
