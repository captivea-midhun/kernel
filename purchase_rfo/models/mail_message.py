# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import api, models


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def create(self, vals):
        if vals.get('author_id') == self.env.ref('base.partner_root').id and vals.get(
                'model') == 'purchase.order':
            purchase_order = self.env['purchase.order'].browse(vals.get('res_id'))
            if purchase_order:
                if 'tracking_value_ids' in vals:
                    for line in vals.get('tracking_value_ids'):
                        if line[2]['field_desc'] == 'Approved By':
                            line[2].update({
                                'field_desc': 'Automatically Approved By'})
                        if line[2]['new_value_char'] == 'Approved':
                            line[2].update({
                                'new_value_char': "Automatically Approved"})
                vals.update({
                    'author_id': purchase_order.manager_id.partner_id.id,
                    'email_from': purchase_order.manager_id.email,
                    'reply_to': purchase_order.manager_id.email})
        return super(MailMessage, self).create(vals)
