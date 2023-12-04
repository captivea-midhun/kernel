# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    manufacturer = fields.Char(string='Manufacturer')

    def delete_button(self):
        return self.unlink()

    def archive_button(self):
        if not self:
            context = self._context
            product_id = self.env['product.template'].browse(context.get('active_ids'))
            for record in product_id:
                self = record
                self.active = False
        else:
            self.active = False

    def unarchive_button(self):
        if not self:
            context = self._context
            product_id = self.env['product.template'].browse(context.get('active_ids'))
            for record in product_id:
                self = record
                self.active = True
        else:
            self.active = True
