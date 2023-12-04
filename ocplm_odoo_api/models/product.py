# -*- coding: utf-8 -*-
# Part of odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    revision = fields.Integer('Revision')

    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)

        for product in res:
            ids = []
            for p in self.search(['&', ('id', '!=', product.id), ('default_code', 'ilike', res.default_code)]):
                if p.default_code and res.default_code:
                    if res.default_code.split()[0] == p.default_code.split()[0]:
                        self.env['mail.activity'].create({
                            'activity_type_id': self.env.ref("mail.mail_activity_data_todo").id,
                            'summary': "Going to Dakota",
                            'user_id': self.env.user.id,
                            'date_deadline': fields.Datetime.now(),
                            'res_model_id': self.env['ir.model']._get('product.template').id,
                            'res_id': p.id
                        })
                        ids.append(p.id)

            if ids:
                product.message_post(body=_('Previous revisions exist'))

        return res



class Product(models.Model):
    _inherit = "product.product"

    def create(self, vals):
        res = super(Product, self).create(vals)

        for product in res:
            ids = []
            for p in self.search(['&', ('id', '!=', product.id), ('default_code', 'ilike', res.default_code)]):
                if p.default_code and res.default_code:
                    if res.default_code.split()[0] == p.default_code.split()[0]:
                        self.env['mail.activity'].create({
                            'activity_type_id': self.env.ref("mail.mail_activity_data_todo").id,
                            'summary': "Going to Dakota",
                            'user_id': self.env.user.id,
                            'date_deadline': fields.Datetime.now(),
                            'res_model_id': self.env['ir.model']._get('product.product').id,
                            'res_id': p.id
                        })
                        ids.append(p.id)

            if ids:
                product.message_post(body=_('Previous revisions exist'))

        return res
