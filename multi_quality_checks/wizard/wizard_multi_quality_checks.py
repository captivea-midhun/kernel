# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class WizardQualityChecks(models.TransientModel):
    _name = 'wizard.multi.quality.checks'
    _description = "Quality Checks"

    picking_id = fields.Many2one('stock.picking')
    location_dest_id = fields.Many2one('stock.location', string="Destination Location")
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.user.company_id)
    lines = fields.One2many('wizard.multi.quality.checks.lines', 'quality_check_id')

    @api.model
    def default_get(self, fields_lst):
        res = super(WizardQualityChecks, self).default_get(fields_lst)
        ctx = dict(self.env.context)
        picking_id = ctx.get('active_ids', [])
        if not picking_id:
            return res
        picking_id = self.env['stock.picking'].browse(picking_id)
        lines = []
        checks = picking_id.check_ids.filtered(
            lambda check: check.quality_state == 'none')

        for check in checks:
            move_id = picking_id.move_lines.filtered(
                lambda
                    ml: ml.product_id.id == check.product_id.id and ml.purchase_line_id.id == check.purchase_line_id.id)
            lines.append(
                (0, 0,
                 {'product_id': check.product_id.id, 'product_tracking': check.product_id.tracking,
                  'is_pass': True,
                  'qty_done':
                      1 if check.product_id.tracking in ('serial', 'lot_serial')
                      else move_id and move_id.product_uom_qty - move_id.quantity_done or 0.00,
                  'location_dest_id': picking_id.location_dest_id.id,
                  'check_id': check.id,
                  'move_id': move_id and move_id.id or False, }))
        res.update({'lines': lines,
                    'location_dest_id': picking_id.location_dest_id.id,
                    'picking_id': picking_id.id})
        return res

    def action_do_pass(self, pass_check_ids):
        for check in pass_check_ids:
            check.do_pass()
        return True

    def action_do_fail(self, fail_check_ids):
        for check in fail_check_ids:
            check.do_fail()
        return True

    def check_duplicate_lot(self, picking_id):
        for line in self.lines.filtered(
                lambda l: l.product_id.tracking in ('serial', 'lot_serial')):
            result = line.search_count([('quality_check_id', '=', self.id),
                                        ('lot_id', '=', line.lot_id.id),
                                        ('product_id', '=', line.product_id.id)])
            if result > 1:
                raise ValidationError(
                    _("You can not choose two same serial number %s .") % (line.lot_id.name))
            move_line = picking_id.move_line_ids.filtered(
                lambda ml: ml.lot_id and ml.lot_id.id == line.lot_id.id
                           and ml.product_id.tracking in ('serial', 'lot_serial')
                           and ml.product_id.id == line.product_id.id)
            if move_line:
                raise ValidationError(
                    _("You can not assign %s serial number because this serial number already"
                      " assigned to %s product.") % (line.lot_id.name,
                         move_line[0].product_id.display_name))

    def check_lot_quantity(self):
        for line in self.lines.filtered(
                lambda l: l.product_id.tracking in ('serial', 'lot_serial')):
            res = line.product_id._compute_quantities_dict(
                line.lot_id.id, owner_id=None, package_id=None, from_date=False, to_date=False)
            if not res:
                return True
            if res.get(line.product_id.id).get('qty_available') > 0.00:
                raise ValidationError(_(
                    'A serial number %s can have only one quantity %s product.'
                ) % (line.lot_id.name, line.product_id.display_name))

    def action_create_move_lines(self, picking_id):
        for line in self.lines:
            lot_id = line.lot_id
            line.check_id.update({'lot_id': lot_id.id or False, 'comments': line.comments})
            if line.product_tracking == 'none' and (
                    line.move_id.quantity_done + line.qty_done) != line.move_id.product_uom_qty:
                if line.move_id.quantity_done:
                    done_qty = line.move_id.quantity_done + line.qty_done
                    rem_qty = line.move_id.product_uom_qty - done_qty
                else:
                    done_qty = sum(picking_id.check_ids.filtered(
                        lambda check: check.quality_state != 'none' and check.product_id.id ==
                                      line.product_id.id).mapped('qty'))
                    rem_qty = done_qty - line.qty_done
                line.check_id.update({'qty': line.qty_done})
                copy_check_id = line.check_id.copy()
                copy_check_id.update({'qty': rem_qty, 'lot_id': False, 'comments': False})

            # Create Move Line
            line.move_id.update(
                {'move_line_ids': [
                    (0, 0, {'lot_id': lot_id.id or False,
                            'lot_name': lot_id.name,
                            'qty_done': line.qty_done,
                            'product_id': line.product_id.id,
                            'product_uom_id': line.product_id.uom_id.id,
                            'location_id': line.move_id.location_id.id,
                            'location_dest_id': line.location_dest_id.id,
                            'picking_id': picking_id.id})]})
        return True

    def action_do_proceed(self):
        if not self.lines:
            return {'type': 'ir.actions.act_window_close'}
        if any(self.lines.filtered(lambda l: not l.location_dest_id)):
            raise UserError(_('Please define destination location.'))

        # If no lots when needed, raise error
        picking_type = self.picking_id.picking_type_id
        if picking_type.use_create_lots or picking_type.use_existing_lots:
            for line in self.lines.filtered(
                    lambda l: l.product_id.tracking != 'none' and not l.lot_id):
                raise UserError(_(
                    'You need to supply a Lot/Serial number for product %s.'
                ) % line.product_id.display_name)

        self.check_lot_quantity()
        self.check_duplicate_lot(self.picking_id)
        self.action_do_pass(self.lines.filtered(lambda l: l.is_pass).mapped('check_id'))
        self.action_do_fail(self.lines.filtered(lambda l: not l.is_pass).mapped('check_id'))
        self.action_create_move_lines(self.picking_id)
        return {'type': 'ir.actions.act_window_close'}


class WizardQualityCheckslines(models.TransientModel):
    _name = 'wizard.multi.quality.checks.lines'
    _description = "Quality Checks Lines"

    product_id = fields.Many2one('product.product')
    qty_done = fields.Float(string="Quantity")
    product_tracking = fields.Selection([('serial', 'By Unique Serial Number'),
                                         ('lot', 'By Lots'),
                                         ('lot_serial', 'By Lots - Unique Serial Number'),
                                         ('none', 'No Tracking')])
    is_pass = fields.Boolean()
    move_id = fields.Many2one('stock.move')
    location_dest_id = fields.Many2one('stock.location', string="Location")
    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number')
    comments = fields.Char()
    check_id = fields.Many2one('quality.check', string="Quality Check")
    quality_check_id = fields.Many2one('wizard.multi.quality.checks', string="Quality Check Ref.")
