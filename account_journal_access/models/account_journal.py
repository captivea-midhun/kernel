# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def read(self, fields, load='_classic_read'):
        if self.env.user.journal_ids:
            self = self.env.user.journal_ids
        return super(AccountJournal, self).read(fields, load=load)
