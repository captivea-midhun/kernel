from odoo import fields, models, api, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    manual_match = fields.Char('Manual Match')
    previous_match = fields.Char('Previous Match')
    hide_clearing = fields.Boolean('Hide')
    match_amount_sum = fields.Float('Difference')

    def open_journal_match_wizard(self):
        line_ids = self.env.context.get('active_ids', [])
        lines = self.env['account.move.line'].browse(line_ids)
        context = self._context.copy() or {}
        context.update({'lines': line_ids})
        # non_po_lines = lines.filtered(lambda line: not line.purchase_line_id)
        # if non_po_lines:
        #     pop_up_wiz = self.env['journal.match.wizard'].create({
        #         'notification': 'Journal Entries must be of Purchase Order',
        #         'pop_notification': True
        #     })
        #     return {
        #         'name': _('Journal Match'),
        #         'view_mode': 'form',
        #         'res_model': 'journal.match.wizard',
        #         'views': [(self.env.ref('captivea_journal_match.journal_match_form_view').id, 'form')],
        #         'type': 'ir.actions.act_window',
        #         'res_id': pop_up_wiz.id,
        #         'target': 'new'
        #     }
        # else:
        return {
            'name': _('Journal Match'),
            'view_mode': 'form',
            'res_model': 'journal.match.wizard',
            'views': [(self.env.ref('captivea_journal_match.journal_match_form_view').id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }

    def auto_journal_match(self):
        mo_journal_match_account_id = self.env['ir.config_parameter'].sudo() \
            .get_param('captivea_journal_match.default_mo_journal_match_account_id')
        try:
            mo_journal_match_account_id = int(mo_journal_match_account_id)
        except Exception as e:
            mo_journal_match_account_id = False
        if mo_journal_match_account_id:
            read_group_var = self.sudo().read_group(
                [('x_studio_mo', '!=', False),
                 ('hide_clearing', '!=', True),
                 ('account_id', '=', mo_journal_match_account_id)],
                fields=['x_studio_mo'],
                groupby=['x_studio_mo'])
            for record in read_group_var:
                lines_domain = record.get('__domain', [])
                if lines_domain:
                    lines = self.sudo().search(lines_domain)
                    if lines:
                        debit = round(sum(lines.mapped('debit')), 2)
                        credit = round(sum(lines.mapped('credit')), 2)
                        balance = credit - debit
                        if balance == 0:
                            previous_matches = [l.manual_match for l in lines if l.manual_match]
                            for previous_match in list(set(previous_matches)):
                                current_line = lines.filtered(lambda x: x.manual_match == previous_match)
                                current_line.write({'previous_match': previous_match})
                                previous = previous_match  # l.previous_match
                                # if previous:
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
                                    # match_ids.extend(lines.ids)
                                    # lines and previous_data.extend(lines.ids)
                                    if lines:
                                        previous_data = list(set(previous_data) - set(lines.ids))
                                    previous_data = list(set(previous_data))
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
                            lines.write({'manual_match': '', 'match_amount_sum': 0, 'hide_clearing': True})
        return True
