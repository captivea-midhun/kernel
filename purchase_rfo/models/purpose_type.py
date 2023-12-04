# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import fields, models


class PurposeType(models.Model):
    _name = 'purpose.type'
    _description = 'Purchase Purpose Type'
    _order = "name"

    name = fields.Char("Name", required=True)
    active = fields.Boolean(
        'Active', default=True,
        help="By unchecking the active field, you may hide an Purpose type you will not use.")
