# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class WizardPurchaseTrackingNumber(models.TransientModel):
    _name = 'wizard.purchase.tracking.number'
    _description = "Purchase Tracking Number."

    purchase_id = fields.Many2one('purchase.order', string='Purchase Order')
    po_tracking_number = fields.Char(string="Tracking Number")
    courier_id = fields.Many2one('purchase.delivery.courier', string="Courier")

    def action_set_tracking_number(self):
        """
            This method allows to set tracking number in purchase order and
            send mail to purchase representative.
        """
        self.purchase_id.update({'tracking_number': self.po_tracking_number,
                                 'courier_id': self.courier_id.id})
        partner_id = self.purchase_id.company_id.partner_id
        template = self.env.ref('purchase_rfo.mail_template_wiz_tracking_number')
        context = dict(self.env.context)
        web_base_url = self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        web_base_url += '/web#id=%d&view_type=form&model=%s' % (
            self.purchase_id.id, self._context.get('active_model'))
        context.update({'web_base_url': web_base_url})

        if template:
            template.with_context(context).send_mail(self.id, force_send=True)
        else:
            _logger.warning("No email template found for sending email to the Purchase user")
        return True
