from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mo_journal_match_account_id = fields.Many2one(
        'account.account',
        config_parameter='captivea_journal_match.default_mo_journal_match_account_id')
