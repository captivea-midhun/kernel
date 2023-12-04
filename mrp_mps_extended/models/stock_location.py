from odoo import fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    use_in_mps = fields.Boolean("Use In Master Production Schedule", default=True)
