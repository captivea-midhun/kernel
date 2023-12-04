# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    type = fields.Selection(
        [('contact', 'Contact'),
         ('invoice', 'Invoice Address'),
         ('delivery', 'Delivery Address'),
         ('other', 'Other Address'),
         ("private", "Private Address"),
         ], string='Address Type',
        default='contact',
        help="Invoice & Delivery addresses are used in sales orders. Private "
             "addresses are only visible by authorized users.",
        tracking=True)

    street = fields.Char(tracking=True)
    street2 = fields.Char(tracking=True)
    zip = fields.Char(change_default=True, tracking=True)
    city = fields.Char(tracking=True)
    state_id = fields.Many2one("res.country.state", string='State',
                               ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]",
                               tracking=True)
    country_id = fields.Many2one(
        'res.country', string='Country', ondelete='restrict', tracking=True)

    company_type = fields.Selection(selection_add=[('company', 'Company'),
                                                   ('person', 'Individual')],
                                    compute='_compute_company_type',
                                    inverse='_write_company_type')
