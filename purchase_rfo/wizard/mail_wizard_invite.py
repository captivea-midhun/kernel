# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import api, fields, models


class Invite(models.TransientModel):
    """ Wizard to invite partners (or channels) and make them followers. """
    _inherit = 'mail.wizard.invite'

    template_id = fields.Many2one(
        'mail.template', 'Use template', index=True, domain="[('model', '=', 'purchase.order')]")

    @api.onchange('template_id')
    def onchange_template_id(self):
        context = self._context
        if context.get('default_res_model') == 'purchase.order':
            tpl = self.env['mail.template'].search([('name', '=', 'Add Follower')])
            self.message = tpl._render_template(tpl.body_html, context.get('default_res_model'),
                                                context.get('default_res_id'), post_process=True)
