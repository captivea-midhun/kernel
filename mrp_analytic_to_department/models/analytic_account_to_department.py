# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import fields, models


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    costs_hour_account_id = fields.Many2one(
        'account.analytic.account', string='Department',
        help="Fill this only if you want automatic\
        analytic accounting entries on production orders.")
