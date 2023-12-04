# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

import copy

from odoo import api, models


class AccountReconciliation(models.AbstractModel):
    _inherit = 'account.reconciliation.widget'
    _description = 'Account Reconciliation widget'

    @api.model
    def process_bank_statement_line(self, st_line_ids, data):
        res = copy.deepcopy(data)
        return super(AccountReconciliation, self.with_context(
            to_attachment=res and res[0].get('to_attachment', False) or False)
                     ).process_bank_statement_line(st_line_ids, data)
