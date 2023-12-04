# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    po_route_id = fields.Many2one(
        'stock.location.route', string="Receiving Route")

    def _get_route_destination_location(self):
        """
        Method to get destination location based on selected route into
        Purchase order line.
        """
        self.ensure_one()
        if self.po_route_id:
            sequence = False
            rule_data = False
            for rule_rec in self.po_route_id.rule_ids.filtered(
                    lambda r: r.picking_type_id.code == 'incoming' and r.picking_type_id.warehouse_id.id == self.order_id.picking_type_id.warehouse_id.id):
                if not rule_data:
                    sequence = rule_rec.sequence
                    rule_data = rule_rec
                elif rule_data and rule_rec.sequence < sequence:
                    sequence = rule_rec.sequence
                    rule_data = rule_rec
            if rule_data:
                return [rule_data and rule_data.location_id.id or False,
                        rule_data.picking_type_id.id]
        return [self.order_id.picking_type_id.default_location_dest_id.id, False]

    def lines_group_by_route(self, picking):
        """
        Method to group PO lines based on selected routes into
        PO lines.
        """
        group_by_route = {}
        current_picking = []
        for line in self:
            dest_location_id = line._get_route_destination_location()
            if dest_location_id:
                if dest_location_id[0] != picking.location_dest_id.id:
                    if line.po_route_id and group_by_route.get(
                            line.po_route_id.id):
                        group_by_route[line.po_route_id.id].append(line)
                    elif line.po_route_id and not group_by_route.get(
                            line.po_route_id.id):
                        group_by_route.update({line.po_route_id.id: [line]})
                else:
                    current_picking.append(line)
        if current_picking:
            group_by_route.update({'current_picking': current_picking})
        return group_by_route

    def _create_stock_moves(self, picking):
        """
        Method override to create picking based on selected groups into PO
        lines.
        """
        values = []
        po_lines = self.lines_group_by_route(picking)
        flag = True if len(po_lines) == 1 else False
        for key in po_lines:
            if key == 'current_picking':
                for line in po_lines[key]:
                    for val in line._prepare_stock_moves(picking):
                        values.append(val)
            else:
                lines = po_lines[key]
                ctx = dict(self._context) or {}
                dest_location_id = lines[0]._get_route_destination_location()
                if flag:
                    picking.write({'location_dest_id': dest_location_id[0],
                                   'picking_type_id': dest_location_id[1]})
                    copy_picking = picking
                    ctx.update({'default_change_location': True})
                else:
                    copy_picking = picking.copy({
                        'location_dest_id': dest_location_id[0],
                        'picking_type_id': dest_location_id[1]})
                    ctx.update({'default_change_location': False})
                for line in lines:
                    for val in line.with_context(
                            ctx)._prepare_stock_moves(copy_picking):
                        values.append(val)
        return self.env['stock.move'].create(values)

    def _prepare_stock_moves(self, picking):
        """
        Method inherited to update location, picking_id and route_ids
        into stock move vals.
        """
        ctx = dict(self._context) or {}
        move_vals = super(PurchaseOrderLine, self)._prepare_stock_moves(
            picking=picking)
        dest_location_id = self._get_route_destination_location()
        if picking and picking.location_dest_id.id != dest_location_id[0]:
            if ctx.get('default_change_location'):
                picking._update_picking_location(
                    dest_location_id[0], dest_location_id[1])
            else:
                picking = self.order_id.picking_ids.filtered(
                    lambda x: x.state not in (
                        'done', 'cancel') and x.location_dest_id.id == dest_location_id[
                                  0] and x.picking_type_id.id == dest_location_id[1])
            if not picking:
                picking_vals = self.order_id._prepare_picking()
                picking = self.env['stock.picking'].create(picking_vals)
                picking._update_picking_location(
                    dest_location_id[0], dest_location_id[1])
        for val in move_vals:
            if self.po_route_id:
                val.update({'route_ids': [(6, 0, [self.po_route_id.id])]})
            val.update({'location_dest_id': dest_location_id[0],
                        'picking_id': picking.id})
        return move_vals

    @api.onchange('product_id')
    def onchange_product_id(self):
        """
        Method to get product current receiving route into PO Lines.
        """
        res = super(PurchaseOrderLine, self).onchange_product_id()
        if self.product_id:
            pro_route_id = self.product_id.receiving_route_id
            categ_route_id = self.product_id.categ_id.categ_receive_route_id
            self.po_route_id = pro_route_id if pro_route_id else categ_route_id or False
        return res


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends('order_line.move_ids.returned_move_ids',
                 'order_line.move_ids.state',
                 'order_line.move_ids.picking_id')
    def _compute_picking(self):
        super(PurchaseOrder, self)._compute_picking()
        for order in self:
            pick_internal_count = self.env['stock.picking'].search_count(
                [('purchase_picking_id', '=', self.id)])
            order.picking_count = order.picking_count + pick_internal_count

    def action_view_picking(self):
        """ This function returns an action that display existing picking orders and Internal picking orders of given purchase order ids. When only one found, show the picking immediately.
        """
        res = super(PurchaseOrder, self).action_view_picking()
        pick_internal_ids = self.env['stock.picking'].search(
            [('purchase_picking_id', '=', self.id)])
        if pick_internal_ids:
            pick_ids = self.mapped('picking_ids')
            pick_ids |= pick_internal_ids
            if len(pick_ids) > 1:
                if res.get('views'):
                    res['views'] = []
                if res.get('res_id'):
                    res['res_id'] = False
                res['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        return res
