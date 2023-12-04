# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def delete_button(self):
        return self.unlink()

    def archive_button(self):
        if not self:
            context = self._context
            product_id = self.env['product.product'].browse(context.get('active_ids'))
            for record in product_id:
                self = record
                self.active = False
        else:
            self.active = False

    def unarchive_button(self):
        if not self:
            context = self._context
            product_id = self.env['product.product'].browse(context.get('active_ids'))
            for record in product_id:
                self = record
                self.active = True
        else:
            self.active = True

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100,
                     name_get_uid=None):
        res = super(ProductProduct, self)._name_search(
            name=name, args=args, operator=operator,
            limit=limit, name_get_uid=name_get_uid)
        if args is None:
            args = []

        # Search based on vendor product code in product.product model
        args += ([('seller_ids.product_code', operator, name)])
        product_recs = self.search(args)
        if product_recs:
            return product_recs.name_get()
        return res

    def update_category(self):
        """
        Create wizard and Add selected product into wizard
        :return: wizard action
        """
        product_list = []
        for product_id in self:
            product_list.append((0, 0, {'product_id': product_id.id}))
        vals = {'categ_id': False, 'product_data_ids': product_list}
        res_id = self.env['update.product.category'].create(vals)
        return {'name': _('Update Product Category'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env.ref(
                    'product_extension.view_update_product_category_form_view').id,
                'res_model': 'update.product.category',
                'res_id': res_id.id,
                'target': 'new'}
