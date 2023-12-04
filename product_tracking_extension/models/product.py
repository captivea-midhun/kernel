# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    tracking = fields.Selection(selection_add=[('lot_serial', 'By Lots - Unique Serial Number')])


class ProductCategory(models.Model):
    _inherit = 'product.category'

    tracking = fields.Selection(selection_add=[('lot_serial', 'By Lots - Unique Serial Number')])
