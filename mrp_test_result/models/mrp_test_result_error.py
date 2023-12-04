# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields


class MrpTestResultError(models.Model):
    _name = 'mrp.test.result.error'
    _description = 'MRP Test Result Error'

    name = fields.Char(string="Name")
    active = fields.Boolean(string="Active", default=True)
    error_msg = fields.Text(string="Error Message")
    date_error = fields.Datetime(string="Error Date", default=fields.Datetime.now)
