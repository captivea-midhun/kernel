from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    consumed_as_needed = fields.Boolean("Consumed As Needed", tracking=True, index=True, copy=False,
                                        help="Select if the product will be kept in the Pre-Production Inventory "
                                             "Location only")
