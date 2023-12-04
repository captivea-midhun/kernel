# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, Warning
from collections import defaultdict


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_view_mo_delivery(self):
        """ This function returns an action that display picking related to
        manufacturing order orders. It can either be a in a list or in a form
        view, if there is only one picking to show.
        """
        action = super(MrpProduction, self).action_view_mo_delivery()
        pickings = self.picking_ids.filtered(lambda x: x.state not in ['done', 'cancel'])
        # for picking in pickings:
        #     picking.filtered(lambda picking: picking.state == 'draft').action_confirm()
        #     moves = picking.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))
        #     if moves:
        #         picking.action_assign()
        if len(pickings) == 1:
            action['context']['form_view_initial_mode'] = 'edit'
        return action

    def create_transfer(self):
        """ This function creates a Transfer for .
        """
        action = self.env.ref("stock.action_picking_tree_all").read()[0]
        picking_type = self.env['stock.picking.type'].search([('sequence_code', '=', 'PC')], limit=1)
        form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
        action['views'] = form_view
        action['context'] = {
            'default_origin': self.name,
            'default_company_id': self.mapped('company_id').id,
            'default_user_id': self.user_id.id,
            'default_picking_type_id': picking_type.id,
            'default_group_id': self.procurement_group_id.id,
            'default_location_id': picking_type.default_location_src_id.id,
            'default_location_dest_id': picking_type.default_location_dest_id.id,
            'form_view_initial_mode': 'edit',
        }
        return action

    def write(self, vals):
        res = super(MrpProduction, self).write(vals)
        # if vals.get('product_qty'):
        #     for picking in self.picking_ids.filtered(lambda x: x.state not in ['done', 'cancel']):
        #         picking.activity_ids.filtered(lambda x: x.activity_type_id.name == 'Exception').unlink()
        #         try:
        #             activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
        #         except:
        #             activity_type_id = False
        #
        #         activity = picking.activity_ids.filtered(lambda x:
        #                                                  x.activity_type_id.name == 'To Do' and
        #                                                  x.summary == 'The MO quantity has changed, please review the order and make sure all components have been addressed')
        #         if activity:
        #             activity.write({'date_deadline': fields.Date.today()})
        #         else:
        #             self.env['mail.activity'].create({
        #                 'summary': 'The MO quantity has changed, please review the order and make sure all components '
        #                            'have been addressed',
        #                 'date_deadline': fields.Date.today(),
        #                 'user_id': self.user_id.id,
        #                 'activity_type_id': activity_type_id,
        #                 'res_model_id': self.env.ref('stock.model_stock_picking').id,
        #                 'res_id': picking.id,
        #             })
        return res

    def _update_raw_move(self, bom_line, line_data):
        """ :returns update_move, old_quantity, new_quantity """
        quantity = line_data['qty']
        self.ensure_one()
        move = self.move_raw_ids.filtered(
            lambda x: x.bom_line_id.id == bom_line.id and x.state not in ('done', 'cancel'))
        if move:
            old_qty = move[0].product_uom_qty
            remaining_qty = move[0].raw_material_production_id.product_qty - move[
                0].raw_material_production_id.qty_produced
            if quantity > 0:
                move[0].write({'product_uom_qty': quantity})
                move[0]._recompute_state()
                move[0]._action_assign()
                if move[0].raw_material_production_id.picking_type_id.sequence_code == 'MO' and move[0].raw_material_production_id.picking_type_id.code == 'mrp_operation':
                    move[0]._action_update_picking()
                move[0].unit_factor = remaining_qty and (quantity - move[0].quantity_done) / remaining_qty or 1.0
                return move[0], old_qty, quantity
            else:
                if move[0].quantity_done > 0:
                    raise UserError(
                        _('Lines need to be deleted, but can not as you still have some quantities to consume in them. '))
                move[0]._action_cancel()
                move[0].unlink()
                return self.env['stock.move'], old_qty, quantity
        else:
            move_values = self._get_move_raw_values(bom_line, line_data)
            move_values['state'] = 'confirmed'
            move = self.env['stock.move'].create(move_values)
            return move, 0, quantity

    def action_confirm(self):
        self._check_company()
        for production in self:
            if not production.move_raw_ids:
                raise UserError(_("Add some materials to consume before marking this MO as to do."))
            for move_raw in production.move_raw_ids:
                move_raw.write({
                    'unit_factor': move_raw.product_uom_qty / production.product_qty,
                })
            production._generate_finished_moves()
            production.move_raw_ids._adjust_procure_method()
            (production.move_raw_ids | production.move_finished_ids)._action_confirm()
        return True

    def action_toggle_is_locked(self):
        self.ensure_one()
        self.is_locked = not self.is_locked
        if not self.is_locked and self.bom_id.consumption != 'flexible':
            raise Warning(
                _('The BOM is currently not set to "Flexible", please change the setting in the BOM if you want to '
                  'update the BOM'))
        return True

    @api.model
    def create(self, vals):
        res = super(MrpProduction, self).create(vals)
        sku_list = []
        skus = ""
        for line in res.move_raw_ids:
            if not line.product_id.active:
                sku_list.append(line.product_id.default_code)
                skus += str(line.product_id.default_code) + "<br/>"
        if sku_list:
            self.env['mail.message'].create({
                'message_type': 'comment',
                'model': res._name,
                'res_id': res.id,
                'subtype_id': self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment'),
                'body': "Product(s) from your previous order are unavailable for purchase.  "
                        "Archived Products:<br/>" + skus +
                        "You may need to add or create a new rev of these products. Contact the Inventory "
                        "Team with any questions."
            })
        return res

    def action_cancel(self):
        """ Cancels production order, unfinished stock moves and set procurement
        orders in exception """
        if not self.move_raw_ids:
            self.state = 'cancel'
            return True
        try:
            activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
        except:
            activity_type_id = False
        user = self.env['res.users'].search([('name', 'ilike', 'Dakota Decker')])
        picking_type = self.env['stock.picking.type'].search([('sequence_code', '=', 'PC')], limit=1)
        done_picking = self.picking_ids.filtered(
            lambda x: x.state == 'done' and
                      x.picking_type_id == picking_type and
                      x.location_id == picking_type.default_location_src_id)
        for line in self.move_raw_ids:
            done_qty = sum(done_picking.move_ids_without_package.filtered(lambda x: x.product_id == line.product_id).mapped(
                'quantity_done'))
            if line.product_uom_qty - line.quantity_done - done_qty <= 0:
                self.env['mail.activity'].create({
                    'summary': 'Manufacturing Order "%s" has been cancelled with components that need to be returned '
                               'to stock' % self.name,
                    'date_deadline': fields.Date.today(),
                    'user_id': user.id,
                    'activity_type_id': activity_type_id,
                    'res_model_id': self.env.ref('mrp.model_mrp_production').id,
                    'res_id': self.id,
                })
                break
        self._action_cancel()
        return True

    def _action_cancel(self):
        documents_by_production = {}
        for production in self:
            documents = defaultdict(list)
            for move_raw_id in self.move_raw_ids.filtered(lambda m: m.state not in ('done', 'cancel')):
                iterate_key = self._get_document_iterate_key(move_raw_id)
                if iterate_key:
                    document = self.env['stock.picking']._log_activity_get_documents({move_raw_id: (move_raw_id.product_uom_qty, 0)}, iterate_key, 'UP')
                    for key, value in document.items():
                        documents[key] += [value]
            if documents:
                documents_by_production[production] = documents

        self.workorder_ids.filtered(lambda x: x.state not in ['done', 'cancel']).action_cancel()
        finish_moves = self.move_finished_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
        raw_moves = self.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
        (finish_moves | raw_moves)._action_cancel()
        picking_ids = self.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
        picking_ids.action_cancel()

        for production, documents in documents_by_production.items():
            filtered_documents = {}
            for (parent, responsible), rendering_context in documents.items():
                if not parent or parent._name == 'stock.picking' and parent.state == 'cancel' or parent == production:
                    continue
                filtered_documents[(parent, responsible)] = rendering_context
            # production._log_manufacture_exception(filtered_documents, cancel=True)

        # In case of a flexible BOM, we don't know from the state of the moves if the MO should
        # remain in progress or done. Indeed, if all moves are done/cancel but the quantity produced
        # is lower than expected, it might mean:
        # - we have used all components but we still want to produce the quantity expected
        # - we have used all components and we won't be able to produce the last units
        #
        # However, if the user clicks on 'Cancel', it is expected that the MO is either done or
        # canceled. If the MO is still in progress at this point, it means that the move raws
        # are either all done or a mix of done / canceled => the MO should be done.
        self.filtered(lambda p: p.state not in ['done', 'cancel'] and p.bom_id.consumption == 'flexible').write({'state': 'done'})

        return True