# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    scrapped_return = fields.Boolean('Scrapped Return')

    def write(self, vals):
        """
        Log notes for change of product or quantity in MO edit function.
        """
        content1 = ""
        content2 = ""
        raw_material_production_id = self.raw_material_production_id
        new_product_id = vals.get("product_id", False)
        if new_product_id:
            new_product_rec = self.env['product.product'].browse(new_product_id)

        # Product name changed content
        if vals.get("product_id"):
            if self.product_id != new_product_rec and raw_material_production_id and new_product_id:
                content1 = "  \u2022 Product: " + \
                           self.product_id.name + " \u2794 " + \
                           new_product_rec.name + "<br/>"

        # Product qty changed content
        if vals.get("product_uom_qty"):
            if self.product_uom_qty != vals.get(
                    "product_uom_qty") and raw_material_production_id and new_product_id:
                content2 = "  \u2022 " + new_product_rec.name + \
                           "<br/>" + "To Consume: " + str(self.product_uom_qty) + \
                           " \u2794 " + str(vals.get("product_uom_qty")) + "<br/>"
        if content1 or content2:
            raw_material_production_id.message_post(body=content1 + content2)
        return super(StockMove, self).write(vals)


class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    def process(self):
        res = super(StockImmediateTransfer, self).process()
        # Code to create logs after receiving the purchase order.
        purchase_id = self.pick_ids.purchase_id
        if purchase_id:
            purchase_order = self.env['purchase.order'].search([('id', '=', purchase_id.id)])
            content1 = """ <div style="font-family: 'Lucica Grande', Ubuntu, Arial,
                            Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34);
                            background-color: rgb(255, 255, 255);">""" + \
                       """<p>Items for PO: <b>%s</b></p><br/>""" % purchase_order.name + \
                       """<p>Vendor: <b>%s</b></p>""" % purchase_order.partner_id.name
            content2 = """<table width = "100%" style="color: #454748; font-size: 12px;">
                            <tr><th width="25%">Product</th>
                                <th width="25%">Description</th>
                                <th width="20%">SKU</th>
                                <th width="10%">Quantity</th>
                                <th width="10%">Received Quantity</th>
                                </tr><br/>"""
            for po_line in purchase_order.order_line:
                if po_line.product_id:
                    content2 += """<tr><td>%s</td>""" % po_line.product_id.name + \
                                """<td>%s</td>""" % po_line.name + \
                                """<td>%s</td>""" % po_line.product_id.default_code + \
                                """<td>%s</td>""" % po_line.product_qty + \
                                """<td>%s</td>""" % po_line.qty_received
            content3 = """</tr><br/></table><br/></div>"""
            purchase_order.message_post(body=content1 + content2 + content3)
        return res
