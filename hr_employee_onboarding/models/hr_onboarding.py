# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from collections import OrderedDict

from odoo import fields, api, models


class HrOnboarding(models.Model):
    _name = 'hr.onboarding'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'HR Onboarding Form'
    _order = 'name desc'

    @api.model
    def get_preferred_laptop_task(self):
        html_text = """
            <ul>
                <li>Order Preferred Laptop</li>
            </ul>
        """
        return html_text

    @api.model
    def get_jumpcloud_task(self):
        html_text = """
            <ul>
            <li>Username: first initial / last name (for
                    hyphens: flast1-last2)</li>
                <li>Email: first.last@kernel.co (
                for hyphens: first.last1-last2@kernel.co)</li>
                <li>Specify initial password:
                    <ul>
                        <li>Random generated password</li>
                    </ul>
                </li>
                <li>Require MFA</li>
                <li>Enable LDAP bind</li>
                <li>Enforce UID/GID consistency
                    <ul>
                        <li>1password => find latest,
                        add user/group to mapping</li>
                    </ul>
                </li>
                <li>User groups: all employees and then specific role (
                ex: git users)</li>
                <li>Directories: ldap should be auto checked</li>
            </ul>
        """
        return html_text

    @api.model
    def get_openlaptop_task(self):
        html_text = """
            <ul>
                <li>Create kernel-admin user, make unique password and add to
                    shared 1password</li>
                <li>Install jumpcloud agent for ALL users</li>
                <li>Register system on jumpcloud</li>
                <li>Add system to appropriate system groups (windows or mbp)
                </li>
                <li>Add user as local admin/sudoer</li>
                <li>Run the add cert command</li>
            </ul>
        """
        return html_text

    @api.model
    def get_gsuite_task(self):
        html_text = """
            <ul>
                <li>Register</li>
                <li>Do not send private email (use printout instead)</li>
                <li>Add to kernel-employees</li>
                <li>Add to kernel all mailing list</li>
                <li>Add to remote work calendar through calendar settings</li>
            </ul>
        """
        return html_text

    @api.model
    def get_slack_task(self):
        html_text = """
            <ul>
                <li>Register</li>
            </ul>
        """
        return html_text

    @api.model
    def get_zoom_task(self):
        html_text = """
            <ul>
                <li>Register as basic account</li>
            </ul>
        """
        return html_text

    def get_jira_task(self):
        html_text = """
            <ul>
                <li>Send JIRA First Day List link</li>
            </ul>
        """
        return html_text

    @api.model
    def get_one_password_task(self):
        html_text = """
            <ul>
                <li>Register on website</li>
                <li>Put on Google/Slack/etc password here</li>
            </ul>
        """
        return html_text

    @api.model
    def get_grubhub_task(self):
        html_text = """
            <ul>
                <li>Culver City Office</li>
                <li>LA employees</li>
                <li>Send welcome email after adding account</li>
            </ul>
        """
        return html_text

    @api.model
    def get_procurify_task(self):
        html_text = """
            <ul>
                <li>Register</li>
                <li>Go to pending</li>
                <li>Add as a requester</li>
                <li>Add to office mgmt. + specific group location</li>
            </ul>
        """
        return html_text

    name = fields.Char(required=True)
    title = fields.Char()
    start_date = fields.Date()
    location = fields.Char()
    mobile = fields.Char()
    email = fields.Char(string="Personal Email")
    department_id = fields.Many2one('hr.department', 'Team')
    hiring_manager = fields.Char()
    pre_hire_onboarding_ids = fields.One2many(
        'hr.pre.hire.onboarding', 'hr_pre_onboarding_id',
        string="Pre Hire")
    post_hire_onboarding_ids = fields.One2many(
        'hr.post.hire.onboarding', 'hr_post_onboarding_id',
        string="Post Hire")
    hr_offer_onboarding_ids = fields.One2many(
        'hr.offer.onboarding', 'hr_offer_onboarding_id',
        string="Offer")
    hr_offer_post_onboarding_ids = fields.One2many(
        'hr.offer.post.hire.onboarding', 'hr_offer_post_onboarding_id',
        string="Offer Post Hire")
    hr_options_onboarding_ids = fields.One2many(
        'hr.options.onboarding', 'hr_options_onboarding_id',
        string="Options")
    hr_operations_onboarding_ids = fields.One2many(
        'hr.operations.onboarding', 'hr_operations_onboarding_id',
        string="Operations")
    hr_reception_onboarding_ids = fields.One2many(
        'hr.reception.onboarding', 'hr_reception_onboarding_id',
        string="reception")
    hr_secure_onboarding_ids = fields.One2many(
        'hr.secure.onboarding', 'hr_secure_onboarding_id',
        string="security")
    state = fields.Selection(
        [('active', 'Active'), ('complete', 'Complete')],
        default='active', track_visibility='onchange', copy=False,
        string="Status")

    # Order Preferred Laptop
    preferred_laptop_task = fields.Html(default=get_preferred_laptop_task)
    preferred_laptop_task_description = fields.Char()
    preferred_laptop_completion_date = fields.Date(
        help="Date of Completion")
    preferred_laptop_note = fields.Text()

    # JumpCloud
    jumpcloud_task = fields.Html(default=get_jumpcloud_task)
    jumpcloud_task_description = fields.Char()
    jumpcloud_completion_date = fields.Date(
        help="Date of Completion")
    jumpcloud_note = fields.Text()

    open_laptop_task = fields.Html(default=get_openlaptop_task)
    open_laptop_task_description = fields.Char()
    open_laptop_completion_date = fields.Date(
        help="Date of Completion")
    open_laptop_note = fields.Text()

    # Gsuite
    gsuite_task = fields.Html(default=get_gsuite_task)
    gsuite_task_description = fields.Char()
    gsuite_completion_date = fields.Date(
        help="Date of Completion")
    gsuite_note = fields.Text()

    # Slack
    slack_task = fields.Html(default=get_slack_task)
    slack_task_description = fields.Char()
    slack_completion_date = fields.Date(
        help="Date of Completion")
    slack_note = fields.Text()

    # Zoom
    zoom_task = fields.Html(default=get_zoom_task)
    zoom_task_description = fields.Char()
    zoom_completion_date = fields.Date(
        help="Date of Completion")
    zoom_note = fields.Text()

    # 1Password
    one_password_task = fields.Html(default=get_one_password_task)
    one_password_task_description = fields.Char()
    one_password_completion_date = fields.Date(
        help="Date of Completion")
    one_password_note = fields.Text()

    # GrubHub
    grubhub_task = fields.Html(default=get_grubhub_task)
    grubhub_task_description = fields.Char()
    grubhub_completion_date = fields.Date(
        help="Date of Completion")
    grubhub_note = fields.Text()

    # Procurify
    procurify_task = fields.Html(default=get_procurify_task)
    procurify_task_description = fields.Char()
    procurify_completion_date = fields.Date(
        help="Date of Completion")
    procurify_note = fields.Text()

    # Software
    software_task = fields.Char(
        default='Required software according Hiring manager')
    software_task_description = fields.Char()
    software_completion_date = fields.Date(
        help="Date of Completion")
    software_note = fields.Text()

    # JIRA
    jira_task = fields.Char(
        default='Send JIRA First Day List link')
    jira_task_description = fields.Char()
    jira_completion_date = fields.Date(
        help="Date of Completion")
    jira_note = fields.Text()

    # Agency
    agency_name = fields.Char(string="Agency Name")
    agency_task_description = fields.Char()
    agency_completion_date = fields.Date(
        help="Date of Completion")
    agency_note = fields.Text()

    agency_contact = fields.Char(string="Agency Contact")
    agency_contact_task_description = fields.Char()
    agency_contact_completion_date = fields.Date(
        help="Date of Completion")
    agency_contact_note = fields.Text()

    signed_contact = fields.Char(string="Signed Contract")
    signed_contact_task_description = fields.Char()
    signed_contact_completion_date = fields.Date(
        help="Date of Completion")
    signed_contact_note = fields.Text()

    informed_agency_start = fields.Char(string="Informed Agency of Start")
    informed_agency_task_description = fields.Char()
    informed_agency_completion_date = fields.Date(
        help="Date of Completion")
    informed_agency_note = fields.Text()

    @api.onchange('name')
    def set_pre_post_hire_onboarding(self):
        pre_hire_ids = self.env['hr.pre.hire.onboarding'].search(
            [('hr_pre_onboarding_id', '=', False)])
        post_hire_ids = self.env['hr.post.hire.onboarding'].search(
            [('hr_post_onboarding_id', '=', False)])
        hr_offer_onboarding_ids = self.env['hr.offer.onboarding'].search(
            [('hr_offer_onboarding_id', '=', False)])
        hr_offer_post_onboarding_ids = self.env[
            'hr.offer.post.hire.onboarding'].search(
            [('hr_offer_post_onboarding_id', '=', False)])
        hr_options_onboarding_ids = self.env['hr.options.onboarding'].search(
            [('hr_options_onboarding_id', '=', False)])
        hr_operations_onboarding_ids = self.env[
            'hr.operations.onboarding'].search(
            [('hr_operations_onboarding_id', '=', False)])
        hr_reception_onboarding_ids = self.env[
            'hr.reception.onboarding'].search(
            [('hr_reception_onboarding_id', '=', False)])
        hr_secure_onboarding_ids = self.env[
            'hr.secure.onboarding'].search(
            [('hr_secure_onboarding_id', '=', False)])

        if self.name:
            if not self.pre_hire_onboarding_ids:
                self.pre_hire_onboarding_ids = [
                    (0, 0, {'name': pre_hire_id.name})
                    for pre_hire_id in pre_hire_ids]
            if not self.post_hire_onboarding_ids:
                self.post_hire_onboarding_ids = [
                    (0, 0, {'name': post_hire_id.name})
                    for post_hire_id in post_hire_ids]
            if not self.hr_offer_onboarding_ids:
                self.hr_offer_onboarding_ids = [
                    (0, 0, {'name': hr_offer_onboarding_id.name})
                    for hr_offer_onboarding_id in hr_offer_onboarding_ids]
            if not self.hr_offer_post_onboarding_ids:
                self.hr_offer_post_onboarding_ids = [
                    (0, 0, {'name': hr_offer_post_onboarding_id.name})
                    for hr_offer_post_onboarding_id
                    in hr_offer_post_onboarding_ids]
            if not self.hr_options_onboarding_ids:
                self.hr_options_onboarding_ids = [
                    (0, 0, {'name': hr_options_onboarding_id.name})
                    for hr_options_onboarding_id in hr_options_onboarding_ids]
            if not self.hr_operations_onboarding_ids:
                self.hr_operations_onboarding_ids = [
                    (0, 0, {'name': hr_operations_onboarding_id.name})
                    for hr_operations_onboarding_id in
                    hr_operations_onboarding_ids]
            if not self.hr_reception_onboarding_ids:
                self.hr_reception_onboarding_ids = [
                    (0, 0, {'name': hr_reception_onboarding_id.name})
                    for hr_reception_onboarding_id in
                    hr_reception_onboarding_ids]
            if not self.hr_secure_onboarding_ids:
                self.hr_secure_onboarding_ids = [
                    (0, 0, {'name': hr_secure_onboarding_id.name})
                    for hr_secure_onboarding_id in
                    hr_secure_onboarding_ids]

    def _get_onchange_create(self):
        return OrderedDict([
            ('set_pre_post_hire_onboarding',
             ['pre_hire_onboarding_ids', 'post_hire_onboarding_ids',
              'hr_offer_onboarding_ids', 'hr_offer_post_onboarding_ids',
              'hr_options_onboarding_ids'])])

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
        return super(HrOnboarding, self).create(vals)


