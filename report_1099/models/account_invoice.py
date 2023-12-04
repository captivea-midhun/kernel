# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import api, models, fields

income_list = [
    ('rent', '1. Rents'),
    ('royalty', '2. Royalties'),
    ('other', '3. Other Income'),
    ('federal_income_tax_withheld', '4. Federal income tax withheld'),
    ('fishing_boat_proceeds', '5. Fishing boat proceeds'),
    ('medical_and_health_care_payments', '6. Medical and health care payments'),
    ('non_emp_cmpr', '7. Nonemployee compensation'),
    ('sub_stitute_payments_in_lieu_of_dividends_or_interest',
     '8. Substitute payments in lieu of dividends or payments'),
    ('sale', '9. Direct Sales'),
    ('crop_insurance_proceeds', '10. Crop insurance proceeds'),
    ('11', '11. '), ('12', '12. '),
    ('excess_golden_perachute_payments', '13. Excess golden parachute payments'),
    ('gross_proceeds_paid_to_an_attomey', '14. Gross proceeds paid to an attorney'),
    ('section_409A_deferrals', '15a. Section 409A deferrals'),
    ('section_409A_income', '15.b. Section 409A income'),
    ('state_tax_withheld', '16. State tax withheld'),
    ("state_payers_state_no", "17. State/Payer's state no."),
    ('state_income', '18. State income')]


class AccountMove(models.Model):
    _inherit = "account.move"

    is_1099 = fields.Boolean(related='partner_id.is_1099', store=True)

    @api.onchange('partner_id')
    def onchange_partner_inv(self):
        for rec in self:
            for line in rec.invoice_line_ids:
                line.is_1099 = rec.partner_id.is_1099
                if rec.partner_id.is_1099:
                    line.type_income = rec.partner_id.type_income
                else:
                    line.type_income = False


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    is_1099 = fields.Boolean()
    type_income = fields.Selection(income_list, string="Income Type")

    @api.model
    def default_get(self, default_fields):
        """ Setting default value of is_1099 from relevant partner """
        res = super(AccountMoveLine, self).default_get(default_fields)
        partner_ids = self._context.get('partner_tags_ids', False)
        partner = self.env['res.partner'].browse(partner_ids)
        if partner:
            res['is_1099'] = partner.is_1099
            if partner.is_1099:
                res['type_income'] = partner.type_income
        return res

    @api.onchange('is_1099')
    def onchange_is_1099(self):
        for rec in self:
            if rec.partner_id and rec.partner_id.is_1099 and rec.is_1099:
                rec.type_income = rec.partner_id.type_income
            else:
                rec.type_income = False

    @api.onchange('partner_id')
    def onchange_partner_1099(self):
        if self.partner_id:
            self.is_1099 = self.partner_id.is_1099
            if self.partner_id.is_1099:
                self.type_income = self.partner_id.type_income
            else:
                self.type_income = False


class AccountPayment(models.Model):
    _inherit = "account.payment"

    is_1099 = fields.Boolean()
