from odoo import fields, models, api, _
from odoo.exceptions import Warning


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountMoveLine, self)._onchange_product_id()
        if self.product_id and self.product_id.to_be_archived:
            return {
                'warning': {'title': 'Product Archived Warning', 'message': (f'Product(s) {self.product_id.name} '
                                                                             'is planned to be Archived. '
                                                                             ' Please select Continue to proceed or '
                                                                             'remove the product(s) before '
                                                                             'proceeding'), },
            }
        return res

class AccountMove(models.Model):
    _inherit = 'account.move'

    # def copy(self, default=None):
    #     res = super(AccountMove, self).copy(default)
    #     prods = self.invoice_line_ids.filtered(lambda l: l.product_id.to_be_archived)
    #     if prods:
    #         list_of_names = prods.mapped('name')
    #         products = ", ".join(list_of_names)
    #         message = f"""<p style="color:red;">Product(s) {products} is/are planned to be Archived. Please remove the product(s) before
    # proceeding.</p> """
    #         res.message_post(
    #             body=message)
    #     return res

    @api.model
    def create(self, vals_list):
        res = super(AccountMove, self).create(vals_list)
        prods = res.invoice_line_ids.filtered(lambda l: l.product_id.to_be_archived)
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
        res = super(AccountMove, self).write(vals)
        product_ids = set()
        if 'invoice_line_ids' in og_vals:
            for prod_line in og_vals['invoice_line_ids']:
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

