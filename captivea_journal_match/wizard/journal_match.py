from odoo import fields, models, api, _


class JournalMatch(models.TransientModel):
    _name = 'journal.match.wizard'
    _description = 'Journal Match Wizard'

    notification = fields.Char()
    manual_match_value = fields.Char('Manual Match', default=lambda self: self._get_default_manual_match_value())
    pop_notification = fields.Boolean(default=False)
    process_succeed = fields.Boolean(default=False)

    def _get_default_manual_match_value(self):
        line_ids = self.env.context.get('active_ids', [])
        lines = self.env['account.move.line'].browse(line_ids)
        if lines:
            vals = [l.manual_match for l in lines if l.manual_match]
            vals = list(set(vals))
            if vals and len(vals) == 1:
                return vals[0]
        return ''

    def update_moves(self):
        match_ids = []
        match_val = False
        # previous_match = False
        line_ids = self.env.context.get('lines', [])
        lines = self.env['account.move.line'].browse(line_ids)
        previous_matches = [l.manual_match for l in lines if l.manual_match]
        # if len(set(previous_matches)) == 1:
        #     previous_match = previous_matches[0]
        if not self.manual_match_value and previous_matches:
            # match_val = previous_match
            only_pre_matches = list(set(previous_matches))
            for pre in only_pre_matches:
                current_line = lines.filtered(lambda x: x.manual_match == pre)
                current_line.write(
                    {'previous_match': pre, 'manual_match': '', 'match_amount_sum': 0, 'hide_clearing': False})
                # self._cr.commit()
                # if previous_match:
                previous = pre  # l.previous_match
                if previous:
                    self._cr.execute(
                        f"""
                                                    select aml.id 
                                                    from account_move_line aml
                                                    inner join account_move am on am.id = aml.move_id
                                                    where aml.manual_match = '{previous}'::text and
                                                          am.state = 'posted'""")
                    previous_data = self._cr.fetchall()
                    previous_data = [a[0] for a in previous_data]
                    if previous_data:
                        # match_ids.extend(previous_data)
                        if current_line:
                            previous_data = list(set(previous_data) - set(current_line.ids))
                        previous_data = list(set(previous_data))
                        if not previous_data:
                            continue
                        previous_matches = self.env['account.move.line'].browse(previous_data)
                        previous_debit = round(sum(previous_matches.mapped('debit')), 2)
                        previous_credit = round(sum(previous_matches.mapped('credit')), 2)
                        previous_balance = previous_credit - previous_debit
                        for previous_line in previous_matches:
                            previous_line.match_amount_sum = previous_balance
                            if previous_line.manual_match and previous_balance == 0:
                                previous_line.hide_clearing = True
                            else:
                                previous_line.hide_clearing = False
            self.process_succeed = True
            self.pop_notification = True
            self.notification = 'Operation completed successfully.'
            # match_ids = data
        else:
            if self.manual_match_value:
                match_val = self.manual_match_value
            if match_val:
                for l in lines:
                    l.previous_match = l.manual_match
                    l.manual_match = self.manual_match_value
                # self._cr.commit()

                for previous_match in list(set(previous_matches)):

                    previous = previous_match  # l.previous_match
                    if previous:
                        self._cr.execute(
                            f"""
                                select aml.id 
                                from account_move_line aml
                                inner join account_move am on am.id = aml.move_id
                                where aml.manual_match = '{previous}'::text and
                                      am.state = 'posted'""")
                        previous_data = self._cr.fetchall()
                        previous_data = [a[0] for a in previous_data]
                        if previous_data:
                            match_ids.extend(lines.ids)
                            lines and previous_data.extend(lines.ids)
                            previous_data = list(set(previous_data) - set(lines.ids))
                            previous_matches = self.env['account.move.line'].browse(previous_data)
                            previous_debit = round(sum(previous_matches.mapped('debit')), 2)
                            previous_credit = round(sum(previous_matches.mapped('credit')), 2)
                            previous_balance = previous_credit - previous_debit
                            for previous_line in previous_matches:
                                previous_line.match_amount_sum = previous_balance
                                if previous_line.manual_match and previous_balance == 0:
                                    previous_line.hide_clearing = True
                                else:
                                    previous_line.hide_clearing = False

                self._cr.execute(
                    f"""
                    select aml.id 
                    from account_move_line aml
                    inner join account_move am on am.id = aml.move_id
                    where aml.manual_match = '{match_val}'::text and
                          am.state = 'posted'""")
                data = self._cr.fetchall()
                data = [a[0] for a in data]
                lines and data.extend(lines.ids)
                data = list(set(data))
                matches = self.env['account.move.line'].browse(data)
                debit = round(sum(matches.mapped('debit')), 2)
                credit = round(sum(matches.mapped('credit')), 2)
                balance = credit - debit
                for line in matches:
                    line.match_amount_sum = balance
                    if line.manual_match and balance == 0:
                        line.hide_clearing = True
                    else:
                        line.hide_clearing = False
                self.process_succeed = True
                self.pop_notification = True
                self.notification = 'Operation completed successfully.'
                match_ids.extend(data)

            else:
                self.pop_notification = True
                self.notification = 'Operation could not continue as Manual Match value is not set and' \
                                    ' Journal Entries you have selected have different Previous Match Values.'
        context = self._context.copy() or {}
        context.update({
            'match_ids': list(set(match_ids))
        })
        return {
            'name': _('Journal Match'),
            'view_mode': 'form',
            'res_model': 'journal.match.wizard',
            'views': [(self.env.ref('captivea_journal_match.journal_match_form_view').id, 'form')],
            'type': 'ir.actions.act_window',
            'context': context,
            'res_id': self.id,
            'target': 'new'
        }

    def show_reflected_entries(self):
        journal_entries = self.env.context.get('match_ids', [])
        action = self.env.ref('account.action_account_moves_all').read()[0]
        action.update({
            'domain': [('display_type', 'not in', ('line_section', 'line_note')), ('move_id.state', '!=', 'cancel'),
                       ('id', 'in', journal_entries)]
        })
        return action
