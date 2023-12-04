# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from collections import OrderedDict

from odoo import fields, api, models


class Hroffboarding(models.Model):
    _name = 'hr.offboarding'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'HR Offboarding Form'
    _order = 'name desc'

    name = fields.Char(required=True)
    today_date = fields.Date(
        string="Creation Date",
        default=lambda self: fields.Date.context_today(self))
    employment_date = fields.Date(string="Final Date of Employment")
    offboarding_general_post_termination_ids = fields.One2many(
        'offboarding.general.post.termination', 'offboarding_general_id',
        string="General Post Termination")
    offboarding_hr_person_ids = fields.One2many(
        'offboarding.hr.person', 'offboarding_hr_person_id',
        string="In Person")
    offboarding_hr_post_termination_ids = fields.One2many(
        'offboarding.hr.post.termination',
        'offboarding_hr_post_termination_id',
        string="HR Post Termination")
    offboarding_finance_options_ids = fields.One2many(
        'offboarding.finance.options', 'offboarding_finance_option_id',
        string="PayChecks")
    offboarding_finance_opt_post_termination_ids = fields.One2many(
        'offboarding.finance.options.post.termination',
        'finance_opt_post_termination_id',
        string="Finance Options Post Termination")
    offboarding_it_termination_process_ids = fields.One2many(
        'offboarding.it.termination.process', 'offboarding_it_termination_id',
        string="Termination Process")
    offboarding_operations_ids = fields.One2many(
        'offboarding.operations', 'offboarding_operation_id',
        string="Operations")
    offboarding_reception_ids = fields.One2many(
        'offboarding.reception', 'offboarding_reception_id',
        string="Reception")
    offboarding_secure_ids = fields.One2many(
        'offboarding.secure', 'offboarding_secure_id',
        string="Security")
    state = fields.Selection(
        [('active', 'Active'), ('complete', 'Complete')],
        default='active', track_visibility='onchange', copy=False,
        string="Status")

    @api.onchange('name')
    def set_termination_offboarding_data(self):
        general_post_termination_ids = self.env[
            'offboarding.general.post.termination'].search([
            ('offboarding_general_id', '=', False)])
        hr_person_ids = self.env['offboarding.hr.person'].search([
            ('offboarding_hr_person_id', '=', False)])
        hr_post_termination_ids = self.env[
            'offboarding.hr.post.termination'].search(
            [('offboarding_hr_post_termination_id', '=', False)])
        finance_options_ids = self.env['offboarding.finance.options'].search(
            [('offboarding_finance_option_id', '=', False)])
        finance_opt_post_termination_ids = self.env[
            'offboarding.finance.options.post.termination'].search(
            [('finance_opt_post_termination_id', '=', False)])
        it_termination_process_ids = self.env[
            'offboarding.it.termination.process'].search(
            [('offboarding_it_termination_id', '=', False)])
        offboarding_operations_ids = self.env['offboarding.operations'].search(
            [('offboarding_operation_id', '=', False)])
        offboarding_reception_ids = self.env['offboarding.reception'].search(
            [('offboarding_reception_id', '=', False)])
        offboarding_secure_ids = self.env['offboarding.secure'].search(
            [('offboarding_secure_id', '=', False)])
        if self.name:
            if not self.offboarding_general_post_termination_ids:
                self.offboarding_general_post_termination_ids = [
                    (0, 0, {'name': general_post_termination_id.name})
                    for general_post_termination_id in
                    general_post_termination_ids]
            if not self.offboarding_hr_person_ids:
                self.offboarding_hr_person_ids = [
                    (0, 0, {'name': hr_person_id.name})
                    for hr_person_id in hr_person_ids]
            if not self.offboarding_hr_post_termination_ids:
                self.offboarding_hr_post_termination_ids = [
                    (0, 0, {'name': hr_post_termination_id.name})
                    for hr_post_termination_id in hr_post_termination_ids]
            if not self.offboarding_finance_options_ids:
                self.offboarding_finance_options_ids = [
                    (0, 0, {'name': finance_options_id.name})
                    for finance_options_id in finance_options_ids]
            if not self.offboarding_finance_opt_post_termination_ids:
                self.offboarding_finance_opt_post_termination_ids = [
                    (0, 0, {'name': finance_opt_post_termination_id.name})
                    for finance_opt_post_termination_id
                    in finance_opt_post_termination_ids]
            if not self.offboarding_it_termination_process_ids:
                self.offboarding_it_termination_process_ids = [
                    (0, 0, {'name': it_termination_process_id.name})
                    for it_termination_process_id in
                    it_termination_process_ids]
            if not self.offboarding_operations_ids:
                self.offboarding_operations_ids = [
                    (0, 0, {'name': offboarding_operations_id.name})
                    for offboarding_operations_id in
                    offboarding_operations_ids]
            if not self.offboarding_reception_ids:
                self.offboarding_reception_ids = [
                    (0, 0, {'name': offboarding_reception_id.name})
                    for offboarding_reception_id in
                    offboarding_reception_ids]
            if not self.offboarding_secure_ids:
                self.offboarding_secure_ids = [
                    (0, 0, {'name': offboarding_secure_id.name})
                    for offboarding_secure_id in
                    offboarding_secure_ids]

    def _get_onchange_create(self):
        return OrderedDict([
            ('set_termination_offboarding_data',
             ['offboarding_general_post_termination_ids',
              'offboarding_hr_person_ids',
              'offboarding_hr_post_termination_ids',
              'offboarding_finance_options_ids',
              'offboarding_finance_opt_post_termination_ids',
              'offboarding_it_termination_process_ids'])])

    @api.model
    def create(self, vals):
        """call onchange of set project process during import"""
        onchanges = self._get_onchange_create()
        for onchange_method, changed_fields in onchanges.items():
            if any(f not in vals for f in changed_fields):
                order = self.new(vals)
                getattr(order, onchange_method)()
                for field in changed_fields:
                    if field not in vals and order[field]:
                        vals[field] = order._fields[field].convert_to_write(
                            order[field], order)
        return super(Hroffboarding, self).create(vals)


