from odoo import models, fields, api
from odoo.tests import Form
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_round, float_is_zero



class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.onchange('product_id')
    def onchange_product(self):
        moves = self.raw_material_production_id.move_raw_ids - self
        if self.product_id.id in moves.mapped('product_id').ids:
            raise UserError("You cannot add the same component on the MO, "
                            "please update the quantity of the existing component on the MO")

    @api.model
    def create(self, vals):
        exist_lines = self.env['mrp.production'].browse(vals.get('raw_material_production_id')).move_raw_ids
        # if vals.get('raw_material_production_id') and \
        #         vals.get('product_id') in exist_lines.mapped('product_id').ids \
        #         and 'cancel_backorder' not in self._context:
        #     raise UserError("You cannot add the same component on the MO, "
        #                     "please update the quantity of the existing component on the MO")
        res = super(StockMove, self).create(vals)
        if res.raw_material_production_id and res.raw_material_production_id.state == 'confirmed' and not self.env.context.get(
                'from_mrp') and res.raw_material_production_id.picking_type_id.sequence_code == 'MO' and res.raw_material_production_id.picking_type_id.code == 'mrp_operation':
            res.with_context(create_new=1)._action_update_picking()
        return res

    def write(self, vals):
        res = super(StockMove, self).write(vals)
        # activity = self.picking_id.activity_ids.filtered(lambda x:
        #                                                  x.activity_type_id.name == 'To Do' and
        #                                                  x.summary == 'The MO quantity has changed, please review the order and make sure all components have been addressed')
        # if self.picking_id and vals.get('state') == 'done' and activity:
        #     activity.action_done()
        for rec in self:
            if rec.raw_material_production_id and rec.raw_material_production_id.state == 'confirmed' and self.env.context.get(
                    'from_mrp') and rec.raw_material_production_id.picking_type_id.sequence_code == 'MO' and rec.raw_material_production_id.picking_type_id.code == 'mrp_operation':
                rec._action_update_picking()
        return res

    def _action_update_picking(self):
        if not self.product_id.consumed_as_needed:
            picking_type = self.env['stock.picking.type'].search([('sequence_code', '=', 'PC')], limit=1)
            to_consume = self.product_uom_qty
            TNQ = to_consume + sum(
                self.raw_material_production_id.scrap_ids.filtered(lambda x: x.product_id == self.product_id).mapped(
                    'scrap_qty'))
            done_pickings = self.raw_material_production_id.picking_ids.filtered(
                lambda x: x.state == 'done' and
                          x.picking_type_id == picking_type and
                          x.location_id == picking_type.default_location_src_id)
            TTQ = sum(done_pickings.move_ids_without_package.filtered(lambda x: x.product_id == self.product_id).mapped(
                'quantity_done'))
            open_pickings = self.raw_material_production_id.picking_ids.filtered(
                lambda x: x.state not in ['done', 'cancel'] and
                          x.picking_type_id == picking_type and
                          x.location_id == picking_type.default_location_src_id)
            TOQ = sum(open_pickings.move_ids_without_package.filtered(lambda x: x.product_id == self.product_id).mapped(
                'product_uom_qty'))
            return_pickings = self.raw_material_production_id.picking_ids.filtered(
                lambda x: x.state not in ['cancel'] and
                          x.picking_type_id == picking_type and
                          x.location_id == picking_type.default_location_dest_id)
            TOTR = sum(return_pickings.move_ids_without_package.filtered(lambda x: x.product_id == self.product_id).mapped(
                'product_uom_qty'))

            if TNQ > (TTQ + TOQ - TOTR):
                r_move = return_pickings.filtered(
                    lambda x: x.state not in ('done', 'cancel')).move_ids_without_package.filtered(
                    lambda x: x.product_id == self.product_id)
                if r_move.product_uom_qty > (TNQ - TTQ - TOQ + TOTR):
                    r_move.write({'product_uom_qty': (TNQ - TTQ - TOQ + TOTR)})
                else:
                    r_picking = r_move.picking_id
                    r_move.write({'state': 'draft'})
                    r_move.unlink()
                    if not r_picking.move_ids_without_package:
                        r_picking.unlink()
                return_pickings = self.raw_material_production_id.picking_ids.filtered(
                    lambda x: x.state not in ['cancel'] and
                              x.picking_type_id == picking_type and
                              x.location_id == picking_type.default_location_dest_id)
                TOTR = sum(
                    return_pickings.move_ids_without_package.filtered(lambda x: x.product_id == self.product_id).mapped(
                        'product_uom_qty'))
                self.env.cr.commit()
                if open_pickings:
                    move = open_pickings.move_ids_without_package.filtered(lambda x: x.product_id == self.product_id)
                    if move:
                        move.write({'product_uom_qty': move.product_uom_qty + (TNQ - TTQ - TOQ + TOTR)})
                    else:
                        if (TNQ - TTQ - TOQ + TOTR) > 0:
                            rec = self.create({
                                'product_id': self.product_id.id,
                                'product_uom_qty': (TNQ - TTQ - TOQ + TOTR),
                                'product_uom': self.product_uom.id,
                                'name': self.raw_material_production_id.name,
                                'date': self.raw_material_production_id.date_planned_start,
                                'date_expected': self.raw_material_production_id.date_planned_finished,
                                'picking_type_id': open_pickings.picking_type_id.id,
                                'location_id': picking_type.default_location_src_id.id,
                                'location_dest_id': picking_type.default_location_dest_id.id,
                                'company_id': self.company_id.id,
                                'picking_id': open_pickings.id,
                                'warehouse_id': self.location_dest_id.get_warehouse().id,
                                'origin': self.raw_material_production_id.name,
                                'group_id': self.raw_material_production_id.procurement_group_id.id,
                            })
                            self.move_orig_ids = [(4, rec.id)]
                            rec._action_confirm()
                            self.env.cr.commit()
                else:
                    if (TNQ - TTQ - TOQ + TOTR) > 0:
                        picking = self.env['stock.picking'].create({
                            'origin': self.raw_material_production_id.name,
                            'company_id': self.mapped('company_id').id,
                            'user_id': self.raw_material_production_id.user_id.id,
                            'group_id': self.group_id.id,
                            'move_type': self.mapped('group_id').move_type or 'direct',
                            'picking_type_id': picking_type.id,
                            'location_id': picking_type.default_location_src_id.id,
                            'location_dest_id': picking_type.default_location_dest_id.id,
                        })
                        rec = self.create({
                            'product_id': self.product_id.id,
                            'product_uom_qty': (TNQ - TTQ - TOQ + TOTR),
                            'product_uom': self.product_uom.id,
                            'name': self.raw_material_production_id.name,
                            'date': self.raw_material_production_id.date_planned_start,
                            'date_expected': self.raw_material_production_id.date_planned_finished,
                            'picking_type_id': picking.picking_type_id.id,
                            'location_id': picking_type.default_location_src_id.id,
                            'location_dest_id': picking_type.default_location_dest_id.id,
                            'company_id': self.company_id.id,
                            'picking_id': picking.id,
                            'warehouse_id': self.location_dest_id.get_warehouse().id,
                            'origin': self.raw_material_production_id.name,
                            'group_id': self.raw_material_production_id.procurement_group_id.id,
                        })
                        self.move_orig_ids = [(4, rec.id)]
                        picking.action_confirm()
                        self.env.cr.commit()
            elif TNQ < (TTQ + TOQ - TOTR):
                move = open_pickings.move_ids_without_package.filtered(lambda x: x.product_id == self.product_id)
                if abs(TTQ - (TNQ + TOTR)) == 0 and move:
                    m_picking = move.picking_id
                    move.write({'state': 'draft'})
                    move.unlink()
                    if not m_picking.move_ids_without_package:
                        m_picking.unlink()
                elif TTQ - (TNQ + TOTR) > 0:
                    if move:
                        m_picking = move.picking_id
                        move.write({'state': 'draft'})
                        move.unlink()
                        if not m_picking.move_ids_without_package:
                            m_picking.unlink()
                    moves = done_pickings.move_ids_without_package.filtered(lambda x: x.product_id == self.product_id)
                    r_qty = TTQ - (TNQ + TOTR)
                    for move in moves:
                        if move.product_uom_qty >= r_qty > 0:
                            reverse_order = self.raw_material_production_id.picking_ids.filtered(
                                lambda x: x.state not in ('done', 'cancel') and
                                          x.picking_type_id == picking_type and
                                          x.location_id == picking_type.default_location_dest_id and
                                          x.origin == 'Return of %s' % move.picking_id.name)
                            if reverse_order:
                                vals = {
                                    'product_id': move.product_id.id,
                                    'product_uom_qty': r_qty,
                                    'product_uom': move.product_uom.id,
                                    'date_expected': move.date_expected,
                                    'picking_type_id': move.picking_id.picking_type_id.id,
                                    'location_id': reverse_order[0].location_id.id,
                                    'location_dest_id': reverse_order[0].location_dest_id.id,
                                    'picking_id': reverse_order[0].id,
                                    'warehouse_id': move.location_dest_id.get_warehouse().id,
                                    'state': 'draft',
                                    'origin_returned_move_id': move.id,
                                    'procure_method': 'make_to_stock',
                                    'to_refund': True,
                                    'is_subcontract': False,
                                }
                                move.copy(vals)
                                reverse_order[0].do_unreserve()
                                reverse_order[0].action_confirm()
                                reverse_order[0].action_assign()
                                self.env.cr.commit()
                            else:
                                stock_return_picking_form = Form(
                                    self.env['stock.return.picking'].with_context(active_id=move.picking_id.id,
                                                                                  active_model='stock.picking'))
                                return_wizard = stock_return_picking_form.save()
                                r_wizard_line = return_wizard.product_return_moves.filtered(
                                    lambda x: x.product_id == move.product_id)
                                r_wizard_line.write({'quantity': r_qty})
                                return_wizard.product_return_moves.filtered(lambda x: x.id != r_wizard_line.id).unlink()
                                return_picking_id, pick_type_id = return_wizard._create_returns()
                                return_pick = self.env['stock.picking'].browse(return_picking_id)
                                for line in return_pick.move_line_ids_without_package:
                                    line.write({'qty_done': r_qty})
                                self.env.cr.commit()
                            r_qty = 0
                        elif move.product_uom_qty <= r_qty > 0:
                            reverse_order = self.raw_material_production_id.picking_ids.filtered(
                                lambda x: x.state not in ('done', 'cancel') and
                                          x.picking_type_id == picking_type and
                                          x.location_id == picking_type.default_location_dest_id and
                                          x.origin == 'Return of %s' % move.picking_id.name)
                            if reverse_order:
                                vals = {
                                    'product_id': move.product_id.id,
                                    'product_uom_qty': move.product_uom_qty,
                                    'product_uom': move.product_uom.id,
                                    'date_expected': move.date_expected,
                                    'picking_type_id': move.picking_id.picking_type_id.id,
                                    'location_id': reverse_order[0].location_id.id,
                                    'location_dest_id': reverse_order[0].location_dest_id.id,
                                    'picking_id': reverse_order[0].id,
                                    'warehouse_id': move.location_dest_id.get_warehouse().id,
                                    'state': 'draft',
                                    'origin_returned_move_id': move.id,
                                    'procure_method': 'make_to_stock',
                                    'to_refund': True,
                                    'is_subcontract': False,
                                }
                                move.copy(vals)
                                reverse_order[0].do_unreserve()
                                reverse_order[0].action_confirm()
                                reverse_order[0].action_assign()
                                self.env.cr.commit()
                            else:
                                stock_return_picking_form = Form(
                                    self.env['stock.return.picking'].with_context(active_id=move.picking_id.id,
                                                                                  active_model='stock.picking'))
                                return_wizard = stock_return_picking_form.save()
                                r_wizard_line = return_wizard.product_return_moves.filtered(
                                    lambda x: x.product_id == move.product_id)
                                r_wizard_line.with_context(from_mrp=1).write({'quantity': move.product_uom_qty})
                                return_wizard.product_return_moves.filtered(lambda x: x.id != r_wizard_line.id).unlink()
                                return_picking_id, pick_type_id = return_wizard._create_returns()
                                return_pick = self.env['stock.picking'].browse(return_picking_id)
                                for line in return_pick.move_line_ids_without_package:
                                    line.with_context(from_mrp=1).write({'qty_done': move.product_uom_qty})
                                self.env.cr.commit()
                            r_qty = r_qty - move.product_uom_qty
                else:
                    if move.product_uom_qty > abs(TTQ - (TNQ + TOTR)):
                        move.with_context(from_mrp=1).write({'product_uom_qty': abs(TTQ - (TNQ + TOTR))})
                    else:
                        moves = done_pickings.move_ids_without_package.filtered(lambda x: x.product_id == self.product_id)
                        r_qty = TTQ - (TNQ + TOTR)
                        for move in moves:
                            if move.product_uom_qty >= r_qty > 0:
                                reverse_order = self.raw_material_production_id.picking_ids.filtered(
                                    lambda x: x.state not in ('done', 'cancel') and
                                              x.picking_type_id == picking_type and
                                              x.location_id == picking_type.default_location_dest_id and
                                              x.origin == 'Return of %s' % move.picking_id.name)
                                if reverse_order:
                                    vals = {
                                        'product_id': move.product_id.id,
                                        'product_uom_qty': r_qty,
                                        'product_uom': move.product_uom.id,
                                        'date_expected': move.date_expected,
                                        'picking_type_id': move.picking_id.picking_type_id.id,
                                        'location_id': reverse_order[0].location_id.id,
                                        'location_dest_id': reverse_order[0].location_dest_id.id,
                                        'picking_id': reverse_order[0].id,
                                        'warehouse_id': move.location_dest_id.get_warehouse().id,
                                        'state': reverse_order[0].state,
                                        'origin_returned_move_id': move.id,
                                        'procure_method': 'make_to_stock',
                                        'to_refund': True,
                                        'is_subcontract': False,
                                    }
                                    move.copy(vals)
                                    reverse_order[0].do_unreserve()
                                    reverse_order[0].action_confirm()
                                    reverse_order[0].action_assign()
                                    self.env.cr.commit()
                                else:
                                    stock_return_picking_form = Form(
                                        self.env['stock.return.picking'].with_context(active_id=move.picking_id.id,
                                                                                      active_model='stock.picking'))
                                    return_wizard = stock_return_picking_form.save()
                                    r_wizard_line = return_wizard.product_return_moves.filtered(
                                        lambda x: x.product_id == move.product_id)
                                    r_wizard_line.with_context(from_mrp=1).write({'quantity': abs(TTQ - (TNQ + TOTR))})
                                    return_wizard.product_return_moves.filtered(lambda x: x.id != r_wizard_line.id).unlink()
                                    return_picking_id, pick_type_id = return_wizard._create_returns()
                                    return_pick = self.env['stock.picking'].browse(return_picking_id)
                                    for line in return_pick.move_line_ids_without_package:
                                        line.with_context(from_mrp=1).write({'qty_done': line.product_uom_qty})
                                    self.env.cr.commit()
                            elif move.product_uom_qty <= r_qty > 0:
                                reverse_order = self.raw_material_production_id.picking_ids.filtered(
                                    lambda x: x.state not in ('done', 'cancel') and
                                              x.picking_type_id == picking_type and
                                              x.location_id == picking_type.default_location_dest_id and
                                              x.origin == 'Return of %s' % move.picking_id.name)
                                if reverse_order:
                                    vals = {
                                        'product_id': move.product_id.id,
                                        'product_uom_qty': r_qty,
                                        'product_uom': move.product_uom.id,
                                        'date_expected': move.date_expected,
                                        'picking_type_id': move.picking_id.picking_type_id.id,
                                        'location_id': reverse_order[0].location_id.id,
                                        'location_dest_id': reverse_order[0].location_dest_id.id,
                                        'picking_id': reverse_order[0].id,
                                        'warehouse_id': move.location_dest_id.get_warehouse().id,
                                        'state': 'draft',
                                        'origin_returned_move_id': move.id,
                                        'procure_method': 'make_to_stock',
                                        'to_refund': True,
                                        'is_subcontract': False,
                                    }
                                    move.copy(vals)
                                    reverse_order[0].do_unreserve()
                                    reverse_order[0].action_confirm()
                                    reverse_order[0].action_assign()
                                    self.env.cr.commit()
                                else:
                                    stock_return_picking_form = Form(
                                        self.env['stock.return.picking'].with_context(active_id=move.picking_id.id,
                                                                                      active_model='stock.picking'))
                                    return_wizard = stock_return_picking_form.save()
                                    r_wizard_line = return_wizard.product_return_moves.filtered(
                                        lambda x: x.product_id == move.product_id)
                                    r_wizard_line.with_context(from_mrp=1).write({'quantity': abs(TTQ - (TNQ + TOTR))})
                                    return_wizard.product_return_moves.filtered(lambda x: x.id != r_wizard_line.id).unlink()
                                    return_picking_id, pick_type_id = return_wizard._create_returns()
                                    return_pick = self.env['stock.picking'].browse(return_picking_id)
                                    for line in return_pick.move_line_ids_without_package:
                                        line.with_context(from_mrp=1).write({'qty_done': move.product_uom_qty})
                                    self.env.cr.commit()
                                r_qty = r_qty - move.product_uom_qty
            else:
                if self._context.get('create_new'):
                    if open_pickings and (TNQ - TTQ - TOQ + TOTR) > 0:
                        rec = self.create({
                            'product_id': self.product_id.id,
                            'product_uom_qty': (TNQ - TTQ - TOQ + TOTR),
                            'product_uom': self.product_uom.id,
                            'name': self.raw_material_production_id.name,
                            'date': self.raw_material_production_id.date_planned_start,
                            'date_expected': self.raw_material_production_id.date_planned_finished,
                            'picking_type_id': open_pickings.picking_type_id.id,
                            'location_id': picking_type.default_location_src_id.id,
                            'location_dest_id': picking_type.default_location_dest_id.id,
                            'company_id': self.company_id.id,
                            'picking_id': open_pickings.id,
                            'warehouse_id': self.location_dest_id.get_warehouse().id,
                            'origin': self.raw_material_production_id.name,
                            'group_id': self.raw_material_production_id.procurement_group_id.id,
                        })
                        rec._action_confirm()
                        self.move_orig_ids = [(4, rec.id)]
                        self.env.cr.commit()
                    else:
                        if (TNQ - TTQ - TOQ + TOTR) > 0:
                            picking = self.env['stock.picking'].create({
                                'origin': self.raw_material_production_id.name,
                                'company_id': self.mapped('company_id').id,
                                'user_id': self.raw_material_production_id.user_id.id,
                                'group_id': self.group_id.id,
                                'move_type': self.mapped('group_id').move_type or 'direct',
                                'picking_type_id': picking_type.id,
                                'location_id': picking_type.default_location_src_id.id,
                                'location_dest_id': picking_type.default_location_dest_id.id,
                            })
                            rec = self.create({
                                'product_id': self.product_id.id,
                                'product_uom_qty': (TNQ - TTQ - TOQ + TOTR),
                                'product_uom': self.product_uom.id,
                                'name': self.raw_material_production_id.name,
                                'date': self.raw_material_production_id.date_planned_start,
                                'date_expected': self.raw_material_production_id.date_planned_finished,
                                'picking_type_id': picking.picking_type_id.id,
                                'location_id': picking_type.default_location_src_id.id,
                                'location_dest_id': picking_type.default_location_dest_id.id,
                                'company_id': self.company_id.id,
                                'picking_id': picking.id,
                                'warehouse_id': self.location_dest_id.get_warehouse().id,
                                'origin': self.raw_material_production_id.name,
                                'group_id': self.raw_material_production_id.procurement_group_id.id,
                            })
                            self.move_orig_ids = [(4, rec.id)]
                            picking.action_confirm()
                            self.env.cr.commit()

    def action_explode(self):
        """ Explodes pickings """
        # in order to explode a move, we must have a picking_type_id on that move because otherwise the move
        # won't be assigned to a picking and it would be weird to explode a move into several if they aren't
        # all grouped in the same picking.
        moves_to_return = self.env['stock.move']
        moves_to_unlink = self.env['stock.move']
        phantom_moves_vals_list = []
        for move in self:
            if not move.product_id.consumed_as_needed and move.picking_type_id.code == 'mrp_operation':
                if not move.picking_type_id or (
                        move.production_id and move.production_id.product_id == move.product_id):
                    moves_to_return |= move
                    continue
                bom = self.env['mrp.bom'].sudo()._bom_find(product=move.product_id, company_id=move.company_id.id,
                                                           bom_type='phantom')
                if not bom:
                    moves_to_return |= move
                    continue
                if move.picking_id.immediate_transfer:
                    factor = move.product_uom._compute_quantity(move.quantity_done,
                                                                bom.product_uom_id) / bom.product_qty
                else:
                    factor = move.product_uom._compute_quantity(move.product_uom_qty,
                                                                bom.product_uom_id) / bom.product_qty
                boms, lines = bom.sudo().explode(move.product_id, factor, picking_type=bom.picking_type_id)
                for bom_line, line_data in lines:
                    if move.picking_id.immediate_transfer:
                        phantom_moves_vals_list += move._generate_move_phantom(bom_line, 0, line_data['qty'])
                    else:
                        phantom_moves_vals_list += move._generate_move_phantom(bom_line, line_data['qty'], 0)
                # delete the move with original product which is not relevant anymore
                moves_to_unlink |= move
            elif move.picking_type_id.code != 'mrp_operation':
                if not move.picking_type_id or (
                        move.production_id and move.production_id.product_id == move.product_id):
                    moves_to_return |= move
                    continue
                bom = self.env['mrp.bom'].sudo()._bom_find(product=move.product_id, company_id=move.company_id.id,
                                                           bom_type='phantom')
                if not bom:
                    moves_to_return |= move
                    continue
                if move.picking_id.immediate_transfer:
                    factor = move.product_uom._compute_quantity(move.quantity_done,
                                                                bom.product_uom_id) / bom.product_qty
                else:
                    factor = move.product_uom._compute_quantity(move.product_uom_qty,
                                                                bom.product_uom_id) / bom.product_qty
                boms, lines = bom.sudo().explode(move.product_id, factor, picking_type=bom.picking_type_id)
                for bom_line, line_data in lines:
                    if move.picking_id.immediate_transfer:
                        phantom_moves_vals_list += move._generate_move_phantom(bom_line, 0, line_data['qty'])
                    else:
                        phantom_moves_vals_list += move._generate_move_phantom(bom_line, line_data['qty'], 0)
                # delete the move with original product which is not relevant anymore
                moves_to_unlink |= move

        moves_to_unlink.sudo().unlink()
        if phantom_moves_vals_list:
            phantom_moves = self.env['stock.move'].create(phantom_moves_vals_list)
            phantom_moves._adjust_procure_method()
            moves_to_return |= phantom_moves.action_explode()
        return moves_to_return

    def _action_assign(self):
        result = super(StockMove, self)._action_assign()
        self._set_reserved_quantity()
        return result

    def _set_reserved_quantity(self):
        assigned_moves = self.env['stock.move']
        partially_available_moves = self.env['stock.move']
        reserved_availability = {move: move.reserved_availability for move in self}
        roundings = {move: move.product_id.uom_id.rounding for move in self}
        move_line_vals_list = []
        for move in self:
            if move.product_id.consumed_as_needed:
                rounding = roundings[move]
                missing_reserved_uom_quantity = move.product_uom_qty - reserved_availability[move]
                missing_reserved_quantity = move.product_uom._compute_quantity(missing_reserved_uom_quantity, move.product_id.uom_id, rounding_method='HALF-UP')
                need = missing_reserved_quantity
                if float_is_zero(need, precision_rounding=rounding):
                    assigned_moves |= move
                    continue
                # Reserve new quants and create move lines accordingly.
                forced_package_id = move.package_level_id.package_id or None
                available_quantity = self.env['stock.quant']._get_available_quantity(move.product_id, move.location_id, package_id=forced_package_id)
                if available_quantity <= 0:
                    continue
                taken_quantity = move._update_reserved_quantity(need, available_quantity, move.location_id, package_id=forced_package_id, strict=False)
                if float_is_zero(taken_quantity, precision_rounding=rounding):
                    continue
                if float_compare(need, taken_quantity, precision_rounding=rounding) == 0:
                    assigned_moves |= move
                else:
                    partially_available_moves |= move

        self.env['stock.move.line'].create(move_line_vals_list)
        partially_available_moves.write({'state': 'partially_available'})
        assigned_moves.write({'state': 'assigned'})
