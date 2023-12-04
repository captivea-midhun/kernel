# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields


class TableHeader(models.Model):
    _name = 'table.header'
    _description = "Table Header"
    _rec_name = 'filename'

    operator = fields.Char(string="Operator")
    part_number = fields.Char(string="PartNumber")
    product_id = fields.Many2one('product.product', string="Product")
    serial_number = fields.Char(string="Serial Number")
    station = fields.Char(string='Station')
    step = fields.Char(string="Step")
    datetime = fields.Datetime(stirng="Datetime")
    filename = fields.Char(string="FileName")
    temperature = fields.Char(string="Temperature")
    notes = fields.Char(string="Notes")
    pass_fail = fields.Boolean(string="PassFail")
    bin = fields.Char(stirng="Bin")
    table_subtest_ids = fields.One2many('table.subtest', 'hid', string="SubTests")


class TableSubTest(models.Model):
    _name = 'table.subtest'
    _description = "Table SubTest"

    parameter = fields.Char(stirng="Parameter")
    result = fields.Float(string="Result")
    pf = fields.Boolean(string="PF")
    parent_parameter = fields.Char(string="ParentParameter")
    hid = fields.Many2one('table.header', string="HID", ondelete='cascade', index=True, copy=False)
    channel = fields.Char(string="Channel")
