from odoo import models, fields


class CaptiveaProductArchivingWizard(models.TransientModel):
    _name = 'captivea.product.archiving.wizard'
    _description = 'Captivea Product Archiving Wizard'

    sale_order_ids = fields.One2many('product.archiving.origin.ref', 'archiving_product_order_ref', string='Sale Order')
    picking_ids = fields.One2many('product.archiving.origin.ref', 'archiving_product_picking_ref', string="Pickings")
    manufacturing_order_ids = fields.One2many('product.archiving.origin.ref', 'archiving_product_production_ref', string="Manufacturing Order")
    po_line_ids = fields.One2many('product.archiving.origin.ref','archiving_product_purchase_ref', string='PO Lines')
    location_ids = fields.One2many('product.archiving.origin.ref', 'archiving_product_location_ref', string='Product in Stock')

    msg_label = fields.Html(string="Messages")

    def conform_arching_product(self):
        product = self._context.get('active_id')
        product_id = self.env['product.product'].browse(product)
        product_id.write({'to_be_archived': True})
        if product_id.qty_available <= 0:
            product_id.create_activity_for_product_archiving()
        return True
