# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import fields, models


class QualityAlertTeam(models.Model):
    _inherit = 'quality.alert.team'

    users_ids = fields.Many2many('res.users', string="Team Member")
