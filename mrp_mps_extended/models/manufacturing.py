from odoo import fields, models, api
import calendar
from dateutil.relativedelta import relativedelta
import pytz


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values,
                         bom):
        """
        Author : Udit Ramani (Setu Consulting Services Private Ltd.)
        Purpose : Inherited this method to add a reference of MPS in Manufacturing Orders.
        Date : 29th Oct 2021
        """
        res = super(StockRule, self)._prepare_mo_vals(product_id, product_qty, product_uom, location_id, name, origin,
                                                      company_id, values, bom)
        if values and 'is_replanished_from_mps' in values.keys() and values[
            'is_replanished_from_mps']:
            res.update({
                'is_replanished_from_mps': values['is_replanished_from_mps']
            })
        return res


class MO(models.Model):
    _inherit = 'mrp.production'

    is_replanished_from_mps = fields.Boolean(default=False)

    @api.model
    def create(self, vals_list):
        """
        Author : Udit Ramani (Setu Consulting Services Private Ltd.)
        Purpose : Inherited this method to take date related changes and added department in the Manufacturing Order.
        Date : 29th Oct 2021
        """
        res = super(MO, self).create(vals_list)
        for rec in res:
            if rec.is_replanished_from_mps:
                local_tz = pytz.timezone(self.env.user.tz)
                rec.department_id = self.env['hr.department'].search([('use_for_mps', '=', True)]) or False
                date_planned_start = local_tz.normalize(rec.date_planned_start.astimezone(local_tz))
                date_planned_finished = local_tz.normalize(rec.date_planned_finished.astimezone(local_tz))
                weekday = calendar.day_name[date_planned_start.weekday()]
                if weekday == 'Saturday':
                    rec.date_planned_start = date_planned_start - relativedelta(days=1)
                    rec.date_planned_finished = date_planned_finished - relativedelta(days=1)
                if weekday == 'Sunday':
                    rec.date_planned_start = rec.date_planned_start - relativedelta(days=2)
                    rec.date_planned_finished = rec.date_planned_finished - relativedelta(days=2)
                date_deadline = local_tz.normalize(rec.date_deadline.astimezone(local_tz))
                weekday = calendar.day_name[date_deadline.weekday()]
                if weekday == 'Saturday':
                    rec.date_deadline = rec.date_deadline - relativedelta(days=1)
                if weekday == 'Sunday':
                    rec.date_deadline = rec.date_deadline - relativedelta(days=2)
        return res