class HRPreHireOnboarding(models.Model):
    _name = 'hr.pre.hire.onboarding'
    _description = 'General Pre-Hire'
    _order = 'sequence'

    name = fields.Text()
    task_completion_date = fields.Date(
        string="Date of Completion", help="Date of Completion")
    initials = fields.Char(help="Initials")
    sequence = fields.Integer()
    hr_pre_onboarding_id = fields.Many2one(
        'hr.onboarding', ondelete='cascade', index=True, copy=False)
    note = fields.Text(string="Notes")


class HRPostHireOnboarding(models.Model):
    _name = 'hr.post.hire.onboarding'
    _description = 'General Post-Hire'
    _order = 'sequence'

    name = fields.Text()
    task_completion_date = fields.Date(
        string="Date of Completion", help="Date of Completion")
    initials = fields.Char(help="Initials")
    sequence = fields.Integer()
    hr_post_onboarding_id = fields.Many2one(
        'hr.onboarding', ondelete='cascade', index=True, copy=False)
    note = fields.Text(string="Notes")


class HROfferOnboarding(models.Model):
    _name = 'hr.offer.onboarding'
    _description = 'HR offer Onboarding'
    _order = 'sequence'

    name = fields.Text()
    task_completion_date = fields.Date(
        string="Date of Completion", help="Date of Completion")
    initials = fields.Char(help="Initials")
    sequence = fields.Integer()
    hr_offer_onboarding_id = fields.Many2one(
        'hr.onboarding', ondelete='cascade', index=True, copy=False)
    note = fields.Text(string="Notes")


