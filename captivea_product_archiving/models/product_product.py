from odoo import fields, models, api
from datetime import timedelta, date


class ProductProduct(models.Model):
    _inherit = 'product.product'

    to_be_archived = fields.Boolean(string="To Be Archived", default=False)

    def archive_check(self):
        archiving_wizard = self.env['captivea.product.archiving.wizard'].create({})
        self._cr.execute("""
                    select
                        sm.id
                    from
                        stock_move sm
                        LEFT JOIN stock_location l on l.id=sm.location_id
                        LEFT JOIN stock_warehouse wh ON l.parent_path like concat('%/', wh.view_location_id, '/%')
                    where
                        product_id = {}
                        --and state in ('partially_available', 'assigned')
                        and sm.state not in ('done','cancel')
                        and (l.usage = 'internal' AND wh.id IS NOT NULL) OR l.usage = 'transit'
                    """.format(self.id))
        move_ids = [a[0] for a in self._cr.fetchall()]
        stock_move = self.env['stock.move'].browse(move_ids)

        for move in stock_move:
            self.env['product.archiving.origin.ref'].create({
                'archiving_product_picking_ref': move.picking_id and archiving_wizard.id or False,
                'archiving_product_production_ref': move.raw_material_production_id and archiving_wizard.id or False,
                'production_id': move.raw_material_production_id.id,
                'picking_id': move.picking_id.id
            })

        self._cr.execute("""
                            select
                                mo.id
                            from
                                mrp_production mo
                            where
                                product_id = {}
                                and mo.state not in ('done','cancel')
                            """.format(self.id))
        mo_ids = [a[0] for a in self._cr.fetchall()]
        mo_ids = self.env['mrp.production'].browse(mo_ids)

        for move in mo_ids:
            self.env['product.archiving.origin.ref'].create({
                'archiving_product_production_ref': archiving_wizard.id,
                'production_id': move.id,
            })

        self._cr.execute("""select
                                sq.id
                            from
                                stock_quant sq
                                LEFT JOIN stock_location l on l.id=sq.location_id
                                LEFT JOIN stock_warehouse wh ON l.parent_path like concat('%/', wh.view_location_id, '/%')
                            where
                                sq.product_id = {}
                                and sq.quantity > 0
                                and (l.usage = 'internal' AND wh.id IS NOT NULL) OR l.usage = 'transit'
                                """.format(self.id))
        quant_ids = [a[0] for a in self._cr.fetchall()]
        quant_ids = self.env['stock.quant'].browse(quant_ids)
        for quant in quant_ids:
            self.env['product.archiving.origin.ref'].create({
                'archiving_product_location_ref': archiving_wizard.id,
                'location_id': quant.location_id.id,
                'Quantity': quant.quantity
            })

        # self._cr.execute("""select
        #                         so.id
        #                     from
        #                         sale_order_line sol
        #                         join sale_order so on so.id = sol.order_id
        #                     where
        #                         product_id = {}
        #                         and so.state not in ('done','cancel')""".format(self.id))

        self._cr.execute("""    select distinct id from (

                                            select
                                                so.id
                                            from
                                                sale_order_line sol
                                                inner join sale_order so on sol.order_id = so.id

                                            where sol.product_id = {0} and so.state in ('draft','sent')

                                            union all

                                            select
                                                so.id
                                            from
                                                sale_order_line sol
                                                inner join sale_order so on sol.order_id = so.id
                                                inner join stock_move sm on sm.sale_line_id = sol.id 
                                            where

                                                sol.product_id = {0} and
                                                sm.state not in ('done','cancel') and so.state != 'cancel'
                                                or (sol.product_id = {0} and so.state != 'cancel' and sm.state = 'done' and so.invoice_status != 'invoiced')

                                            union all

                                            select
                                                so.id
                                            from
                                                sale_order_line sol
                                                inner join sale_order so on sol.order_id = so.id
                                                inner join sale_order_line_invoice_rel rel on rel.order_line_id = sol.id
                                                inner join account_move_line aml on aml.id = rel.invoice_line_id
												inner join account_move am on aml.move_id = am.id
                                            where
                                                sol.product_id = {0}
                                                and am.state not in ('posted','cancel')
                                                and so.state != 'cancel'

                                            )as po_ids;
                                            """.format(self.id))


        sale_order = [a[0] for a in self._cr.fetchall()]
        sale_order = self.env['sale.order'].browse(sale_order)
        for order in sale_order:
            self.env['product.archiving.origin.ref'].create({
                'archiving_product_order_ref': archiving_wizard.id,
                'sale_order_id': order.id
            })

        self._cr.execute("""    select distinct id from (
                                    
                                    select
                                        pol.id
                                    from
                                        purchase_order_line pol
                                        inner join purchase_order po on pol.order_id = po.id
                                        
                                    where pol.product_id = {0} and po.state in ('draft','sent','to approve')
                                    
                                    union all
                                    
                                    select
                                        pol.id
                                    from
                                        purchase_order_line pol
                                        inner join purchase_order po on pol.order_id = po.id
                                        inner join stock_move sm on sm.purchase_line_id = pol.id
                                    where
                                        
                                        pol.product_id = {0} and po.state != 'cancel' and
                                        sm.state not in ('done','cancel')
                                        or (pol.product_id = {0} and sm.state = 'done' and po.invoice_status != 'invoiced' and po.state != 'cancel')
                                        
                                    union all
                                    
                                    select
                                        pol.id
                                    from
                                        purchase_order_line pol
                                        inner join purchase_order po on pol.order_id = po.id
                                        inner join account_move_line aml on aml.purchase_line_id = pol.id
                                        inner join account_move am on aml.move_id = am.id
                                    where
                                        pol.product_id = {0} and po.state != 'cancel'
                                        and am.state not in ('posted','cancel')
                                        
                                    )as po_ids;
                                    """.format(self.id))
        po_ids = [a[0] for a in self._cr.fetchall()]
        po_ids = self.env['purchase.order.line'].browse(po_ids)

        for line in po_ids:
            self.env['product.archiving.origin.ref'].create({
                'archiving_product_purchase_ref': archiving_wizard.id,
                'po_id': line.order_id.id,
                'Quantity': line.product_qty
            })



        msg = ''
        if archiving_wizard.sale_order_ids or archiving_wizard.picking_ids or archiving_wizard.manufacturing_order_ids or archiving_wizard.po_line_ids or archiving_wizard.location_ids:
            msg = """The product has inventory or is currently reserved/used on a document.  We recommend to process 
            all transactions and zero out the inventory before Archiving the product.  Please refer to the list below 
            for more details.  Would you like to continue archiving the product? """


        messages = """<p style='color:red;'><b>{}</b>
                            </p>""".format(msg or "<p style='color:black;'>The product can be Archived. Please select Archive to proceed.<p/>")
        archiving_wizard.msg_label = messages
        
        wizard_form = self.env.ref('captivea_product_archiving.view_captivea_product_archiving_wizard', False)
        return {
            'name': 'Captivea Product Archiving Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'captivea.product.archiving.wizard',
            'res_id': archiving_wizard.id,
            'view_id': wizard_form.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new'
        }

    def create_activity_for_product_archiving(self):
        activity_obj = self.env['mail.activity']
        user_id = self.env['ir.config_parameter'].get_param('captivea_product_archiving.archiving_product_activity_user')
        activity_after_x_days = self.env['ir.config_parameter'].get_param('captivea_product_archiving.activity_after_x_days')
        if not user_id:
            user_id = self.env.ref('base.user_admin').id
        for product_id in self:
            product_archive_message = self.env['ir.config_parameter'].get_param('captivea_product_archiving.activity_message_for_archiving')
            activity = activity_obj.search([('res_id', '=', product_id.id),
                                 ('user_id', '=', int(user_id)),
                                 ('summary', '=', product_archive_message or "Please archive {}".format(product_id.name))])
            if not activity:
                activity_data = {
                    'res_id': product_id.id,
                    'res_model_id': self.env['ir.model']._get(product_id._name).id,
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'summary': product_archive_message or "Please archive {}".format(product_id.name),
                    'date_deadline': date.today() + timedelta(days=int(activity_after_x_days)),
                    'user_id': int(user_id),
                }
                activity_obj.create(activity_data)
        return True

    @api.model
    def check_stock_and_create_activity_archiving_product(self):
        product_ids = self.search([('to_be_archived', '=', True)])
        product_ids.create_activity_for_product_archiving()
        return True

    def action_archive(self):
        self.write({'to_be_archived': False})
        return super(ProductProduct, self).action_archive()
