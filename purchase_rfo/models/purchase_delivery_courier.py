# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields


class PurchaseDeliveryCourier(models.Model):
    _name = 'purchase.delivery.courier'
    _description = "Purchase Delivery Courier"

    name = fields.Char(string="Courier Name", required=True)
    active = fields.Boolean(string="Active", default=True)
