# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields


class res_users(models.Model):
    _inherit = 'res.users'

    journal_ids = fields.Many2many(
        'account.journal', 'journal_user_rel', 'user_id', 'journal_id', string='Allowed Journal')
