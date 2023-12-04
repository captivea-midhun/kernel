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

    subcontractor_ids = fields.Many2many(
        'res.partner', string='Subcontractors', check_company=True,
        related='bom_id.subcontractor_ids')
