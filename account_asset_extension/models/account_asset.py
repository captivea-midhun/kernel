# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from datetime import datetime

from odoo import models, fields, api
from odoo.tools import float_round


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_cip_move = fields.Boolean(string="CIP Move?", copy=False, default=False)

    def unlink(self):
        """Unlink asset journal entries"""
        for move in self:
            if self._context.get('active_model') == "account.asset" and \
                    move.state == 'cancel' and \
                    self.env.user.has_group(
                        'account_asset_extension.group_asset_journal_entry_delete'):
                self = self.with_context(force_delete=True)
        return super(AccountMove, self).unlink()


class AccountAsset(models.Model):
    _inherit = "account.asset"

    depreciation_move_ids = fields.One2many(
        'account.move', 'asset_id', string='Depreciation Lines',
        domain=[('is_cip_move', '=', False)],
        readonly=True, states={'draft': [('readonly', False)],
                               'open': [('readonly', False)],
                               'paused': [('readonly', False)]})
    disposal_date = fields.Date(readonly=True, states={'draft': [('readonly', False)]},
                                compute="_compute_disposal_date", store=True)

    @api.depends('depreciation_move_ids.date', 'state')
    def _compute_disposal_date(self):
        for asset in self:
            if asset.state == 'close':
                dates = asset.depreciation_move_ids.filtered(lambda m: m.date).mapped('date')
                asset.disposal_date = dates and max(dates)
            else:
                asset.disposal_date = False

    def open_entries(self):
        res = super(AccountAsset, self).open_entries()
        move_ids = self.depreciation_move_ids
        move_ids |= self.env['account.move'].search([
            ('asset_id', '=', self.id), ('is_cip_move', '=', True)])
        res['domain'] = [('id', 'in', move_ids.ids)]
        return res

    def validate(self):
        res = super(AccountAsset, self).validate()
        move_obj = self.env['account.move']
        move_vals = move_obj.with_context(type='entry').default_get(
            ['journal_id', 'type', 'date', 'currency_id'])
        for asset in self:
            if not asset.original_move_line_ids or not asset.model_id:
                continue
            move_lines = []
            move_vals.update({'asset_id': asset.id, 'is_cip_move': True,
                              'ref': asset.name, 'auto_post': True})
            # Credit Lines
            move_lines.append(
                (0, 0, {'account_id': asset.model_id.account_asset_id.id,
                        'credit': 0.00,
                        'name': asset.name,
                        'debit': asset.original_value,
                        'analytic_account_id': asset.account_analytic_id and asset.account_analytic_id.id or False,
                        'analytic_tag_ids': asset.analytic_tag_ids and [
                            (6, 0, asset.analytic_tag_ids.ids)] or [], }))
            # Debit Lines
            for line in asset.original_move_line_ids:
                move_lines.append(
                    (0, 0, {'account_id': line.account_id.id,
                            'credit': line.debit,
                            'debit': 0.00,
                            'name': line.name,
                            'analytic_account_id': line.analytic_account_id and line.analytic_account_id.id or False,
                            'analytic_tag_ids': line.analytic_tag_ids and [
                                (6, 0, line.analytic_tag_ids.ids)] or [], }))
            move_vals.update({'line_ids': move_lines})
            move_obj.create(move_vals)
        return res

    def get_category_data(self, category_id, move_ids, start_date, end_date):
        context = dict(self._context) or {}
        hide_zero_lines = context.get('zero_lines', False)
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        category_data = []
        vendor_bill_moves = self.env['account.move'].search([('type','=','in_invoice'),('purchase_order_id','!=',None)])
        for move in move_ids.filtered(
                lambda mv: (not category_id and not mv.asset_id.model_id) or (
                        category_id and mv.asset_id.model_id and mv.asset_id.model_id.id == category_id.id)):
            acc_move_search = vendor_bill_moves.filtered(lambda mv: any(ass.id == move.asset_id.id for ass in mv.asset_ids))
            # print ("acc_move_search --->>>", acc_move_search)
            po_name = ''
            if acc_move_search:
                if len(acc_move_search) == 1:
                    po_name = acc_move_search.purchase_order_id.name if acc_move_search.purchase_order_id else acc_move_search.purchase_id.name
                    if not po_name:
                        po_name = acc_move_search.invoice_origin
                if len(acc_move_search) > 1:
                    po_names_list = []
                    for acc_move in acc_move_search:
                        po_names_list_add = acc_move.purchase_order_id.name if acc_move.purchase_order_id else acc_move.purchase_id.name
                        if not po_names_list_add:
                            po_names_list_add = acc_move.invoice_origin
                        po_names_list.append(po_names_list_add)
                    if po_names_list and False not in po_names_list:
                        po_name = ','.join(po_names_list)
            if not po_name or (po_name and "PO" not in po_name):
                po_name = ''
            # if po_name and "PO" not in po_name:
            #     po_name = ''
            beg_acc_dep_cost = disposed = disposal = purchase_value = orignal_value = 0.00
            disposed_move_id = max(move.asset_id.depreciation_move_ids.filtered(lambda dmv: dmv.state == 'posted').sorted(key='id',reverse=True))
            currency = move.asset_id.currency_id
            if move.asset_id.acquisition_date < start_date:
                orignal_value = float_round(
                    move.asset_id.original_value, precision_rounding=currency.rounding)
            else:
                purchase_value = float_round(
                    move.asset_id.original_value, precision_rounding=currency.rounding)

            prior_month_move_ids = move.asset_id.depreciation_move_ids.filtered(
                lambda mv: mv.date < start_date and mv.state == 'posted')
            if prior_month_move_ids:
                beg_acc_dep_cost = prior_month_move_ids[0].asset_depreciated_value
            beg_acc_dep_cost = float_round(
                beg_acc_dep_cost, precision_rounding=currency.rounding)
            if move.asset_id.state == 'close' and move.asset_id.disposal_date:
                if move.asset_id.disposal_date.year == end_date.year and move.asset_id.disposal_date <= end_date:
                    disposal_move_id = max(move.asset_id.depreciation_move_ids.filtered(lambda mv: mv.state == 'posted'))
                    disposal_mv_line_id = disposal_move_id.line_ids.filtered(
                        lambda l: l.account_id.id == move.asset_id.account_depreciation_id.id
                                  and l.debit != 0.00)
                    disposal = disposal_mv_line_id and disposal_mv_line_id[0].debit or 0.00
                    if disposal:
                        disposed = move.asset_id.original_value - disposal

            disposed = float_round(disposed, precision_rounding=currency.rounding)
            disposal = float_round(disposal, precision_rounding=currency.rounding)
            depreciation_cost = 0.00
            if move.asset_id.method_period == '12':
                current_month_move_id = move.asset_id.depreciation_move_ids.filtered(
                    lambda mv: mv.date.year == end_date.year and mv.state == 'posted')
            else:
                current_month_move_id = move.asset_id.depreciation_move_ids.filtered(
                    lambda mv: (mv.date >= start_date and mv.date <= end_date) and mv.state == 'posted')
            # if not current_month_move_id:
            #     current_month_move_id = move.asset_id.depreciation_move_ids.filtered(
            #         lambda mv: (mv.date >= start_date and mv.date <= end_date) and mv.id == disposed_move_id.id)
            if current_month_move_id:
                depreciation_cost = sum(current_month_move_id.filtered(
                    lambda mv: (mv.id != disposed_move_id.id and mv.date == move.asset_id.disposal_date)).mapped('amount_total')) #mv.date != move.asset_id.disposal_date and
                if len(current_month_move_id) == 1 and disposed_move_id == current_month_move_id and move.asset_id.state == 'open':
                    depreciation_cost = sum(current_month_move_id.filtered(
                    lambda mv: "Disposal" not in mv.ref).mapped('amount_total')) #mv.date != move.asset_id.disposal_date and
                if len(current_month_move_id) > 1 and move.asset_id.state == 'open':
                    depreciation_cost = sum(current_month_move_id.filtered(
                    lambda mv: "Disposal" not in mv.ref).mapped('amount_total'))
                if len(current_month_move_id) == 1 and disposed_move_id != current_month_move_id and move.asset_id.state == 'open':
                    depreciation_cost = sum(current_month_move_id.mapped('amount_total'))
                if len(current_month_move_id) > 1 and move.asset_id.state == 'close':
                    dup_dt_mv = self.env['account.move']
                    max_current_month_move_id = max(current_month_move_id.ids)
                    for cm in current_month_move_id:
                        # if cm.date == move.asset_id.disposal_date:
                        #     dup_dt_mv |= cm
                        if cm.id == max_current_month_move_id:
                            dup_dt_mv |= cm
                    if len(dup_dt_mv) >= 1:
                        dup_dt_mv = dup_dt_mv.sorted(key='id',reverse=True)[0].id
                        depreciation_cost = sum(current_month_move_id.filtered(
                        lambda mv: mv.id != dup_dt_mv).mapped('amount_total'))
            if current_month_move_id and len(current_month_move_id) == 1 and disposed_move_id == current_month_move_id and move.asset_id.state == 'close':
                depreciation_cost =  0.00
            if current_month_move_id and len(current_month_move_id) == 1 and disposed_move_id != current_month_move_id and move.asset_id.state == 'close':
                depreciation_cost = sum(current_month_move_id.mapped('amount_total'))
            if move.asset_id.original_value < 0:
                depreciation_cost = -depreciation_cost
            depreciation_cost = float_round(
                depreciation_cost, precision_rounding=currency.rounding)
            disposal = float_round(disposal, precision_rounding=currency.rounding)

            end_acc_dep_cost = (beg_acc_dep_cost + depreciation_cost) - disposal
            end_acc_dep_cost = float_round(
                end_acc_dep_cost, precision_rounding=currency.rounding)

            end_cost = (orignal_value + purchase_value) - disposed

            end_cost = float_round(end_cost, precision_rounding=currency.rounding)

            if disposal:
                net_value_cost = end_cost - disposal
            else:
                net_value_cost = (orignal_value + purchase_value) - end_acc_dep_cost

            net_value_cost = float_round(net_value_cost, precision_rounding=currency.rounding)

            if move.asset_id.method_period == '1':
                year = int(move.asset_id.method_number / 12)
                month = int(move.asset_id.method_number % 12)
                dep_year = '.'.join([str(year), str(month)])
            else:
                dep_year = str(move.asset_id.method_number)

            if move.asset_id.state == 'close':
                if not len(str(float_round(move.asset_id.original_value,precision_rounding=currency.rounding)).rsplit('.')[-1]) == 2:
                    original_value = round(float_round(move.asset_id.original_value,precision_rounding=currency.rounding), 2)
                else:
                    original_value = float_round(move.asset_id.original_value,precision_rounding=currency.rounding)
                move_line_id = move.asset_id.depreciation_move_ids.mapped('line_ids').filtered(
                    lambda ml: ml.account_id.id == move.asset_id.account_depreciation_id.id and \
                               ml.debit == original_value)
                if len(move_line_id) > 1:
                    disposed = float_round(move_line_id[1].debit, precision_rounding=currency.rounding)
                    disposal = float_round(move_line_id[1].debit, precision_rounding=currency.rounding)
                elif move_line_id:
                    disposed = float_round(move_line_id.debit, precision_rounding=currency.rounding)
                    disposal = float_round(move_line_id.debit, precision_rounding=currency.rounding)
                    # end_cost = 0.00 Commented this code, discussed with sebastien dtd. 26 apr 2022
                    # net_value_cost = 0.00
                    # depreciation_cost = 0.00 Commented this code, discussed with sebastien dtd. 26 apr 2022
                    # end_acc_dep_cost = 0.00 Commented this code, discussed with sebastien dtd. 26 apr 2022
                else:
                    # change for disposal date as per discussion with Seb G. dtd. 27-04-2022
                    # disposed = float_round(orignal_value, precision_rounding=currency.rounding)
                    
                    disposed = float_round(disposed, precision_rounding=currency.rounding)
                    prior_month_move_ids = move.asset_id.depreciation_move_ids.filtered(
                        lambda mv: mv.date <= end_date and mv.state == 'posted')
                    if prior_month_move_ids:
                        disposal = float_round(prior_month_move_ids[0].asset_depreciated_value,
                                           precision_rounding=currency.rounding)
                    else:
                        disposal = float_round(disposal, precision_rounding=currency.rounding)
                    # end_cost = 0.00 Commented this code, discussed with sebastien dtd. 26 apr 2022
                    # net_value_cost = 0.00 Commented this code, discussed with sebastien dtd. 4 may 2022
                    # beg_acc_dep_cost = 0.00 Commented this code, discussed with sebastien dtd. 4 may 2022
                    # end_acc_dep_cost = 0.00 Commented this code, discussed with sebastien dtd. 4 may 2022
            if move.asset_id.disposal_date and not (move.asset_id.disposal_date >= start_date and move.asset_id.disposal_date <= end_date):
                disposed = 0.00
                disposal = 0.00
            if move.asset_id.disposal_date and move.asset_id.disposal_date < start_date:
                beg_acc_dep_cost = 0.00
            # if move.asset_id.disposal_date and (move.asset_id.disposal_date >= start_date and move.asset_id.disposal_date <= end_date):
            #     depreciation_cost = sum(move.asset_id.depreciation_move_ids.filtered(
            #         lambda mv: "Disposal" not in mv.ref or mv.id != disposed_move_id.id).mapped('amount_total'))
            #     print ("depreciation_cost --****************->>", depreciation_cost)
                # if current_month_move_id:
                #     depreciation_cost = sum(current_month_move_id.filtered(
                #         lambda mv: "Disposal" not in mv.ref).mapped('amount_total'))
            if move.asset_id.disposal_date and end_date >= move.asset_id.disposal_date:
                disposed_move_id = max(move.asset_id.depreciation_move_ids.filtered(lambda dmv: dmv.state == 'posted').sorted(key='id',reverse=True))
                disposed = disposed_move_id.amount_total
            if disposed and move.asset_id.disposal_date >= start_date and move.asset_id.disposal_date <= end_date:
                category_data.append({'date': move.asset_id.acquisition_date,
                                      'disposal_date': move.asset_id.disposal_date if disposed else '',
                                      'description': move.asset_id.name,
                                      'analytic_tags': ','.join(
                                          move.asset_id.analytic_tag_ids.mapped(
                                              'name')) if move.asset_id.analytic_tag_ids else '',
                                      'journal_entry': move.name,
                                      'po_name': po_name,
                                      'dep_year': dep_year,
                                      'beg_cost': orignal_value,
                                      'purchase': purchase_value,
                                      'disposed': disposed,
                                      'end_cost': (orignal_value + purchase_value) - disposed,
                                      'beg_acc_dep': beg_acc_dep_cost,
                                      'depreciation': depreciation_cost,
                                      'disposal': disposal,
                                      'end_acc_dep': abs(
                                          beg_acc_dep_cost + depreciation_cost - disposal) if disposed else beg_acc_dep_cost + depreciation_cost - disposal,
                                      # 'net_value': net_value_cost,
                                      'net_value': ((orignal_value + purchase_value) - disposed) - (beg_acc_dep_cost + depreciation_cost - disposal) #abs(((orignal_value + purchase_value) - disposed) - abs(beg_acc_dep_cost + depreciation_cost - disposal)) if disposed else ((orignal_value + purchase_value) - disposed) - (beg_acc_dep_cost + depreciation_cost - disposal),
                                      
                                      
                                      })
            elif hide_zero_lines:
                if net_value_cost > 0.00:
                    category_data.append({'date': move.asset_id.acquisition_date,
                                          'disposal_date': move.asset_id.disposal_date if disposed else '',
                                          'description': move.asset_id.name,
                                          'analytic_tags': ','.join(
                                              move.asset_id.analytic_tag_ids.mapped(
                                                  'name')) if move.asset_id.analytic_tag_ids else '',
                                          'journal_entry': move.name,
                                          'po_name': po_name,
                                          'dep_year': dep_year,
                                          'beg_cost': orignal_value,
                                          'purchase': purchase_value,
                                          'disposed': disposed,
                                          'end_cost': (orignal_value + purchase_value) - disposed,
                                          'beg_acc_dep': beg_acc_dep_cost,
                                          'depreciation': depreciation_cost,
                                          'disposal': disposal,
                                          'end_acc_dep': abs(
                                              beg_acc_dep_cost + depreciation_cost - disposal) if disposed else beg_acc_dep_cost + depreciation_cost - disposal,
                                          # 'net_value': net_value_cost
                                          'net_value': ((orignal_value + purchase_value) - disposed) - (beg_acc_dep_cost + depreciation_cost - disposal) #abs(((orignal_value + purchase_value) - disposed) - abs(beg_acc_dep_cost + depreciation_cost - disposal)) if disposed else ((orignal_value + purchase_value) - disposed) - (beg_acc_dep_cost + depreciation_cost - disposal),
                                          })
            elif not hide_zero_lines:
                category_data.append({'date': move.asset_id.acquisition_date,
                                      'disposal_date': move.asset_id.disposal_date if disposed and move.asset_id.disposal_date <= end_date else '',
                                      'description': move.asset_id.name,
                                      'analytic_tags': ','.join(
                                          move.asset_id.analytic_tag_ids.mapped(
                                              'name')) if move.asset_id.analytic_tag_ids else '',
                                      'journal_entry': move.name,
                                      'po_name': po_name,
                                      'dep_year': dep_year,
                                      'beg_cost': orignal_value,
                                      'purchase': purchase_value,
                                      'disposed': disposed,
                                      'end_cost': (orignal_value + purchase_value) - disposed,
                                      'beg_acc_dep': beg_acc_dep_cost,
                                      'depreciation': depreciation_cost,
                                      'disposal': disposal,
                                      'end_acc_dep': abs(
                                          beg_acc_dep_cost + depreciation_cost - disposal) if disposed else beg_acc_dep_cost + depreciation_cost - disposal,
                                      # 'net_value': net_value_cost
                                      'net_value': ((orignal_value + purchase_value) - disposed) - (beg_acc_dep_cost + depreciation_cost - disposal) #abs(((orignal_value + purchase_value) - disposed) - abs(beg_acc_dep_cost + depreciation_cost - disposal)) if disposed else ((orignal_value + purchase_value) - disposed) - (beg_acc_dep_cost + depreciation_cost - disposal),
                                      })
        return sorted(category_data, key=lambda i: i['date'])
