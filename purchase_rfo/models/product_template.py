# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import api, models, _
from odoo.exceptions import ValidationError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    @api.model
    def create(self, vals):
        if vals.get('type') == 'product' and not self.env.user.has_group(
                'purchase_rfo.group_show_inventory_product_type'):
            raise ValidationError(_(
                "You do not have access rights to create or edit inventory products."))
        return super(ProductCategory, self).create(vals)

    def write(self, vals):
        for category in self:
            if vals.get('type') == 'product' and not self.env.user.has_group(
                    'purchase_rfo.group_show_inventory_product_type'):
                raise ValidationError(_(
                    "You do not have access rights to create or edit inventory products."))
            if 'type' in vals and category.type == 'product' and not self.env.user.has_group(
                    'purchase_rfo.group_show_inventory_product_type'):
                raise ValidationError(_(
                    "You do not have access rights to create or edit inventory products."))
        return super(ProductCategory, self).write(vals)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.constrains('categ_id')
    def _check_product_category_type(self):
        if self.categ_id.type == 'product' and not self.env.user.has_group(
                'purchase_rfo.group_show_inventory_product_type'):
            raise ValidationError(_(
                "You do not have access rights to create or edit inventory products."))

    def write(self, vals):
        for template in self:
            if vals.get('type') == 'product' and not self.env.user.has_group(
                    'purchase_rfo.group_show_inventory_product_type'):
                raise ValidationError(_(
                    "You do not have access rights to create or edit inventory products."))
            if 'type' in vals and template.type == 'product' and not self.env.user.has_group(
                    'purchase_rfo.group_show_inventory_product_type'):
                raise ValidationError(_(
                    "You do not have access rights to create or edit inventory products."))
            if 'categ_id' in vals and not self.env.user.has_group(
                    'purchase_rfo.group_change_product_category'):
                raise ValidationError(_(
                    "You do not have access rights to Change Product Category."))
        return super(ProductTemplate, self).write(vals)

    @api.model
    def default_get(self, fields):
        res = super(ProductTemplate, self).default_get(fields)
        res.update({'purchase_method': 'purchase'})
        return res

    @api.constrains('seller_ids', 'purchase_ok')
    def _check_seller_ids(self):
        if not self.seller_ids and self.type == 'product' and self.purchase_ok:
            if self.nbr_reordering_rules:
                raise ValidationError(
                    _("You can't remove vendor because re-ordering rule is configure."))
