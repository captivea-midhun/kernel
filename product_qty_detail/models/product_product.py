# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields, _


class ProductProduct(models.Model):
    _inherit = "product.product"

    net_on_hand_qty = fields.Float(compute='_get_net_on_hand_qty', string='Net On Hand')
    default_code = fields.Char('Internal Reference', index=True, track_visibility='onchange')

    def _get_po_qty_details(self):
        """
        Search purchase order which is not fully received
        :return: List of purchase order with remaining receive quantity, Total Remaining Receive Quantity
        """
        qty_details = []
        po_line_ids = self.env['purchase.order.line'].search(
            [('product_id', '=', self.id), ('state', '=', 'purchase'),
             ('order_id.picking_ids', '!=', False)])
        total_remaining_qty = 0
        for po_line_id in po_line_ids.filtered(lambda line: line.product_qty > line.qty_received):
            remaining_qty = po_line_id.product_qty - po_line_id.qty_received
            qty_details.append((0, 0, {'po_id': po_line_id.order_id.id,
                                       'expected_date': po_line_id.order_id.date_planned or False,
                                       'qty': remaining_qty}))
            total_remaining_qty += remaining_qty
        return qty_details, total_remaining_qty

    def _get_po_qty_received_details(self):
        """  Search purchase order which is fully received """
        qty_details_received = []
        po_line_recs = self.env['purchase.order.line'].search(
            [('product_id', '=', self.product_variant_id.id),
             ('state', '=', 'purchase'),
             ('order_id.picking_ids', '!=', False),
             ('order_id.unreceived_qty', '=', 0)])
        total_received_po_qty = 0
        for po_line in po_line_recs:
            remaining_qty = po_line.qty_received
            qty_details_received.append(
                (0, 0, {'po_id': po_line.order_id.id,
                        'expected_date': po_line.order_id.date_planned or False,
                        'qty': remaining_qty}))
            total_received_po_qty += remaining_qty
        return qty_details_received, total_received_po_qty

    def _get_mo_qty_details(self):
        """
        Search Manufacturing Orders, which is reserved some quantity
        :return: List of Manufacturing Orders with quantity, Total Reserved Quantity
        """
        qty_details = []
        sm_lime_ids = self.env['stock.move.line'].search(
            [('product_id', '=', self.id),
             ('production_id', '!=', False),
             ('production_id.state', 'not in', ['draft', 'done', 'cancel']),
             ('product_uom_qty', '>', 0),
             ('move_id.raw_material_production_id', '!=', False),
             ('move_id.raw_material_production_id.picking_type_id.sequence_code', '!=', 'SBC')])
        sm_ids = sm_lime_ids.mapped('move_id')
        total_reserved_qty = sum(sm_ids.mapped('reserved_availability'))
        for sm in sm_ids:
            qty_details.append((0, 0, {'mo_id': sm.raw_material_production_id.id,
                                       'qty': sm.reserved_availability}))
        return qty_details, total_reserved_qty

    def _get_mo_qty_received_details(self):
        """ Search Manufacturing orders which are done """
        qty_details_received = []
        sm_rec_ids = self.env['stock.move'].search(
            [('product_id', '=', self.id),
             '|', '&', ('production_id', '!=', False),
             ('production_id.state', '=', 'done'),
             '&', ('raw_material_production_id', '!=', False),
             ('raw_material_production_id.state', '=', 'done')])
        total_received_mo_qty = sum(sm_rec_ids.mapped('quantity_done'))

        finish_move_ids = sm_rec_ids.filtered(lambda x: x.production_id)
        for finish_move_id in finish_move_ids:
            qty_details_received.append(
                (0, 0, {'mo_id': finish_move_id.production_id.id,
                        'qty': finish_move_id.quantity_done}))

        component_move_ids = sm_rec_ids.filtered(lambda x: x.raw_material_production_id)
        for component_move_id in component_move_ids:
            qty_details_received.append(
                (0, 0, {'mo_id': component_move_id.raw_material_production_id.id,
                        'qty': component_move_id.quantity_done}))

        return qty_details_received, total_received_mo_qty

    def _get_net_on_hand_qty(self):
        """
        Calculate Net on Hand Quantity
        Calculation :
        Net on Hand Quantity = On Hand Quantity - Total Reserved Quantity in Manufacturing Order
        :return: None
        """
        qty_detail, total_reserve_qty = self._get_mo_qty_details()
        qty_detail_picking, picking_reserved_qty = self._get_picking_qty_details()
        self.net_on_hand_qty = self.qty_available - total_reserve_qty - picking_reserved_qty
        # self.net_on_hand_qty = self.x_studio_stock_qty - total_reserve_qty - picking_reserved_qty

    def _get_picking_qty_details(self):
        """
        Search Stock Pickings, to find reserved quantities
        :return: List of Stock Pickings with quantity, Total Reserved Quantity
        """
        qty_details = []
        sm_line_ids = self.env['stock.move.line'].search(
            [('product_id', '=', self.id), ('product_uom_qty', '>', 0),
             ('picking_id', '!=', False), ('picking_id.picking_type_code', '!=', 'incoming')])
        total_reserved_qty = sum(sm_line_ids.mapped('product_uom_qty'))
        for each in sm_line_ids:
            qty_details.append((0, 0, {'picking_id': each.picking_id.id,
                                       'qty_reserved': each.product_uom_qty}))
        return qty_details, total_reserved_qty

    def _get_picking_qty_received_details(self):
        """ Picking Qty done details"""
        qty_details_received = []
        sm_line_rec_ids = self.env['stock.move.line'].search(
            [('product_id', '=', self.product_variant_id.id),
             ('qty_done', '>', 0), ('picking_id.state', '=', 'done'),
             ('picking_id', '!=', False), ('picking_id.picking_type_code', '!=', 'incoming')])
        total_picking_qty = sum(sm_line_rec_ids.mapped('qty_done'))
        for each in sm_line_rec_ids:
            qty_details_received.append((0, 0, {'picking_id': each.picking_id.id,
                                                'qty_reserved': each.qty_done}))
        return qty_details_received, total_picking_qty

    def action_product_tmpl_detailed_qty(self):
        """
        Create Detail Quantity record and Redirect on Detail Quantity
        :return: Detail Quantity Wizard
        """
        po_rec_dic, total_received_po_qty = self._get_po_qty_received_details()
        po_dic, total_remaining_qty = self._get_po_qty_details()
        mo_rec_dic, total_received_mo_qty = self._get_mo_qty_received_details()
        mo_dic, total_reserve_qty = self._get_mo_qty_details()
        picking_rec_dic, total_picking_qty = self._get_picking_qty_received_details()
        picking_dic, picking_reserved_qty = self._get_picking_qty_details()
        total_reserve_qty += picking_reserved_qty
        vals = {'product_id': self.id,
                'on_hand_qty': self.qty_available,
                'total_remaining_qty': total_remaining_qty,
                'total_reserve_qty': total_reserve_qty,
                'net_qty': self.qty_available - total_reserve_qty,
                'forecast_qty': self.qty_available + total_remaining_qty}
        if po_dic:
            vals['po_qty_ids'] = po_dic
        if po_rec_dic:
            vals['po_qty_rec_ids'] = po_rec_dic
        if mo_dic:
            vals['mo_qty_ids'] = mo_dic
        if mo_rec_dic:
            vals['mo_qty_rec_ids'] = mo_rec_dic
        if picking_dic:
            vals['picking_qty_ids'] = picking_dic
        if picking_rec_dic:
            vals['picking_qty_rec_ids'] = picking_rec_dic

        detail_qty_id = self.env['product.detailed.qty'].create(vals)
        return {'name': _('Detailed Quantity'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env.ref('product_qty_detail.product_detailed_qty_form').id,
                'res_model': 'product.detailed.qty',
                'type': 'ir.actions.act_window',
                'res_id': detail_qty_id.id,
                'target': 'current'}
