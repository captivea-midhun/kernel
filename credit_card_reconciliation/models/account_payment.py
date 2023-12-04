# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import api, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.model
    def create(self, vals):
        payment = super(AccountPayment, self).create(vals)
        context = dict(self._context) or {}
        if context.get('to_attachment', False):
            attachment_value = {'name': payment.name,
                                'res_name': payment.name,
                                'res_model': payment._name,
                                'res_id': payment.id,
                                'type': 'binary',
                                'datas': context['to_attachment']}
            self.env['ir.attachment'].create(attachment_value)
        return payment
