# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from datetime import datetime

from odoo import api, fields, models, exceptions, _


class ConfirmTransfer(models.TransientModel):
    _name = 'confirm.transfer'

    confirmation = fields.Char('')

    def confirm_transfer(self):
        return {'type': 'ir.actions.client', 'tag': 'reload'}


class StockQuantLine(models.TransientModel):
    _name = 'stock.quant.line'
    _description = 'Stock Quant Line'

    wizard_id = fields.Many2one('transfer.stock.picking', string='Wizard')
    product_id = fields.Many2one('product.product', string='Product')
    create_date = fields.Datetime('Created On')
    location_id = fields.Many2one('stock.location', string='Location')
    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number')
    inventory_quantity = fields.Float('On Hand Quantity')
    reserved_quantity = fields.Float('Reserved Quantity')
    currency_id = fields.Many2one('res.currency')
    value = fields.Monetary('Value')


class TransferStockMoveLine(models.TransientModel):
    _name = 'transfer.stock.picking.line'
    _description = 'Transfer Stock Picking Line'

    wizard_id = fields.Many2one('transfer.stock.picking', string='Wizard')
    product_id = fields.Many2one('product.product', string='Product',
                                 domain=lambda self: self.search_product())
    location_id = fields.Many2one('stock.location', 'Source Location',
                                  domain=lambda self: self.search_source_location())
    location_dest_id = fields.Many2one('stock.location', 'Destination Location',
                                       domain=lambda self: self.search_destination_location())
    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number',
                             domain=lambda self: self.search_lots())
    reserved_qty = fields.Float('Reserved')
    done_qty = fields.Float('Done')
    lots_visible = fields.Boolean(compute='_compute_lots_visible')

    @api.depends('location_id', 'location_dest_id', 'wizard_id.picking_type_id')
    def _compute_lots_visible(self):
        context = self._context
        product_id = []
        if context.get('active_model') == 'product.template':
            product_id = self.env['product.template'].browse(context.get('active_id'))
        elif context.get('active_model') == 'product.product':
            product_id = self.env['product.product'].browse(context.get('active_id'))
        if product_id.tracking == 'none':
            self.lots_visible = False
        if product_id.tracking in ('lot', 'serial'):
            self.lots_visible = True

    @api.onchange('product_id')
    def onchange_product_id(self):
        context = self._context
        stock_quant_ids = []
        if context.get('active_model') == 'product.template':
            product_id = self.env['product.template'].browse(context.get('active_id'))
            stock_quant_ids = self.env['stock.quant'].search(
                [('product_tmpl_id', '=', product_id.id)])
        elif context.get('active_model') == 'product.product':
            product_id = self.env['product.product'].browse(context.get('active_id'))
            stock_quant_ids = self.env['stock.quant'].search([('product_id', '=', product_id.id)])
        if self.wizard_id.product_visible and self.product_id:
            for each in stock_quant_ids:
                if self.product_id == each.product_id and each.quantity > 0.0:
                    self.location_id = each.location_id
                    break

    @api.onchange('location_id')
    def onchange_location_id(self):
        context = self._context
        stock_quant_ids = []
        product_id = []
        if context.get('active_model') == 'product.template':
            product_id = self.env['product.template'].browse(context.get('active_id'))
            stock_quant_ids = self.env['stock.quant'].search(
                [('product_tmpl_id', '=', product_id.id)])
            if not self.wizard_id.product_visible:
                self.product_id = product_id.product_variant_id.id
        elif context.get('active_model') == 'product.product':
            product_id = self.env['product.product'].browse(context.get('active_id'))
            stock_quant_ids = self.env['stock.quant'].search([('product_id', '=', product_id.id)])
            if not self.wizard_id.product_visible:
                self.product_id = product_id.id
        if self.wizard_id.product_visible and self.product_id and self.location_id:
            current_list = []
            quant_list = []
            current_list.append(
                {'product_id': self.product_id.id, 'location_id': self.location_id.id})
            for each in stock_quant_ids:
                if each.quantity > 0.00:
                    quant_list.append(
                        {'product_id': each.product_id.id, 'location_id': each.location_id.id})
            for content in current_list:
                if content not in quant_list:
                    raise exceptions.Warning(
                        _('Selected product variant does not exist in the selected source location.\n Please check your transfer details.\n\n Product: %(product)s \n Source Location: %(location)s.')
                        % {'product': self.product_id.display_name,
                           'location': self.location_id.complete_name})
        if self.location_id:
            for each in stock_quant_ids:
                if each.location_id == self.location_id and each.product_id == self.product_id:
                    if product_id.tracking == 'none':
                        self.reserved_qty = each.quantity - each.reserved_quantity
                    if product_id.tracking == 'lot':
                        self.lot_id = each.lot_id
                        self.reserved_qty = each.quantity - each.reserved_quantity
                        break
                    if product_id.tracking == 'serial':
                        if each.reserved_quantity == 0:
                            self.lot_id = each.lot_id
                            self.reserved_qty = each.quantity - each.reserved_quantity
                            break

    @api.model
    def search_product(self):
        context = self._context
        stock_quant_ids = []
        search_content = []
        product_id = []
        if context.get('active_model') == 'product.template':
            product_id = self.env['product.template'].browse(context.get('active_id'))
            stock_quant_ids = self.env['stock.quant'].search(
                [('product_tmpl_id', '=', product_id.id)])
            if product_id.product_variant_ids and stock_quant_ids:
                for each in stock_quant_ids:
                    if each.quantity > 0.00:
                        search_content.append(each.product_id.id)
        elif context.get('active_model') == 'product.product':
            product_id = self.env['product.product'].browse(context.get('active_id'))
            stock_quant_ids = self.env['stock.quant'].search([('product_id', '=', product_id.id)])
            if stock_quant_ids:
                for each in stock_quant_ids:
                    if each.quantity > 0.00:
                        search_content.append(each.product_id.id)
        return [('id', 'in', search_content)]

    @api.model
    def search_source_location(self):
        context = self._context
        stock_quant_ids = []
        search_content = []
        if context.get('active_model') == 'product.template':
            product_id = self.env['product.template'].browse(context.get('active_id'))
            stock_quant_ids = self.env['stock.quant'].search(
                [('product_tmpl_id', '=', product_id.id)])
        elif context.get('active_model') == 'product.product':
            product_id = self.env['product.product'].browse(context.get('active_id'))
            stock_quant_ids = self.env['stock.quant'].search([('product_id', '=', product_id.id)])
        if stock_quant_ids:
            for each in stock_quant_ids.filtered(lambda l: l.location_id.usage in 'internal'):
                if each.quantity > 0.00:
                    search_content.append(each.location_id.id)
        return [('id', 'in', search_content)]

    @api.model
    def search_destination_location(self):
        context = self._context
        search_content = []
        internal_location_ids = self.env['stock.location'].search([('usage', '!=', 'view')])
        for each in internal_location_ids:
            search_content.append(each.id)
        return [('id', 'in', search_content)]

    @api.model
    def search_lots(self):
        context = self._context
        stock_quant_ids = []
        search_content = []
        if context.get('active_model') == 'product.template':
            product_id = self.env['product.template'].browse(context.get('active_id'))
            stock_quant_ids = self.env['stock.quant'].search(
                [('product_tmpl_id', '=', product_id.id)])
        elif context.get('active_model') == 'product.product':
            product_id = self.env['product.product'].browse(context.get('active_id'))
            stock_quant_ids = self.env['stock.quant'].search([('product_id', '=', product_id.id)])
        for each in stock_quant_ids:
            if each.quantity > 0.00:
                search_content.append(each.lot_id.id)
        return [('id', 'in', search_content)]

    @api.onchange('done_qty')
    def onchange_done_qty(self):
        context = self._context
        product_id = []
        if context.get('active_model') == 'product.template':
            product_id = self.env['product.template'].browse(context.get('active_id'))
        elif context.get('active_model') == 'product.product':
            product_id = self.env['product.product'].browse(context.get('active_id'))

        if product_id.tracking == 'serial' and self.done_qty > 1:
            warning = {'title': _('Warning'),
                       'message': 'You can only process 1.0 Units of products with unique serial '
                                  'number.'}
            self.done_qty = ''
            return {'warning': warning}
        if product_id.tracking in ('none', 'lot') and self.done_qty > self.reserved_qty:
            warning = {'title': _('Warning'),
                       'message': 'You cannot process more than the available quantity.'}
            self.done_qty = ''
            return {'warning': warning}

    @api.onchange('lot_id')
    def onchange_lot_id(self):
        if self.lot_id:
            context = self._context
            stock_quant_ids = []
            product_id = []
            if context.get('active_model') == 'product.template':
                product_id = self.env['product.template'].browse(context.get('active_id'))
                stock_quant_ids = self.env['stock.quant'].search(
                    [('product_tmpl_id', '=', product_id.id),
                     ('location_id', '=', self.location_id.id)])
            elif context.get('active_model') == 'product.product':
                product_id = self.env['product.product'].browse(context.get('active_id'))
                stock_quant_ids = self.env['stock.quant'].search(
                    [('product_id', '=', product_id.id),
                     ('location_id', '=', self.location_id.id)])
            current_list = []
            quant_list = []
            current_list.append({'location_id': self.location_id.id, 'lot_id': self.lot_id.id})
            if product_id.tracking in ('serial', 'lot'):
                for each in stock_quant_ids:
                    if each.quantity > 0.0:
                        quant_list.append({'location_id': each.location_id.id,
                                           'lot_id': each.lot_id.id})
                    if self.lot_id == each.lot_id:
                        self.reserved_qty = each.quantity - each.reserved_quantity
                for content in current_list:
                    if content not in quant_list:
                        raise exceptions.Warning(
                            _('Selected serial does not exist in the selected source location.\n '
                              'Please check your transfer details.\n\n Lot number: %(lot)s \n '
                              'Source Location: %(location)s.')
                            % {'lot': self.lot_id.name, 'location': self.location_id.complete_name})


