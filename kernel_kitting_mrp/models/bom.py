# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    is_slot = fields.Boolean(string='Is Slot')


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    slot = fields.Char(string='Slot')
    is_slot = fields.Boolean(string='Is Slot', related='bom_id.is_slot')
