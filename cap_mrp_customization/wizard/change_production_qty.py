# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_round


class ChangeProductionQty(models.TransientModel):
    _inherit = 'change.production.qty'

    def change_prod_qty(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for wizard in self:
            production = wizard.mo_id
            produced = sum(
                production.move_finished_ids.filtered(lambda m: m.product_id == production.product_id).mapped(
                    'quantity_done'))
            if wizard.product_qty < produced:
                format_qty = '%.{precision}f'.format(precision=precision)
                raise UserError(_("You have already processed %s. Please input a quantity higher than %s ") % (
                    format_qty % produced, format_qty % produced))
            old_production_qty = production.product_qty
            production.write({'product_qty': wizard.product_qty})
            done_moves = production.move_finished_ids.filtered(
                lambda x: x.state == 'done' and x.product_id == production.product_id)
            qty_produced = production.product_id.uom_id._compute_quantity(sum(done_moves.mapped('product_qty')),
                                                                          production.product_uom_id)
            factor = production.product_uom_id._compute_quantity(production.product_qty - qty_produced,
                                                                 production.bom_id.product_uom_id) / production.bom_id.product_qty
            boms, lines = production.bom_id.explode(production.product_id, factor,
                                                    picking_type=production.bom_id.picking_type_id)
            picking_type = self.env['stock.picking.type'].search([('sequence_code', '=', 'PC')], limit=1)
            done_pickings = production.picking_ids.filtered(
                lambda x: x.state == 'done' and x.picking_type_id == picking_type and
                          x.location_id == picking_type.default_location_src_id)
            return_pickings = production.picking_ids.filtered(
                lambda x: x.state not in ['cancel'] and
                          x.picking_type_id == picking_type and
                          x.location_id == picking_type.default_location_dest_id)
            documents = {}
            activity_create = False
            chatter_msg = []
            log_msg = "<ul>"
            n_move = self.env['stock.move']
            for line, line_data in lines:
                if line.child_bom_id and line.child_bom_id.type == 'phantom' or \
                        line.product_id.type not in ['product', 'consu']:
                    continue
                move = production.move_raw_ids.filtered(
                    lambda x: x.bom_line_id.id == line.id and x.state not in ('done', 'cancel'))
                if move:
                    move = move[0]
                    old_qty = move.product_uom_qty
                else:
                    old_qty = 0
                iterate_key = production._get_document_iterate_key(move)
                if iterate_key:
                    document = self.env['stock.picking']._log_activity_get_documents(
                        {move: (line_data['qty'], old_qty)}, iterate_key, 'UP')
                    for key, value in document.items():
                        if documents.get(key):
                            documents[key] += [value]
                        else:
                            documents[key] = [value]

                d_move, val, qty = production._update_raw_move(line, line_data)
                n_move = d_move.move_orig_ids[-1] if d_move.move_orig_ids else False
                done_pickings = production.picking_ids.filtered(
                    lambda x: x.state == 'done' and x.picking_type_id == picking_type and
                              x.location_id == picking_type.default_location_src_id)
                return_pickings = production.picking_ids.filtered(
                    lambda x: x.state not in ['cancel'] and
                              x.picking_type_id == picking_type and
                              x.location_id == picking_type.default_location_dest_id)
                TTQ = sum(
                    done_pickings.move_ids_without_package.filtered(lambda x: x.product_id == line.product_id).mapped(
                        'quantity_done'))
                TOTR = sum(
                    return_pickings.move_ids_without_package.filtered(lambda x: x.product_id == line.product_id).mapped(
                        'product_uom_qty'))
                if line_data['qty'] > TTQ - TOTR and not line.product_id.consumed_as_needed:
                    activity_create = True
                if line_data['qty'] == TTQ - TOTR:
                    chatter_msg.append(False)
                else:
                    if n_move and not line.product_id.consumed_as_needed:
                        chatter_msg.append(True)
                        log_msg += "<li>%s : Quantity: %s -> %s</li>" % (line.product_id.name, TTQ - TOTR, line_data['qty'])
                    else:
                        chatter_msg.append(False)

            # production._log_manufacture_exception(documents)
            operation_bom_qty = {}
            for bom, bom_data in boms:
                for operation in bom.routing_id.operation_ids:
                    operation_bom_qty[operation.id] = bom_data['qty']
            finished_moves_modification = self._update_finished_moves(production, production.product_qty - qty_produced,
                                                                      old_production_qty)
            production._log_downside_manufactured_quantity(finished_moves_modification)
            user = self.env['res.users'].search([('name', 'ilike', 'Cristian Salazar')])
            try:
                activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
            except:
                activity_type_id = False
            if old_production_qty > production.product_qty:
                msg = "<p>Quantity To Produce: %s -> %s <br/> <span style='color: red;'><b>Go to Transfers</b> to " \
                      "validate the created return for unused components.</span></p>" % (
                          old_production_qty, production.product_qty)
            else:
                if True in chatter_msg and log_msg:
                    self.env['mail.message'].create({
                        'message_type': 'comment',
                        'model': production._name,
                        'res_id': production.id,
                        'subtype_id': self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment'),
                        'body': "Excess components were transferred for this MO on "
                                "<a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a>."
                                % (n_move.picking_id.id, n_move.picking_id.name) + log_msg + "</ul>"
                    })
                msg = "<p>Quantity To Produce: %s -> %s <br/> <span style='color: red;'><b>Go to Transfers</b> to " \
                      "validate the created transfer for additional components.</span></p>" % (
                          old_production_qty, production.product_qty)
            if activity_create:
                self.env['mail.activity'].create({
                    'note': msg,
                    'date_deadline': fields.Date.today(),
                    'user_id': user.id,
                    'activity_type_id': activity_type_id,
                    'res_model_id': self.env.ref('mrp.model_mrp_production').id,
                    'res_id': production.id,
                })
            moves = production.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            moves._action_assign()
            for wo in production.workorder_ids:
                operation = wo.operation_id
                if operation_bom_qty.get(operation.id):
                    cycle_number = float_round(operation_bom_qty[operation.id] / operation.workcenter_id.capacity,
                                               precision_digits=0, rounding_method='UP')
                    wo.duration_expected = (operation.workcenter_id.time_start +
                                            operation.workcenter_id.time_stop +
                                            cycle_number * operation.time_cycle * 100.0 / operation.workcenter_id.time_efficiency)
                production_qty = wo._get_real_uom_qty(wo.qty_production)
                quantity = production_qty - wo.qty_produced
                if production.product_id.tracking == 'serial':
                    quantity = 1.0 if not float_is_zero(quantity, precision_digits=precision) else 0.0
                else:
                    quantity = quantity if (quantity > 0) else 0
                if float_is_zero(quantity, precision_digits=precision):
                    wo.finished_lot_id = False
                    wo._workorder_line_ids().unlink()
                wo.qty_producing = quantity
                if wo.qty_produced < production_qty and wo.state == 'done':
                    wo.state = 'progress'
                if wo.qty_produced == production_qty and wo.state == 'progress':
                    wo.state = 'done'
                    if wo.next_work_order_id.state == 'pending':
                        wo.next_work_order_id.state = 'ready'
                # assign moves; last operation receive all unassigned moves
                # TODO: following could be put in a function as it is similar as code in _workorders_create
                # TODO: only needed when creating new moves
                moves_raw = production.move_raw_ids.filtered(
                    lambda move: move.operation_id == operation and move.state not in ('done', 'cancel'))
                if wo == production.workorder_ids[-1]:
                    moves_raw |= production.move_raw_ids.filtered(lambda move: not move.operation_id)
                moves_finished = production.move_finished_ids.filtered(
                    lambda move: move.operation_id == operation)  # TODO: code does nothing, unless maybe by_products?
                moves_raw.mapped('move_line_ids').write({'workorder_id': wo.id})
                (moves_finished + moves_raw).write({'workorder_id': wo.id})
                if wo.state not in ('done', 'cancel'):
                    line_values = wo._update_workorder_lines()
                    wo._workorder_line_ids().create(line_values['to_create'])
                    if line_values['to_delete']:
                        line_values['to_delete'].unlink()
                    for line, vals in line_values['to_update'].items():
                        line.write(vals)
        return {}
