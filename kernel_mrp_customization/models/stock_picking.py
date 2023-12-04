# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    bista_incoming_picking_group_id = fields.Many2one(
        'procurement.group', string='Procurement Group Incoming Shipment#',
        help="Subcontractiong Incoming Shipment Procurement Group")

    def button_validate(self):
        subcontract_moves = self.move_ids_without_package.filtered(
            lambda mv: mv.is_subcontract)
        if not subcontract_moves:
            return super(StockPicking, self).button_validate()
        subcontracted_productions = self._get_subcontracted_productions()
        for production in subcontracted_productions:
            Picking_ids = self.search([
                ('group_id', '=', production.procurement_group_id.id),
                ('picking_type_id.code', '=', 'outgoing')])
            if Picking_ids and not any(pick.state == 'done' for pick in Picking_ids):
                raise ValidationError(_(
                    'You can not validate incoming shipment until subcontracti'
                    'ng Delivery Order: %s of Subcontract Order: %s is done.'
                ) % (Picking_ids.name, production.name))
        return super(StockPicking, self).button_validate()

    def action_view_incomming_picking(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        if self.bista_incoming_picking_group_id:
            action['domain'] = [('group_id', '=', self.bista_incoming_picking_group_id.id)]
            return action
