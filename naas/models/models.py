# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class Experiment(models.Model):
    _name = 'naas.experiment'
    _description = 'Experiment'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, tracking=True)

    task_ids = fields.One2many(comodel_name='naas.experiment.task', inverse_name='experiment_id', string="Default Tasks")
    subject_ids = fields.One2many(comodel_name='naas.subject', inverse_name='experiment_id', string="Participants")

class ExperimentTask(models.Model):
    _name = 'naas.experiment.task'
    _description = 'Experiment Task'
    _order = 'group asc, name asc'
    _inherit = ['mail.thread']
    _rec_name = 'computed_name'

    group = fields.Char()
    name = fields.Char()
    completed = fields.Boolean(tracking=True)
    completed_date = fields.Datetime(tracking=True)
    notes = fields.Text(tracking=True)

    # Special types
    task_type = fields.Selection([
        ('default', 'Default'),
        ('event', 'Event'),
        ('attachment', 'Attachment'),
        ('data', 'Data'),
        ('payment', 'Payment')
    ])

    scheduled_from = fields.Datetime(string="Scheduled From", tracking=True)
    scheduled_to = fields.Datetime(string="Scheduled To", tracking=True)
    attachment = fields.Binary(string="File", tracking=True)
    data_session_id = fields.Char(string="Data Session ID", tracking=True)
    payment_method = fields.Char(string="Payment Method", tracking=True)
    payment_amount = fields.Float('Payment Amount', digits=(12,2), tracking=True)
    transaction_code = fields.Char('Transaction Code', tracking=True)

    # one or the other
    experiment_id = fields.Many2one('naas.experiment', ondelete='cascade', index=True, copy=False)
    subject_id = fields.Many2one('naas.subject', ondelete='cascade', index=True, copy=False)

    experiment_name = fields.Char(related='experiment_id.name', string="Experiment")
    subject_name = fields.Char(related='subject_id.name', string="Subject")

    computed_name = fields.Char(compute='_compute_name', string="Task")
    @api.depends('group', 'name')
    def _compute_name(self):
        for record in self:
            record.computed_name = f"{record.group} > {record.name}"

    @api.onchange('completed')
    def _onchange_completed(self):
        if self.completed:
            self.completed_date = fields.Datetime.now()
        else:
            self.completed_date = None

    @api.constrains('scheduled_from','scheduled_to')
    def _check_date(self):
        if self.scheduled_from.date() != self.scheduled_to.date():
            raise ValidationError('Scheduled From and Scheduled To must fall on the same date')
        if self.scheduled_from >= self.scheduled_to:
            raise ValidationError('Scheduled To must greater than Scheduled From')

    @api.model
    def unlink(self):
        raise UserError('You cannot delete tasks!')

    @api.model
    def edit(self, args):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'naas.experiment.task',
            'res_id': args[0],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'flags': {'form': {'action_buttons': True}},
            'context': {'create': False}
        }

class Prospect(models.Model):
    _name = 'naas.prospect'
    _description = "Prospect"
    _inherit = ['mail.thread']

    internal_screening_id = fields.Char(required=True, tracking=True, string="Screening ID")
    submitted_date = fields.Datetime(required=True, tracking=True, default=lambda self: fields.Datetime.now())
    first_name = fields.Char(tracking=True)
    last_name = fields.Char(tracking=True)
    email = fields.Char(tracking=True)
    phone = fields.Char(tracking=True)
    zip_code = fields.Char(tracking=True)
    birth_month = fields.Char(tracking=True) # comes in as char from google sheets
    birth_year = fields.Integer(tracking=True)
    gender = fields.Char(tracking=True)
    can_contact = fields.Char(tracking=True) # comes in as string from google sheets

    subject_ids = fields.One2many(comodel_name='naas.subject', inverse_name='prospect_id', string="Subject In")

    name = fields.Char(compute='_compute_name')
    @api.depends('first_name', 'last_name')
    def _compute_name(self):
        for record in self:
            record.name = f"{record.first_name} {record.last_name}"

class Subject(models.Model):
    _name = 'naas.subject'
    _description = "Subject"
    _inherit = ['mail.thread']

    is_created = fields.Boolean()
    internal_subject_id = fields.Char(required=True, tracking=True, string="Subject ID")
    
    status = fields.Selection([
        ('active', 'Active'),
        ('ineligible', 'Ineligible'),
        ('withdrawn', 'Withdrawn'),
        ('completed', 'Completed')
    ], required=True, tracking=True, default="active")

    experiment_id = fields.Many2one('naas.experiment', required=True, ondelete='cascade', index=True, copy=False)
    prospect_id = fields.Many2one('naas.prospect', required=True, ondelete='cascade', index=True, copy=False)
    
    task_ids = fields.One2many(comodel_name='naas.experiment.task', inverse_name='subject_id', string="Tasks")

    experiment_name = fields.Char(related='experiment_id.name', string="Experiment")
    prospect_name = fields.Char(related='prospect_id.name', string="Prospect")

    name = fields.Char(compute='_compute_name')
    @api.depends('experiment_name', 'prospect_name')
    def _compute_name(self):
        for record in self:
            record.name = f"{record.experiment_name} / {record.prospect_name}"

    @api.constrains('prospect_id', 'experiment_id')
    def _check_description(self):
        for record in self:
            exists = self.search(['&',('prospect_id.id','=',record.prospect_id.id),'&',('experiment_id.id','=',record.experiment_id.id),('id','!=',record.id)], count=True)
            if exists > 0:
                raise ValidationError("Subject already exists")

    @api.model
    def create(self, vals):
        vals['is_created'] = True
        task_ids = self.env['naas.experiment.task'].search([('experiment_id', '=', vals['experiment_id'])])
        new_tasks = [ (0, 0, {
            'task_type': task_id.task_type,
            'group': task_id.group,
            'name': task_id.name
        }) for task_id in task_ids ]
        vals['task_ids'] = new_tasks
        vals['status'] = 'active'
        return super(Subject, self).create(vals)

    def add_missing_tasks(self):
        task_ids = self.env['naas.experiment.task'].search([('experiment_id', '=', self.experiment_id.id)])
        subject_task_names = set([t.computed_name for t in self.env['naas.experiment.task'].search([('subject_id', '=', self.id)])])

        # add all new experiment tasks that don't exist on the subject
        new_tasks = [ ({
            'subject_id': self.id,
            'task_type': task_id.task_type,
            'group': task_id.group,
            'name': task_id.name
        }) for task_id in task_ids if task_id.computed_name not in subject_task_names ]

        self.env['naas.experiment.task'].create(new_tasks)