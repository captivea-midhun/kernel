# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from datetime import datetime

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class Inventory(models.Model):
    _inherit = "stock.inventory"
    _description = "Inventory"
    _order = 'sequence'

    @api.depends('move_ids')
    def _compute_move_lines(self):
        for adj_rec in self:
            adj_rec.update(
                {'move_line_ids': adj_rec.move_ids.move_line_ids and
                                  adj_rec.move_ids.move_line_ids.ids or False})

    sequence = fields.Char(string='Inventory Number', copy=False, readonly=True)
    move_line_ids = fields.One2many('stock.move.line', 'inventory_id', string='Product Moves',
                                    compute='_compute_move_lines')
    validated_user = fields.Many2one('res.users', string='Validated By')

    @api.model
    def create(self, values):
        if values.get('sequence', _('New')) == _('New'):
            values['sequence'] = self.env['ir.sequence'].next_by_code('stock.inventory') or _('New')
        return super(Inventory, self).create(values)

    def action_validate(self):
        for rec in self:
            rec.validated_user = self.env.user.id
        return super(Inventory, self.with_context(inventory_adjustment=True)).action_validate()


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    net_qty = fields.Float(string='Net On Hand', compute='_get_net_on_hand_qty')

    def _get_net_on_hand_qty(self):
        """ Search Manufacturing Orders, which has reserved some quantity"""
        for rec in self:
            domain = [('product_id', '=', rec.product_id.id),
                      ('production_id', '!=', False),
                      ('production_id.state', 'not in',
                       ['draft', 'done', 'cancel']),
                      ('product_uom_qty', '>', 0),
                      ('move_id.raw_material_production_id', '!=', False)]
            if rec.product_id.tracking != 'none':
                domain += [('lot_id', '=', rec.prod_lot_id.id)]
            sm_lime_ids = self.env['stock.move.line'].search(domain)
            sm_ids = sm_lime_ids.mapped('move_id')
            reserve_qty = sum(sm_ids.mapped('reserved_availability'))
            rec.net_qty = rec.product_id.qty_available - reserve_qty


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    prod_type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Inventory Product')], string='Product Type')

    @api.model_create_multi
    def create(self, vals):
        res = super(StockMoveLine, self).create(vals)
        for rec in res:
            rec.prod_type = rec.product_id.type
            # for update date base on Scheduled Date
            move_id = rec.move_id
            if move_id.inventory_id and move_id.inventory_id.accounting_date and \
                    move_id.state != 'done':
                rec.date = datetime.combine(move_id.inventory_id.accounting_date,
                                            datetime.now().time())
            if move_id and move_id.quant_id and move_id.quant_id.description and \
                    move_id.quant_id.accounting_date and move_id.qty_adjust:
                rec.date = datetime.combine(move_id.quant_id.accounting_date, datetime.now().time())
        return res

    def _action_done(self):
        """ Update date in stock move lines based on IA and stock quant accounting date."""

        # Stock move line is deleted after super call to handle this flag is used.
        flag = False
        if self.filtered(lambda x: x.move_id.inventory_id or x.move_id.qty_adjust):
            flag = True
        rec = super(StockMoveLine, self)._action_done()

        if flag:
            for line in self:
                if line.move_id.inventory_id and line.state != 'done' and \
                        line.move_id.inventory_id.accounting_date:
                    line.date = datetime.combine(line.move_id.inventory_id.accounting_date,
                                                 datetime.now().time())
                if line.move_id and line.move_id.quant_id and line.move_id.quant_id.description \
                        and line.move_id.quant_id.accounting_date and line.move_id.qty_adjust:
                    line.date = datetime.combine(line.move_id.quant_id.accounting_date,
                                                 datetime.now().time())
        return rec

    @api.depends('move_id')
    def _compute_move_lines(self):
        for ml_rec in self:
            if ml_rec.move_id.inventory_id:
                ml_rec.update({'inventory_id': ml_rec.move_id.inventory_id.id or False})

    inventory_id = fields.Many2one('stock.inventory', string='Inventory Adjustment')


class StockMove(models.Model):
    _inherit = "stock.move"

    prod_type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Inventory Product')], string='Product Type')

    def create(self, vals):
        res = super(StockMove, self).create(vals)
        for rec in res:
            rec.prod_type = rec.product_id.type
        return res

    # for update date base on Scheduled Date
    def write(self, vals):
        for mv in self:
            if mv.inventory_id and mv.inventory_id.accounting_date and \
                    mv.state != 'done':
                adj_date = datetime.combine(mv.inventory_id.accounting_date, datetime.now().time())
                vals['date_expected'] = adj_date
                vals['date'] = adj_date
            if mv.quant_id and mv.quant_id.description and mv.quant_id.accounting_date and \
                    mv.qty_adjust:
                sm_date = datetime.combine(mv.quant_id.accounting_date, datetime.now().time())
                vals['date_expected'] = sm_date
                vals['date'] = sm_date
        move = super(StockMove, self).write(vals)
        return move

    def _get_accounting_data_for_valuation(self):
        self.ensure_one()
        default_adjustment_account_id = self.env['ir.config_parameter'].sudo() \
            .get_param('inventory_adjustment_extended.default_adjustment_account_id')
        if self._context.get('inventory_adjustment', False):
            accounts_data = \
                self.product_id.product_tmpl_id.get_product_accounts()
            if self.location_id.valuation_out_account_id:
                acc_src = self.location_id.valuation_out_account_id.id
            else:
                if default_adjustment_account_id and \
                        default_adjustment_account_id.isdigit():
                    acc_src = int(default_adjustment_account_id)
                else:
                    acc_src = accounts_data['expense'].id

            if self.location_dest_id.valuation_in_account_id:
                acc_dest = self.location_dest_id.valuation_in_account_id.id
            else:
                if default_adjustment_account_id and \
                        default_adjustment_account_id.isdigit():
                    acc_dest = int(default_adjustment_account_id)
                else:
                    acc_dest = accounts_data['expense'].id

            acc_valuation = accounts_data.get('stock_valuation', False)
            if acc_valuation:
                acc_valuation = acc_valuation.id
            if not accounts_data.get('stock_journal', False):
                raise UserError(_(
                    'You don\'t have any stock journal defined on your '
                    'product category, check if you have installed a chart of '
                    'accounts.'))
            if not acc_src:
                raise UserError(_(
                    'Cannot find a stock input account for the product %s. '
                    'You must define one on the product category, or on the '
                    'location, before processing this operation.') % (
                                    self.product_id.display_name))
            if not acc_dest:
                raise UserError(_(
                    'Cannot find a stock output account for the product %s. '
                    'You must define one on the product category, or on the '
                    'location, before processing this operation.') % (
                                    self.product_id.display_name))
            if not acc_valuation:
                raise UserError(_(
                    'You don\'t have any stock valuation account defined on '
                    'your product category. You must define one before '
                    'processing this operation.'))
            journal_id = accounts_data['stock_journal'].id
            return journal_id, acc_src, acc_dest, acc_valuation
        return super(StockMove, self)._get_accounting_data_for_valuation()
