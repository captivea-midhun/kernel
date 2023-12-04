# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (http://www.bistasolutions.com)
#
##############################################################################

from odoo import models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def _check_bank_statement(self):
        """
        Define Scheduler function to call daily to check that Company and
        Journal fields value set or not in statement line which statement in
        Open state.
        :return:
        """
        statement_ids = self.search([('state', '=', 'open'),
                                     ('name', '=', 'online sync')])
        for statement_id in statement_ids:
            for statement_line in statement_id.line_ids:
                if not statement_line.company_id:
                    statement_line.update({
                        'company_id': statement_line.statement_id.company_id.id or False})
                if not statement_line.journal_id:
                    statement_line.update({
                        'journal_id': statement_line.statement_id.journal_id.id or False})