class HROfferPostHireOnboarding(models.Model):
    _name = 'hr.offer.post.hire.onboarding'
    _description = 'HR offer Post Hire Onboarding'
    _order = 'sequence'

    name = fields.Text()
    task_completion_date = fields.Date(
        string="Date of Completion", help="Date of Completion")
    initials = fields.Char(help="Initials")
    sequence = fields.Integer()
    hr_offer_post_onboarding_id = fields.Many2one(
        'hr.onboarding', ondelete='cascade', index=True, copy=False)
    note = fields.Text(string="Notes")


class HRoptionsOnboarding(models.Model):
    _name = 'hr.options.onboarding'
    _description = 'HR Options Onboarding'
    _order = 'sequence'

    name = fields.Text()
    task_completion_date = fields.Date(
        string="Date of Completion", help="Date of Completion")
    initials = fields.Char(help="Initials")
    sequence = fields.Integer()
    hr_options_onboarding_id = fields.Many2one(
        'hr.onboarding', ondelete='cascade', index=True, copy=False)
    note = fields.Text(string="Notes")


class HRoperationsOnboarding(models.Model):
    _name = 'hr.operations.onboarding'
    _description = 'HR Operations Onboarding'
    _order = 'sequence'

    name = fields.Text()
    task_completion_date = fields.Date(
        string="Date of Completion", help="Date of Completion")
    initials = fields.Char(help="Initials")
    sequence = fields.Integer()
    hr_operations_onboarding_id = fields.Many2one(
        'hr.onboarding', ondelete='cascade', index=True, copy=False)
    note = fields.Text(string="Notes")


class HRreceptionOnboarding(models.Model):
    _name = 'hr.reception.onboarding'
    _description = 'HR Reception Onboarding'
    _order = 'sequence'

    name = fields.Text()
    task_completion_date = fields.Date(
        string="Date of Completion", help="Date of Completion")
    initials = fields.Char(help="Initials")
    sequence = fields.Integer()
    hr_reception_onboarding_id = fields.Many2one(
        'hr.onboarding', ondelete='cascade', index=True, copy=False)
    note = fields.Text(string="Notes")

class HRsecureOnboarding(models.Model):
    _name = 'hr.secure.onboarding'
    _description = 'HR Security Onboarding'
    _order = 'sequence'

    name = fields.Text()
    task_completion_date = fields.Date(
        string="Date of Completion", help="Date of Completion")
    initials = fields.Char(help="Initials")
    sequence = fields.Integer()
    hr_secure_onboarding_id = fields.Many2one(
        'hr.onboarding', ondelete='cascade', index=True, copy=False)
    note = fields.Text(string="Notes")