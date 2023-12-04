

from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    hide_po = fields.Boolean(string="Hide From Clearing Report", help="Check this field to hide the PO from the Purchase Clearing Account Report", stored=True, tracking=True)

