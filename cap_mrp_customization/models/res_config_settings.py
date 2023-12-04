from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mo_consumable_prod_account_id = fields.Many2one('account.account', string="Consumable Product Account",
                                                    config_parameter='cap_mrp_customization.default_mo_consumable_prod_account_id')
    mo_inv_adj_account_id = fields.Many2one('account.account', string="Inventory Adjustment Product Account",
                                                    config_parameter='cap_mrp_customization.default_mo_inv_adj_account_id')