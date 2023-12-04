# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    adjustment_account_id = fields.Many2one(
        'account.account',
        config_parameter='inventory_adjustment_extended.default_adjustment_account_id')
