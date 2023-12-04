from odoo import api, fields, models, _


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    @api.model
    def create(self, vals):
        res = super(StockScrap, self).create(vals)
        moves = self.env['stock.move'].search([('product_id', '=', res.product_id.id),
                                              ('raw_material_production_id', '=', res.production_id.id)])
        for move in moves:
            if res.production_id.picking_type_id.sequence_code == 'MO' and res.production_id.picking_type_id.code == 'mrp_operation':
                move._action_update_picking()
        return res

    def do_scrap(self):
        self._check_company()
        for scrap in self:
            scrap.name = self.env['ir.sequence'].next_by_code('stock.scrap') or _('New')
            move = self.env['stock.move'].with_context(from_mrp=1).create(scrap._prepare_move_values())
            # master: replace context by cancel_backorder
            move.with_context(is_scrap=True)._action_done()
            scrap.write({'move_id': move.id, 'state': 'done'})
            scrap.date_done = fields.Datetime.now()
        return True
