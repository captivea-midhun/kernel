from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    interval_number = fields.Integer('Interval Number')
    interval_type = fields.Selection([('minutes', 'Minutes'),
                                     ('hours', 'Hours'),
                                     ('days', 'Days'),
                                     ('weeks', 'Weeks'),
                                     ('months', 'Months')], string='Interval Unit', default='days')
    nextcall = fields.Datetime(string='Next Execution Date', required=True,
                               help="Next planned execution date for this job.")
    is_auto_replenish = fields.Boolean('Auto Replenish')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        cron_id = self.env.ref('mrp_mps_extended.mps_scheduler')
        res['interval_number'] = cron_id.interval_number
        res['interval_type'] = cron_id.interval_type
        res['nextcall'] = cron_id.nextcall
        res['is_auto_replenish'] = cron_id.active
        return res

    @api.model
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        cron_id = self.env.ref('mrp_mps_extended.mps_scheduler')
        if cron_id:
            cron_id.active = self.is_auto_replenish
            cron_id.interval_number = self.interval_number
            cron_id.interval_type = self.interval_type
            cron_id.nextcall = self.nextcall
        return res

