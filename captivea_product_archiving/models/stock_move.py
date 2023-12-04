from odoo import fields, models, api, _
from odoo.exceptions import Warning


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(StockMove, self).onchange_product_id()
        if self.product_id and self.product_id.to_be_archived:
            return {
                'warning': {'title': 'Product Archived Warning', 'message': (f'Product(s) {self.product_id.name} '
                                                                             'is planned to be Archived. '
                                                                             ' Please select Continue to proceed or '
                                                                             'remove the product(s) before '
                                                                             'proceeding'), },
            }
        return res


class MRP(models.Model):
    _inherit = 'mrp.production'

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(MRP, self).onchange_product_id()
        if self.product_id and self.product_id.to_be_archived:
            return {
                'warning': {'title': 'Product Archived Warning', 'message': (f'Product(s) {self.product_id.name} '
                                                                             'is planned to be Archived. '
                                                                             ' Please select Continue to proceed or '
                                                                             'remove the product(s) before '
                                                                             'proceeding'), },
            }
        return res

    @api.model
    def create(self, vals_list):
        res = super(MRP, self).create(vals_list)
        prods = res.move_raw_ids.filtered(lambda l: l.product_id.to_be_archived)
        if prods:
            list_of_names = prods.mapped('name')
            products = list(set(list_of_names))
            products = ", ".join(products)
            message = f"""<p style="color:red;">Product(s) {products} is/are planned to be Archived. Please remove the product(s) before
            proceeding.</p> """
            res.message_post(
                body=message)
        if res.product_id and res.product_id.to_be_archived:
            message = f"""<p style="color:red;">Product {res.product_id.name} is planned to be Archived. Please change the product to be manufactured before
                        proceeding.</p> """
            res.message_post(
                body=message)

        return res

    def write(self, vals):
        og_vals = vals.copy()
        res = super(MRP, self).write(vals)
        product_ids = set()
        if 'move_raw_ids' in og_vals:
            for prod_line in og_vals['move_raw_ids']:
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

        if 'product_id' in og_vals:
            product = self.env['product.product'].browse(og_vals['product_id'])
            if product.to_be_archived:
                message = f"""<p style="color:red;">Product {product.name} is planned to be Archived. Please change the product to be manufactured before
                                        proceeding.</p> """
                self.message_post(
                    body=message)

        return res


    # def copy(self, default=None):
    #     res = super(MRP, self).copy(default)
    #     prods = self.move_raw_ids.filtered(lambda l: l.product_id.to_be_archived)
    #     if prods:
    #         list_of_names = prods.mapped('name')
    #         products = ", ".join(list_of_names)
    #         message = f"""<p style="color:red;">Product(s) {products} is/are planned to be Archived. Please remove the product(s) before
    # proceeding.</p> """
    #         res.message_post(
    #             body=message)
    #     return res


class Transfers(models.Model):
    _inherit = 'stock.picking'

    # def copy(self, default=None):
    #     res = super(Transfers, self).copy(default)
    #     prods = self.move_ids_without_package.filtered(lambda l: l.product_id.to_be_archived)
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
        res = super(Transfers, self).create(vals_list)
        prods = res.move_ids_without_package.filtered(lambda l: l.product_id.to_be_archived)
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
        res = super(Transfers, self).write(vals)
        product_ids = set()
        if 'move_ids_without_package' in og_vals:
            for prod_line in og_vals['move_ids_without_package']:
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
