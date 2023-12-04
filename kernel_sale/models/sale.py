# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    so_notes = fields.Char(string='Notes')

    def _prepare_invoice(self):
        vals = super(SaleOrder, self)._prepare_invoice()
        vals.update({'invoice_notes': self.so_notes})
        return vals
