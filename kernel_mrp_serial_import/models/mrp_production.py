# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    is_import_serial = fields.Boolean(string="Is Import Serial")
