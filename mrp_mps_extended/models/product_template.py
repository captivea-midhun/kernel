from odoo import fields, models, api


class ProPro(models.Model):
    _inherit = 'product.product'

    mps_tmp_seq = fields.Integer()
    mps_tmp_level = fields.Char()

    def add_chatter(self):
        """
        Author : Udit Ramani (Setu Consulting Services Private Ltd.)
        Purpose : Added this method to add a log that Product has been removed from MPS.
        Date : 29th Oct 2021
        """
        self.env['mail.message'].create({
            'subject': 'Product Removed from MPS',
            'model': 'product.product',
            'res_id': self.id,
            'body': f"""
                            <div style="margin-left:30px;margin-top:10px;">
                                &bull; <strong style="color:red;">{self.display_name}</strong> has been removed from MPS.
                            </div>
                            """,
            'author_id': self.env.user.partner_id.id
        })

    def add_to_mps(self):
        """
        Author : Udit Ramani (Setu Consulting Services Private Ltd.)
        Purpose : Added this method to create MPS records.
        Date : 29th Oct 2021
        """
        mps = self.env['mrp.production.schedule']
        if not mps.search([('product_id', '=', self.id), ('company_id', '=', self.env.company.id)]):
            mps_id = mps.create({
                'product_id': self.id,
                'company_id': self.env.company.id
            })
            warehouse_id = self.env['stock.warehouse'].search([('default_warehouse_mps', '=', True)])
            if warehouse_id and len(warehouse_id) == 1:
                mps_id.warehouse_id = warehouse_id

    # @api.model
    # def create(self, vals):
    #     """
    #     Author : Udit Ramani (Setu Consulting Services Private Ltd.)
    #     Purpose : Directly add products to MPS once it will be created.
    #     Date : 29th Oct 2021
    #     """
    #     pro = super(ProPro, self).create(vals)
    #     if pro and pro.type == 'product':
    #         pro.use_in_mps = True
    #         pro.add_to_mps()
    #     return pro

    def write(self, vals):
        """
        Author : Udit Ramani (Setu Consulting Services Private Ltd.)
        Purpose : Auto remove product from MPS.
        Date : 29th Oct 2021
        """
        res = super(ProPro, self).write(vals)
        if res and 'use_in_mps' in vals.keys():
            if vals['use_in_mps'] and self.env.context.get('mps_is_created_from_screen') != 'yes':
                self.add_to_mps()
            if not vals['use_in_mps']:
                mps = self.env['mrp.production.schedule'].search([('product_id', '=', self.id)])
                if self.env.context.get('mps_is_deleted_from_screen') != 'yes':
                    if mps:
                        mps.unlink()
                        self.add_chatter()

                else:
                    self.add_chatter()

        if res and 'active' in vals.keys():
            if not vals['active']:
                mps = self.env['mrp.production.schedule'].search([('product_id', '=', self.id)])
                if mps:
                    mps.with_context(do_not_set_use_in_mps_to_false=True).unlink()
                    self.add_chatter()
                    self.use_in_mps = False
        return res


class ProTem(models.Model):
    _inherit = 'product.template'

    minimum_qty = fields.Float('Minimum Quantity', help='Minimum Quantity to order or manufacture generated in MPS',
                               tracking=True)
    multiple_qty = fields.Float('Multiple Quantity', help='Multiple quantity for POs and MOs generated in MPS',
                                tracking=True)
    use_in_mps = fields.Boolean(string="Use in MPS", help="Select if the product needs to be added to MPS")

    mps_tmp_seq = fields.Integer()
    mps_tmp_level = fields.Char()

    def add_chatter(self):
        """
        Author : Udit Ramani (Setu Consulting Services Private Ltd.)
        Purpose : Added this method to add a log that Product has been removed from MPS.
        Date : 29th Oct 2021
        """
        self.env['mail.message'].create({
            'subject': 'Product Removed from MPS',
            'model': 'product.template',
            'res_id': self.id,
            'body': f"""
                               <div style="margin-left:30px;margin-top:10px;">
                                   &bull; <strong style="color:red;">{self.display_name}</strong> has been removed from MPS.
                               </div>
                               """,
            'author_id': self.env.user.partner_id.id
        })

    def add_to_mps(self):
        """
        Author : Udit Ramani (Setu Consulting Services Private Ltd.)
        Purpose : Added this method to create MPS records.
        Date : 29th Oct 2021
        """
        mps = self.env['mrp.production.schedule']
        products = self.env['product.product'].search([('product_tmpl_id', '=', self.id)])
        warehouse_id = self.env['stock.warehouse'].search([('default_warehouse_mps', '=', True)])
        for product_id in products:
            if not mps.search([('product_id', '=', product_id.id), ('company_id', '=', self.env.company.id)]):
                mps_id = mps.create({
                    'product_id': product_id.id,
                    'company_id': self.env.company.id
                })
                if warehouse_id and len(warehouse_id) == 1:
                    mps_id.warehouse_id = warehouse_id

    @api.model
    # def create(self, vals):
    #     """
    #     Author : Udit Ramani (Setu Consulting Services Private Ltd.)
    #     Purpose : Directly add products to MPS once it will be created.
    #     Date : 29th Oct 2021
    #     """
    #     pro = super(ProTem, self).create(vals)
    #     if pro and pro.type == 'product':
    #         pro.use_in_mps = True
    #         pro.add_to_mps()
    #     return pro

    def write(self, vals):
        """
        Author : Udit Ramani (Setu Consulting Services Private Ltd.)
        Purpose : Auto remove product from MPS.
        Date : 29th Oct 2021
        """
        res = super(ProTem, self).write(vals)
        products = self.env['product.product'].search([('product_tmpl_id', '=', self.id)])
        products = products.ids if products else []
        if res and 'use_in_mps' in vals.keys():
            if vals['use_in_mps'] and self.env.context.get('mps_is_created_from_screen') != 'yes':
                self.add_to_mps()
            if not vals['use_in_mps']:
                mps = self.env['mrp.production.schedule'].search(
                    ['|', ('product_tmpl_id', '=', self.id), ('product_id', 'in', products)])
                if self.env.context.get('mps_is_deleted_from_screen') != 'yes':
                    if mps:
                        mps.unlink()
                        self.add_chatter()
                        children = self.env['product.product'].search([('product_tmpl_id', '=', self.id)])
                        if children:
                            children.add_chatter()
                else:
                    self.add_chatter()
        if res and 'active' in vals.keys():
            if not vals['active']:
                mps = self.env['mrp.production.schedule'].search(
                    ['|', ('product_tmpl_id', '=', self.id), ('product_id', 'in', products)])
                if mps:
                    mps.unlink()
                    self.add_chatter()
                self.use_in_mps = False
        return res
