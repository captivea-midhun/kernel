from odoo import fields, models, api


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    use_in_mps = fields.Boolean("Use In Master Production Schedule", default=True)
    default_warehouse_mps = fields.Boolean("Is Default MPS Warehouse?",
                                           help='Select if you want to set this warehouse as default when MPS is created automatically.',
                                           default=False)

    @api.model
    def create(self, vals_list):
        """
        Author : Raumil Dhandhukia (Setu Consulting Services Private Ltd.)
        Purpose : Set default warehouse.
        Date : 1st Nov 2021
        """
        res = super(StockWarehouse, self).create(vals_list)
        if res and res.use_for_mps:
            warehouse = self.search([('id', '!=', res.id), ('default_warehouse_mps', '=', True)])
            if warehouse:
                warehouse.default_warehouse_mps = False
        return res

    def write(self, vals):
        """
       Author : Raumil Dhandhukia (Setu Consulting Services Private Ltd.)
       Purpose : Set default warehouse.
       Date : 1st Nov 2021
       """
        res = super(StockWarehouse, self).write(vals)
        if 'default_warehouse_mps' in vals.keys() and vals['default_warehouse_mps']:
            warehouse = self.search([('id', '!=', self.id), ('default_warehouse_mps', '=', True)])
            if warehouse:
                warehouse.default_warehouse_mps = False
        return res
