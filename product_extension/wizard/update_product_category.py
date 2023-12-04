# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields, _


class UpdateProductCategory(models.TransientModel):
    _name = 'update.product.category'
    _description = 'Update Product Category Wizard'

    categ_id = fields.Many2one('product.category', string='Product Category')
    product_data_ids = fields.One2many('update.product.category.line', 'update_product_categ_id')

    def update_product_category(self):
        """
        Update product category and also change product type based on product category
        Post log note for update.
        :return: True
        """
        for rec in self.product_data_ids:
            product_id = rec.product_id
            default_code = product_id.default_code
            if default_code:
                product_id.write({'default_code': default_code + ' (Archived)'})
            update_dict = {'name': product_id.name,
                           'default_code': default_code or '',
                           'standard_price': product_id.standard_price,
                           'categ_id': self.categ_id.id,
                           'seller_ids': product_id.seller_ids}
            product_id.archive_button()
            new_product_id = product_id.copy(update_dict)
            new_product_id._onchange_categ_id()
            new_product_id.message_post(body=_("Product Type Updated"))
        return True


class UpdateProductCategoryLine(models.TransientModel):
    _name = 'update.product.category.line'
    _description = 'Contain Product Data'

    update_product_categ_id = fields.Many2one('update.product.category')
    product_id = fields.Many2one('product.product', string='Product')
