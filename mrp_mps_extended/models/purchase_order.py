from odoo import fields, models, api
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
import calendar
import pytz


class PO(models.Model):
    _inherit = 'purchase.order'

    is_replanished_from_mps = fields.Boolean(default=False)

    @api.model
    def create(self, vals_list):
        """
        Author : Udit Ramani (Setu Consulting Services Private Ltd.)
        Purpose : To add department in the purchase order when it will be created from MPS.
        Date : 29th Oct 2021
        """
        res = super(PO, self).create(vals_list)
        for rec in res:
            if rec.is_replanished_from_mps:
                rec.department_id = self.env['hr.department'].search([('use_for_mps', '=', True)]) or False
        return res


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_purchase_order(self, company_id, origins, values):
        """
        Author : Udit Ramani (Setu Consulting Services Private Ltd.)
        Purpose : Inherited this method to add a reference of MPS in Purchase Orders.
        Date : 29th Oct 2021
        """
        res = super(StockRule, self)._prepare_purchase_order(company_id, origins, values)
        if values and values[0] and 'is_replanished_from_mps' in values[0].keys() and values[0][
            'is_replanished_from_mps']:
            res.update({
                'is_replanished_from_mps': values[0]['is_replanished_from_mps']
            })
        return res


class POLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.model
    def create(self, vals_list):
        """
        Author : Udit Ramani (Setu Consulting Services Private Ltd.)
        Purpose : Inherited this method to take date related changes in the Manufacturing Order.
        Date : 29th Oct 2021
        """
        local_tz = self.env.user.tz and pytz.timezone(self.env.user.tz) or pytz.timezone('UTC')
        res = super(POLine, self).create(vals_list)
        for rec in res:
            if rec.order_id and rec.order_id.is_replanished_from_mps:
                supplier_info = self.env['product.supplierinfo'].search(
                    [('product_tmpl_id', '=', rec.product_id.product_tmpl_id.id),
                     ('name', '=', rec.order_id.partner_id.id)], limit=1)
                if supplier_info:
                    delay = supplier_info.delay
                    if delay:
                        delayed_date = rec.order_id.date_order + relativedelta(days=delay)
                        if not rec.order_id.expected_date or rec.order_id.expected_date < delayed_date.date():
                            rec.order_id.expected_date = delayed_date
                            current_datetime = datetime.now()
                            expected_date = datetime(rec.order_id.expected_date.year, rec.order_id.expected_date.month,
                                                     rec.order_id.expected_date.day,
                                                     current_datetime.hour,
                                                     current_datetime.minute, current_datetime.second)
                            expected_date = local_tz.normalize(expected_date.astimezone(local_tz))
                            weekday = calendar.day_name[expected_date.weekday()]
                            if weekday == 'Saturday':
                                rec.order_id.expected_date = expected_date - relativedelta(days=1)
                            if weekday == 'Sunday':
                                rec.order_id.expected_date = expected_date - relativedelta(days=2)
        return res





