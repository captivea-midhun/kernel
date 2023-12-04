from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    archiving_product_activity_user = fields.Many2one(
        'res.users', string='Activity User',
        config_parameter='captivea_product_archiving.archiving_product_activity_user')
    activity_after_x_days = fields.Integer(string="Show Activity After X Days", default=0,
                                           config_parameter='captivea_product_archiving.activity_after_x_days')
    activity_message_for_archiving = fields.Char(string="Activity Message", default='',
                                           config_parameter='captivea_product_archiving.activity_message_for_archiving')
