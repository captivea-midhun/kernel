# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.http_routing.models.ir_http import slugify


class ProductTemplateTag(models.Model):
    _name = "product.template.tag"
    _description = "Product Tag"

    name = fields.Char(string="Name", required=True, translate=True)
    color = fields.Integer(string="Color Index")
    product_tmpl_ids = fields.Many2many(
        comodel_name="product.template",
        string="Products",
        relation="product_template_product_tag_rel",
        column1="tag_id",
        column2="product_tmpl_id",
    )
    products_count = fields.Integer(
        string="# of Products", compute="_compute_products_count", store=True
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    code = fields.Char(
        string="Code",
        compute="_compute_code",
        readonly=False,
        inverse="_inverse_code",
        store=True,
    )

    _sql_constraints = [
        ("code_uniq", "unique(code)",
         "Product template tag code already exists",)
    ]

    @api.depends("name", "code")
    def _compute_code(self):
        for rec in self:
            if rec.name and rec.name.strip():
                rec.code = slugify(rec.name)
            else:
                rec.code = ""

    def _inverse_code(self):
        for rec in self:
            rec.code = slugify(rec.code)

    @api.depends("product_tmpl_ids")
    def _compute_products_count(self):
        for rec in self:
            rec.products_count = len(rec.product_tmpl_ids)
