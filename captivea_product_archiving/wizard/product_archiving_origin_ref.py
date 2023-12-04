from odoo import models, fields


class ProductArchivingOriginRef(models.TransientModel):
    _name = 'product.archiving.origin.ref'
    _description = 'Product Archiving Wizard'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    picking_id = fields.Many2one("stock.picking", string='Picking')
    production_id = fields.Many2one('mrp.production', string='Manufacturing Order')
    # ref_link = fields.Html(string='Ref')
    location_id = fields.Many2one("stock.location", string='Location')
    po_id = fields.Many2one('purchase.order', string='Purchase Order')
    Quantity = fields.Float(string="Quantity")

    archiving_product_order_ref = fields.Many2one('captivea.product.archiving.wizard', string='sale order ref')
    archiving_product_picking_ref = fields.Many2one('captivea.product.archiving.wizard', string='picking ref')
    archiving_product_production_ref = fields.Many2one('captivea.product.archiving.wizard', string='production ref')
    archiving_product_location_ref = fields.Many2one('captivea.product.archiving.wizard', string='location ref')
    archiving_product_purchase_ref = fields.Many2one('captivea.product.archiving.wizard', string='Purchase ref')

    wizard_ref = fields.Many2one('captivea.product.archiving.wizard', string='sale order ref')

    def open_line(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        order = False
        order_model = False
        if self._context.get("from_sale_order", False):
            order = self.sale_order_id.id
            order_model = self.sale_order_id._name

        elif self._context.get('from_purchase_order', False):
            order = self.po_id.id
            order_model = self.po_id._name

        elif self._context.get("from_picking", False):
            order = self.picking_id.id
            order_model = self.picking_id._name

        elif self._context.get("from_production", False):
            order = self.production_id.id
            order_model = self.production_id._name

        elif self._context.get("from_stock", False):
            order = self.production_id.id
            order_model = self.production_id._name

        if order and order_model:
            record_url = base_url + "/web#id=" + str(order) + "&view_type=form&model=" + str(order_model)
            return {
                'type': 'ir.actions.act_url',
                'name': self._context.get('model_name'),
                'target': 'new',
                'url': record_url
            }
        return True
