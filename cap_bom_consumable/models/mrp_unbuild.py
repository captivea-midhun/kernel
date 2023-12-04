

from odoo import models, fields, api, _
from datetime import datetime


class MrpUnbuild(models.Model):
    
    _inherit = "mrp.unbuild"
    
    def action_unbuild(self):
        self.ensure_one()
        res = super(MrpUnbuild, self).action_unbuild()
        if self.mo_id:
            bom_product_ids = self.bom_id.bom_line_ids.filtered(lambda bomp: bomp.product_id.type == 'consu')
            bom_components_dict = {}
            for prod in bom_product_ids:
                bom_components_dict.update({prod.product_id:prod.product_qty})
            consumable_product_lines = self.mo_id.move_raw_ids.filtered(lambda mrw: mrw.product_id.type == 'consu')
            stock_valuation = self.env['stock.valuation.layer'].sudo()
            stock_valuation_search = stock_valuation.search([('stock_move_id','in',consumable_product_lines.ids), ('account_move_id','!=',None)])
            mo_consumable_prod_account_id = self.env['ir.config_parameter'].sudo() \
                .get_param('cap_bom_consumable.default_mo_consumable_prod_account_id')
            mo_inv_adj_account_id = self.env['ir.config_parameter'].sudo() \
                .get_param('cap_bom_consumable.default_mo_inv_adj_account_id')
            for stv in stock_valuation_search:
                if stv.product_id in bom_components_dict:
                    unit_cost = stv.unit_cost * self.product_qty * bom_components_dict[stv.product_id]
                # unit_cost = stv.unit_cost * abs(stv.quantity)
                account_move_vals = {
                                'ref': self.name + ' - ' + stv.product_id.name,
                                'production_id': self.mo_id.id,
                                'journal_id': self.env['account.journal'].search([('name','ilike','Inventory Valuation')], limit=1).id,
                                'date': datetime.now().date(),
                                'line_ids': [(0, 0, {
                                                    'name': self.name + ' - ' + stv.product_id.name,
                                                    'amount_currency': 0.0,
                                                    'currency_id': None,
                                                    'debit': 0.0,
                                                    'credit': unit_cost, #unit_cost > 0.0 and unit_cost or 0.0,
                                                    'date_maturity': None,
                                                    'partner_id': None,
                                                    'account_id': int(mo_consumable_prod_account_id),
                                                    'payment_id': None,
                                                }),
                                                (0, 0, {
                                                    'name': self.name + ' - ' + stv.product_id.name,
                                                    'amount_currency': 0.0,
                                                    'currency_id': None,
                                                    'debit': unit_cost,
                                                    'credit': 0.0,
                                                    'date_maturity': None,
                                                    'partner_id': None,
                                                    'account_id': int(mo_inv_adj_account_id),
                                                    'payment_id': None,
                                                })]
                                }
                account_move = self.env['account.move'].sudo().create(account_move_vals)
                account_move.action_post()
        return res