# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, api, tools, _
from odoo.exceptions import ValidationError


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_purchase_order(self, company_id, origins, values):
        vals = super(StockRule, self)._prepare_purchase_order(
            company_id, origins, values)
        department_id = self.env['ir.config_parameter'].sudo().get_param(
            'purchase_rfo.department_id')
        if department_id:
            dept_id = self.env['hr.department'].browse(int(department_id))
            partner_id = self.env['res.partner'].browse(
                vals.get('partner_id'))
            vals.update(
                {'department_id': dept_id.id,
                 'export_restriction': partner_id.export_restriction,
                 'manager_id': dept_id.user_id and dept_id.user_id.id or False})
        return vals

    @api.model
    def _prepare_purchase_order_line(self, product_id, product_qty,
                                     product_uom, company_id, values, po):
        vals = super(StockRule, self)._prepare_purchase_order_line(
            product_id, product_qty, product_uom, company_id, values, po)
        account_id = self.env['ir.config_parameter'].sudo().get_param(
            'purchase_rfo.po_expense_account_id')
        vals.update({'account_id': account_id and int(account_id) or False})
        return vals


class StockWarehouseOrderPoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    @api.constrains('product_id')
    def check_product_vendor(self):
        if not self.product_id.seller_ids:
            raise ValidationError(
                _('''Please define vendor on product %s before creating reordering rule.''')
                % self.product_id.display_name)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_done(self):
        res = super(StockPicking, self).action_done()
        context = dict(self.env.context)
        web_base_url = self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        template_id = self.env.ref(
            'purchase_rfo.product_received_email_template')
        for stock_pick in self.filtered(
                lambda p: p.picking_type_id.code == 'incoming'):
            purchase_ids = stock_pick.move_ids_without_package.mapped(
                'purchase_line_id').mapped('order_id')
            if not purchase_ids:
                continue
            for purchase_id in purchase_ids:
                partner_id = purchase_id.company_id.partner_id
                web_base_url += '/web#id=%d&view_type=form&model=%s' % (
                    purchase_id.id, purchase_id._name)
                context.update({'web_base_url': web_base_url})
                if partner_id.email:
                    email_from = tools.formataddr(
                        (partner_id.name, partner_id.email))
                else:
                    email_from = self.env.company.catchall
                email_values = {'email_to': purchase_id.user_id.email,
                                'email_from': email_from}
                template_id.with_context(context).send_mail(
                    purchase_id.id, force_send=True, email_values=email_values)
        return res