class OffBoardingGeneralPostTermination(models.Model):
    _name = 'offboarding.general.post.termination'
    _description = 'Offboarding General Post Termination'
    _order = 'sequence'

    name = fields.Text()
    sequence = fields.Integer()
    task_completion_date = fields.Date(string="Date of Completion")
    initials = fields.Text(help="Initials")
    offboarding_general_id = fields.Many2one(
        'hr.offboarding', ondelete='cascade', index=True, copy=False)
    note = fields.Text(string="Notes")


class OffBoardingHRPerson(models.Model):
    _name = 'offboarding.hr.person'
    _description = 'Offboarding HR Person'
    _order = 'sequence'

    name = fields.Text()
    sequence = fields.Integer()
    task_completion_date = fields.Date(string="Date of Completion")
    initials = fields.Text(help="Initials")
    offboarding_hr_person_id = fields.Many2one(
        'hr.offboarding', ondelete='cascade', index=True, copy=False)
    note = fields.Text(string="Notes")


class OffBoardingHRPostTermination(models.Model):
    _name = 'offboarding.hr.post.termination'
    _description = 'Offboarding HR Post Termination'
    _order = 'sequence'

    name = fields.Text()
    sequence = fields.Integer()
    task_completion_date = fields.Date(string="Date of Completion")
    initials = fields.Text(help="Initials")
    offboarding_hr_post_termination_id = fields.Many2one(
        'hr.offboarding', ondelete='cascade', index=True, copy=False)
    note = fields.Text(string="Notes")


class OffBoardingFinanceOptions(models.Model):
    _name = 'offboarding.finance.options'
    _description = 'Offboarding finance options'
    _order = 'sequence'

    name = fields.Text()
    sequence = fields.Integer()
    task_completion_date = fields.Date(string="Date of Completion")
    initials = fields.Text(help="Initials")
    offboarding_finance_option_id = fields.Many2one(
        'hr.offboarding', ondelete='cascade', index=True, copy=False)
    note = fields.Text(string="Notes")


class OffBoardingFinanceOptionsPostTermination(models.Model):
    _name = 'offboarding.finance.options.post.termination'
    _description = 'Offboarding Finance Options Post Termination'
    _order = 'sequence'

    name = fields.Text()
    sequence = fields.Integer()
    task_completion_date = fields.Date(string="Date of Completion")
    initials = fields.Text(help="Initials")
    finance_opt_post_termination_id = fields.Many2one(
        'hr.offboarding', ondelete='cascade', index=True, copy=False)
    note = fields.Text(string="Notes")


class OffboardingItTerminationProcess(models.Model):
    _name = 'offboarding.it.termination.process'
    _description = 'Offboarding IT Termination Process'
    _order = 'sequence'

    name = fields.Text()
    sequence = fields.Integer()
    task_completion_date = fields.Date(string="Date of Completion")
    initials = fields.Text(help="Initials")
    offboarding_it_termination_id = fields.Many2one(
        'hr.offboarding', ondelete='cascade', index=True, copy=False)
    note = fields.Text(string="Notes")


class OffboardingOperations(models.Model):
    _name = 'offboarding.operations'
    _description = 'Offboarding Operations'
    _order = 'sequence'

    name = fields.Text()
    sequence = fields.Integer()
    task_completion_date = fields.Date(string="Date of Completion")
    initials = fields.Text(help="Initials")
    offboarding_operation_id = fields.Many2one(
        'hr.offboarding', ondelete='cascade', index=True, copy=False)
    note = fields.Text(string="Notes")


class OffboardingReception(models.Model):
    _name = 'offboarding.reception'
    _description = 'Offboarding Reception'
    _order = 'sequence'

    name = fields.Text()
    sequence = fields.Integer()
    task_completion_date = fields.Date(string="Date of Completion")
    initials = fields.Text(help="Initials")
    offboarding_reception_id = fields.Many2one(
        'hr.offboarding', ondelete='cascade', index=True, copy=False)
    note = fields.Text(string="Notes")

class OffboardingSecure(models.Model):
    _name = 'offboarding.secure'
    _description = 'Offboarding Security'
    _order = 'sequence'

    name = fields.Text()
    sequence = fields.Integer()
    task_completion_date = fields.Date(string="Date of Completion")
    initials = fields.Text(help="Initials")
    offboarding_secure_id = fields.Many2one(
        'hr.offboarding', ondelete='cascade', index=True, copy=False)
    note = fields.Text(string="Notes")