class TransferStock(models.TransientModel):
    _name = 'transfer.stock.picking'
    _description = 'Transfer Stock Picking'

    product_trasfer_moves = fields.One2many('transfer.stock.picking.line', 'wizard_id', 'Moves')
    stock_quant_lines = fields.One2many('stock.quant.line', 'wizard_id', 'Stock Onhand')
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Types',
                                      domain=lambda self: self.search_internal_location())
    product_visible = fields.Boolean(compute='_compute_product_visible')

    @api.depends('picking_type_id')
    def _compute_product_visible(self):
        context = self._context
        product_id = []
        if context.get('active_model') == 'product.template':
            product_id = self.env['product.template'].browse(context.get('active_id'))
        elif context.get('active_model') == 'product.product':
            product_id = self.env['product.product'].browse(context.get('active_id'))
        if product_id.attribute_line_ids:
            self.product_visible = True
        else:
            self.product_visible = False

    @api.model
    def search_internal_location(self):
        context = self._context
        search_content = []
        picking_type_ids = self.env['stock.picking.type'].search([('code', '=', 'internal')])
        for each in picking_type_ids:
            search_content.append(each.id)
        return [('id', 'in', search_content)]

    @api.model
    def default_get(self, fields):
        res = super(TransferStock, self).default_get(fields)
        context = self._context
        if context.get('active_model') == 'product.template':
            product_id = self.env['product.template'].browse(context.get('active_id'))
            res.update({'picking_type_id': 5})
            product_quant_list = []
            if product_id.product_variant_ids.stock_quant_ids:
                for quant in product_id.product_variant_ids.stock_quant_ids.filtered(
                        lambda l: l.location_id.usage in 'internal'):
                    if quant.quantity > 0.00:
                        product_quant_list.append({
                            'create_date': quant.create_date,
                            'product_id': quant.product_id.id,
                            'location_id': quant.location_id.id,
                            'lot_id': quant.lot_id.id,
                            'inventory_quantity': quant.quantity,
                            'reserved_quantity': quant.reserved_quantity,
                            'currency_id': product_id.currency_id.id,
                            'value': quant.value,
                        })
                res.update({'stock_quant_lines': [(0, 0, each) for each in product_quant_list]})
                return res
            else:
                return res
        elif context.get('active_model') == 'product.product':
            product_id = self.env['product.product'].browse(context.get('active_id'))
            res.update({'picking_type_id': 5})
            product_quant_list = []
            if product_id.stock_quant_ids:
                for quant in product_id.stock_quant_ids:
                    if quant.quantity > 0.00:
                        product_quant_list.append({
                            'create_date': quant.create_date,
                            'location_id': quant.location_id.id,
                            'lot_id': quant.lot_id.id,
                            'inventory_quantity': quant.quantity,
                            'reserved_quantity': quant.reserved_quantity,
                            'currency_id': product_id.currency_id.id,
                            'value': quant.value,
                        })
                res.update({'stock_quant_lines': [(0, 0, each) for each in product_quant_list]})
                return res
            else:
                return res

    def create_transfer(self):
        context = self._context
        product_id = []
        if context.get('active_model') == 'product.template':
            product_id = self.env['product.template'].browse(context.get('active_id'))
        elif context.get('active_model') == 'product.product':
            product_id = self.env['product.product'].browse(context.get('active_id'))
        picking = self.env['stock.picking'].create({
            'picking_type_id': self.picking_type_id.id,
            'location_id': 8,
            'location_dest_id': 8,
            'date_done': datetime.today(),
            'state': 'done'})

        for each in self.product_trasfer_moves:
            if each.done_qty != 0:
                move_id = self.env['stock.move'].create({
                    'picking_id': picking.id,
                    'name': picking.name,
                    'location_id': each.location_id.id,
                    'location_dest_id': each.location_dest_id.id,
                    'product_id': each.product_id.id,
                    'product_uom': product_id.uom_id.id,
                    'product_uom_qty': each.done_qty,
                    'picking_type_id': self.picking_type_id.id,
                    'state': 'done'})

                self.env['stock.move.line'].create({
                    'move_id': move_id.id,
                    'picking_id': picking.id,
                    'product_id': each.product_id.id,
                    'product_uom_id': product_id.uom_id.id,
                    'location_id': each.location_id.id,
                    'location_dest_id': each.location_dest_id.id,
                    'qty_done': each.done_qty,
                    'lot_id': each.lot_id.id,
                    'state': 'done'})

                confirmation = """Transfer(s) completed. Reference #""" + str(
                    picking.name) + """."""
                value = self.env['confirm.transfer'].sudo().create({'confirmation': confirmation})
            else:
                raise exceptions.Warning(_('You cannot process 0 Units of done quantity'))
        return {'name': 'Confirmation',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'confirm.transfer',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'res_id': value.id}
