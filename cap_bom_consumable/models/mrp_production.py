
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, Warning
from collections import defaultdict
from datetime import datetime


class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    
    def button_mark_done(self):
        self.ensure_one()
        res = super(MrpProduction, self).button_mark_done()
        consumable_product_lines = self.move_raw_ids.filtered(lambda mrw: mrw.product_id.type == 'consu')
        stock_valuation = self.env['stock.valuation.layer'].sudo()
        stock_valuation_search = stock_valuation.search([('stock_move_id','in',consumable_product_lines.ids)])
        mo_consumable_prod_account_id = self.env['ir.config_parameter'].sudo() \
            .get_param('cap_bom_consumable.default_mo_consumable_prod_account_id')
        mo_inv_adj_account_id = self.env['ir.config_parameter'].sudo() \
            .get_param('cap_bom_consumable.default_mo_inv_adj_account_id')
        for stv in stock_valuation_search:
            unit_cost = stv.unit_cost * abs(stv.quantity)
            print ("stv --->>", stv)
            print ("stv.unit_cost --->>", stv.unit_cost)
            print ("stv.quantity --->>", stv.quantity)
            print ("unit_cost --->>", unit_cost)
            account_move_vals = {
                            'ref': self.name + ' - ' + stv.product_id.name,
                            'production_id': self.id,
                            'journal_id': self.env['account.journal'].search([('name','ilike','Inventory Valuation')], limit=1).id,
                            'date': datetime.now().date(),
                            'line_ids': [(0, 0, {
                                                'name': self.name + ' - ' + stv.product_id.name,
                                                'amount_currency': 0.0,
                                                'currency_id': None,
                                                'debit': unit_cost,
                                                'credit': 0.0,
                                                'date_maturity': None,
                                                'partner_id': None,
                                                'account_id': int(mo_consumable_prod_account_id),
                                                'payment_id': None,
                                            }),
                                            (0, 0, {
                                                'name': self.name + ' - ' + stv.product_id.name,
                                                'amount_currency': 0.0,
                                                'currency_id': None,
                                                'debit': 0.0,
                                                'credit': unit_cost, #unit_cost > 0.0 and unit_cost or 0.0,
                                                'date_maturity': None,
                                                'partner_id': None,
                                                'account_id': int(mo_inv_adj_account_id),
                                                'payment_id': None,
                                            })]
                            }
            print ("account_move_vals --->>", account_move_vals)
            account_move = self.env['account.move'].sudo().create(account_move_vals)
            account_move.action_post()
            stv.account_move_id = account_move.id
        return res