# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields


class MrpTestResultConfig(models.Model):
    _name = 'mrp.test.result.config'
    _description = 'MRP Test Result Config'

    name = fields.Char(default="Configuration")
    file_path = fields.Char(string="File Path", help="Configure File path")
    error_file_read_path = fields.Char(
        string="Error File Path", help="Configure File path where you want store failed files.")
    success_file_read_path = fields.Char(
        string="Success File Path",
        help="Configure File path where you want store successfully read files.")
