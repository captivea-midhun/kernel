# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################


from odoo import fields, models, api


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    # Override fields due to change the label of fields.
    mobile_phone = fields.Char(string="Mobile")
    work_email = fields.Char(string="Personal Email")
    work_location = fields.Char(string="Location")
    job_title = fields.Char(string="Title")
    department_id = fields.Many2one(
        'hr.department', string="Team",
        domain="['|', ('company_id', '=', False),('company_id', '=', company_id)]")


class Employee(models.Model):
    _inherit = "hr.employee"

    hr_start_date = fields.Date(string='Start Date')
    hr_salary_ids = fields.One2many('hr.salary', 'hr_id', string="HR Salary")
    hr_options_ids = fields.One2many('hr.options', 'hr_id', string="HR Options")
    hr_work_authorization_ids = fields.One2many(
        'hr.work.authorization', 'hr_id', string="HR Work Authorization")
    hr_relocation_ids = fields.One2many('hr.relocation', 'hr_id')
    termination_date = fields.Date()
    reason = fields.Text()
    final_pay_check_amt = fields.Char(string="Final Pay Check Amount")
    method_of_payment = fields.Char()
    severance_package = fields.Selection(selection=[
        ('yes', 'Yes'), ('no', 'No')], help='Check Severance Package')
    date_of_payment = fields.Date()
    severance_agreement_details = fields.Text()
    termination_create_date = fields.Date(string="Creation Date")
    kernel_work_email = fields.Char(string="Work Email", copy=False)

    @api.model
    def create(self, vals):
        if vals.get('kernel_work_email'):
            vals['kernel_work_email'] = vals.get('kernel_work_email') + '@kernel.com'
        return super(Employee, self).create(vals)

    def write(self, vals):
        work_email = vals.get('kernel_work_email', '')
        if work_email and not work_email.endswith("@kernel.com"):
            vals['kernel_work_email'] = work_email + '@kernel.com'
        return super(Employee, self).write(vals)


class HrSalary(models.Model):
    _name = "hr.salary"
    _description = "Hr Salary"

    name = fields.Char(string="Salary")
    hr_id = fields.Many2one("hr.employee", ondelete='cascade', index=True, copy=False)
    salary_date = fields.Date(string="Date")
    note = fields.Text(string="Notes")


class HrOptions(models.Model):
    _name = "hr.options"
    _description = "Hr Options"
    _rec_name = 'no_of_option'

    hr_id = fields.Many2one("hr.employee", ondelete='cascade', index=True, copy=False)
    grant_date = fields.Date()
    no_of_option = fields.Integer(string="No. of Options")
    strike_price = fields.Float()
    note = fields.Text(string="Notes")


class HrRelocation(models.Model):
    _name = "hr.relocation"
    _description = "HR Relocation"
    _rec_name = 'original_location'

    original_location = fields.Char()
    new_location = fields.Char()
    relocation_package = fields.Char()
    family_status = fields.Selection(selection=[
        ('single_spouse', 'Single/Spouse'),
        ('married_family', 'Married/Family')], help='Add family status.')
    notes = fields.Text()
    reloacation_create_date = fields.Date(string="Creation Date")
    hr_id = fields.Many2one("hr.employee", ondelete='cascade', index=True, copy=False)


class HrWorkAuthorization(models.Model):
    _name = "hr.work.authorization"
    _description = "HR Work Authorization"
    _rec_name = 'country_of_origin'

    hr_id = fields.Many2one("hr.employee", ondelete='cascade', index=True, copy=False)
    us_citizen = fields.Selection(selection=[
        ('yes', 'Yes'), ('no', 'No')], string='U.S. Citizen', default="yes",
        help='U.S. Citizen, Permanent Residence or Asylee/Refugee')
    country_of_origin = fields.Char(string="Country of Origin")
    citizenship = fields.Char()
    most_recent_residence = fields.Char()
    law_firm = fields.Char()
    attorney_name = fields.Char()
    attorney_phone = fields.Char(string="Phone")
    attorney_email = fields.Char(string="Email")
    visa_status = fields.Char()
    last_updated_date = fields.Date()
    notes = fields.Text()

    @api.onchange('us_citizen')
    def _onchange_citizenship(self):
        """
        Trigger the onchange to set the value of country_of_origin,
        citizenship,most_recent_residence
        """
        for rec in self:
            if rec.us_citizen == 'yes':
                rec.country_of_origin = False
                rec.citizenship = False
                rec.most_recent_residence = False
                rec.visa_status = False
                rec.last_updated_date = False
                rec.law_firm = False
                rec.attorney_name = False
                rec.attorney_phone = False
                rec.attorney_email = False
                rec.notes = False
            if rec.us_citizen == 'no':
                rec.notes = False
