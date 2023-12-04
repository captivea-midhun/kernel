# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import api, models


class MrpStockReport(models.TransientModel):
    _inherit = 'stock.traceability.report'

    def _make_dict_move(self, level, parent_id, move_line, unfoldable=False):
        data = super(MrpStockReport, self)._make_dict_move(level, parent_id, move_line, unfoldable)
        data[0]['lot_editable'] = move_line.location_dest_id.usage == 'production'
        data[0]['slot'] = move_line.slot
        data[0]['slot_name'] = move_line.slot
        return data

    @api.model
    def _final_vals_to_lines(self, final_vals, level):
        lines = super(MrpStockReport, self)._final_vals_to_lines(final_vals, level)
        for index, data in enumerate(final_vals):
            lines[index]['lot_editable'] = data.get('lot_editable')
            lines[index]['slot_name'] = data.get('slot_name', False)
            lines[index]['columns'].insert(4, data.get('slot', False))
        return lines
