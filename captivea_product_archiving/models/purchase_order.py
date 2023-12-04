from odoo import fields, models, api, _
from odoo.exceptions import Warning


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

#     def copy(self, default=None):
#         res = super(PurchaseOrder, self).copy(default)
#         prods = self.order_line.filtered(lambda l: l.product_id.to_be_archived)
#         if prods:
#             list_of_names = prods.mapped('name')
#             products = ", ".join(list_of_names)
#             message = f"""<p style="color:red;">Product(s) {products} is/are planned to be Archived. Please remove the product(s) before
# proceeding.</p> """
#             res.message_post(
#                 body=message)
#         return res

    @api.model
    def create(self, vals_list):
        res = super(PurchaseOrder, self).create(vals_list)
        prods = res.order_line.filtered(lambda l: l.product_id.to_be_archived)
        if prods:
            list_of_names = prods.mapped('name')
            products = list(set(list_of_names))
            products = ", ".join(products)
            message = f"""<p style="color:red;">Product(s) {products} is/are planned to be Archived. Please remove the product(s) before
        proceeding.</p> """
            res.message_post(
                body=message)
        return res

    def write(self, vals):
        og_vals = vals.copy()
        res = super(PurchaseOrder, self).write(vals)
        product_ids = set()
        if 'order_line' in og_vals:
            for prod_line in og_vals['order_line']:
                if prod_line[0] == 0:
                    product_ids.add(prod_line[2]['product_id'])
            prods = False
            if product_ids:
                prods = self.env['product.product'].browse(product_ids)
                prods = prods.filtered(lambda p: p.to_be_archived)
            if prods:
                list_of_names = prods.mapped('name')
                products = ", ".join(list_of_names)
                message = f"""<p style="color:red;">Product(s) {products} is/are planned to be Archived. Please remove the product(s) before
                    proceeding.</p> """
                self.message_post(
                    body=message)
        return res



class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()
        if self.product_id and self.product_id.to_be_archived:
            return {
                'warning': {'title': 'Product Archived Warning', 'message': (f'Product(s) {self.product_id.name} '
                                                                             'is planned to be Archived. '
                                                                             ' Please select Continue to proceed or '
                                                                             'remove the product(s) before '
                                                                             'proceeding'), },
            }
        return res
