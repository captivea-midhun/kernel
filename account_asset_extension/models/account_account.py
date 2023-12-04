# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from datetime import datetime
from itertools import groupby

from odoo import models, fields
from odoo.tools import float_round


class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_cip = fields.Boolean(string="Is CIP")

    def get_move_line_data(self, start_date, end_date):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        result = []
        move_obj = self.env['account.move.line']
        currency = self.env.user.currency_id

        move_lines = move_obj.search(
            [('account_id', '=', self.id),
             ('date', '<=', end_date),
             ('analytic_tag_ids', '!=', False)], order='date asc', )
        # Above domain filter is not working correctly ('analytic_tag_ids', '!=', False)
        # Requested Ticket Number: 5,300 :Issue: Error message when running CIP report
        move_lines = move_lines.filtered(lambda x: x.analytic_tag_ids)
        for tag_id, line in groupby(
                sorted(move_lines, key=lambda l: l.analytic_tag_ids.ids[0]),
                key=lambda l: l.analytic_tag_ids.ids[0]):

            mv_lines = move_obj.concat(*line)

            prior_move_lines = mv_lines.filtered(
                lambda l: l.date < start_date and tag_id in l.analytic_tag_ids.ids)

            lines = mv_lines.filtered(
                lambda l: l.date >= start_date and l.date <= end_date)

            beginning_value = sum(prior_move_lines.mapped('debit')) - sum(
                prior_move_lines.mapped('credit'))
            beginning_value = float_round(
                beginning_value, precision_rounding=currency.rounding)

            disposed = sum(prior_move_lines.mapped('credit')) + sum(
                lines.mapped('credit')) or 0.00
            disposed = float_round(
                disposed, precision_rounding=currency.rounding)

            current_value = sum(lines.mapped('debit')) or 0.00
            current_value = float_round(
                current_value, precision_rounding=currency.rounding)

            net_value = (beginning_value + current_value) - disposed
            net_value = float_round(
                net_value, precision_rounding=currency.rounding)
            if lines:
                analytic_tag = lines.mapped('analytic_tag_ids').mapped('name')[0]
            elif prior_move_lines:
                analytic_tag = prior_move_lines.mapped('analytic_tag_ids').mapped('name')[0]
            else:
                analytic_tag = 'Undefined Tag'

            if net_value > 0.00:
                result.append(
                    {'date': lines and lines.sorted(key=lambda l: l.date)[0].date or
                             prior_move_lines.sorted(key=lambda l: l.date)[-1].date,
                     'cip_account': self.name,
                     'analytic_tag': analytic_tag,
                     'current_value': current_value,
                     'beginning_value': beginning_value,
                     'end_cost': net_value,
                     'disposed': disposed,
                     'beg_acc_amt': 0.00,
                     'depreciation': 0.00,
                     'disposal': 0.00,
                     'end_acc_dep': 0.00,
                     'net_value': 0.00, })
        return sorted(result, key=lambda i: i['date'])
