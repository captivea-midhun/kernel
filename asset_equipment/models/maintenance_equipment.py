# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

import re

from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    asset_equipment_ids = fields.One2many(
        'maintenance.equipment', 'asset_id', string="Asset Equipment")


class MaintenanceEquipmentCategory(models.Model):
    _inherit = 'maintenance.equipment.category'

    display_cate_field = fields.Boolean(default=False)
    show_mac_address = fields.Boolean(
        default=False, string="Show MAC Address on Equipment")


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    def action_reassign_euipment(self):
        active_user = self.env.user
        action = self.env.ref('asset_equipment.action_wizard_reassign_euipment').read()[0]
        return action

    def write(self, vals):
        active_user = self.env.user
        allowd_change_field = ['location_id', 'employee_id', 'department_id']
        if not active_user.has_group('maintenance.group_equipment_manager'):
            for field in list(vals.keys()):
                if field not in allowd_change_field:
                    raise ValidationError(_(
                        'You do not have rights to modify %s' % self._description))
        for equipment in self:
            # Manage Log when update or remove employee from equipments
            if vals.get('employee_id'):
                employee_id = self.env['hr.employee'].sudo().browse(vals['employee_id'])
                body = """
                    <div class="o_thread_message_content">
                        <p>Equipment Assigned</p>
                        <ul class="o_mail_thread_message_tracking">
                            <li>
                                Assigned Employee: <span> %s </span>
                                <span class="fa fa-long-arrow-right" role="img" aria-label="Changed" title="Changed"></span>
                                <span> %s </span>
                            </li>
                        </ul>
                    </div>
                """ % (
                    equipment.employee_id.name if equipment.employee_id else '',
                    employee_id and employee_id.name or '')
                self.env['mail.message'].sudo().create(
                    {'model': 'maintenance.equipment',
                     'res_id': equipment.id,
                     'body': body,
                     'message_type': 'notification',
                     'subtype_id': self.env.ref('maintenance.mt_mat_assign').id})
            elif vals.get('employee_id') is False:
                body = """
                    <div class="o_thread_message_content">
                        <ul class="o_mail_thread_message_tracking">
                            <li>
                                Assigned Employee: <span> %s </span>
                                <span class="fa fa-long-arrow-right" role="img" aria-label="Changed" title="Changed"></span>
                            </li>
                        </ul>
                    </div>
                """ % (equipment.employee_id.name)
                self.env['mail.message'].sudo().create(
                    {'model': 'maintenance.equipment',
                     'res_id': equipment.id,
                     'body': body,
                     'message_type': 'notification',
                     'subtype_id': self.env.ref('maintenance.mt_mat_assign').id})

            # Manage Log when update or remove department from equipments
            if vals.get('department_id'):
                department_id = self.env['hr.department'].sudo().browse(vals['department_id'])
                body = """
                    <div class="o_thread_message_content">
                        <p>Equipment Assigned</p>
                        <ul class="o_mail_thread_message_tracking">
                            <li>
                                Assigned Department: <span> %s </span>
                                <span class="fa fa-long-arrow-right" role="img" aria-label="Changed" title="Changed"></span>
                                <span> %s </span>
                            </li>
                        </ul>
                    </div>
                """ % (equipment.department_id.name if equipment.department_id else '',
                       department_id and department_id.name or '')
                self.env['mail.message'].sudo().create(
                    {'model': 'maintenance.equipment',
                     'res_id': equipment.id,
                     'body': body,
                     'message_type': 'notification',
                     'subtype_id': self.env.ref('maintenance.mt_mat_assign').id})
            elif vals.get('department_id') is False and equipment.department_id:
                body = """
                    <div class="o_thread_message_content">
                        <ul class="o_mail_thread_message_tracking">
                            <li>
                                Assigned Department: <span> %s </span>
                                <span class="fa fa-long-arrow-right" role="img" aria-label="Changed" title="Changed"></span>
                            </li>
                        </ul>
                    </div>
                """ % (equipment.department_id.name)
                self.env['mail.message'].sudo().create(
                    {'model': 'maintenance.equipment',
                     'res_id': equipment.id,
                     'body': body,
                     'message_type': 'notification',
                     'subtype_id': self.env.ref('maintenance.mt_mat_assign').id})
        return super(MaintenanceEquipment, self.with_context(tracking_disable=True)).write(vals)

    @api.constrains('mac_address')
    def _check_cpu_speed_format(self):
        if not self.mac_address:
            return
        if not re.match("[a-fA-F0-9:]{17}|[a-fA-F0-9]{12}$", self.mac_address):
            raise UserError(_('MAC Address must be in properly formatted.'
                              'E.g. E4:A9:C8:53:49:E9'))

    @api.model
    def default_get(self, fields):
        res = super(MaintenanceEquipment, self).default_get(fields)
        res.update({'equipment_assign_to': 'other'})
        return res

    @api.depends('end_of_life_cycle')
    def _compute_expected_end_of_life(self):
        date_now = fields.Date.context_today(self)
        for equipment in self:
            expected_end_of_life = False
            if equipment.end_of_life_cycle:
                end_of_life_cycle = str(equipment.end_of_life_cycle).split('.')
                expected_end_of_life = date_now + relativedelta(
                    months=(int(end_of_life_cycle[0]) * 12) + (int(end_of_life_cycle[1])))
            equipment.expected_end_of_life = expected_end_of_life

    @api.depends()
    def _compute_equipment_component_count(self):
        for equipment in self:
            equipment.equipment_component_count = self.search_count(
                [('parent_id', '=', equipment.id)])

    def action_show_components(self):
        equipment_component_ids = self.search([('parent_id', '=', self.id)])
        action = self.env.ref('maintenance.hr_equipment_action').read()[0]
        if len(equipment_component_ids) > 1:
            action['domain'] = [('id', 'in', equipment_component_ids.ids)]
        elif len(equipment_component_ids) == 1:
            form_view = [(self.env.ref('maintenance.hr_equipment_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + \
                                  [(state, view)
                                   for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = equipment_component_ids.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {'default_parent_id': self.id}
        action['context'] = context
        return action

    image_1920 = fields.Image("Image", max_width=1920, max_height=1920)
    image_128 = fields.Image("Image 128", related="image_1920",
                             max_width=128, max_height=128, store=True)
    asset_id = fields.Many2one('account.asset', string='Asset')
    asset_model_id = fields.Many2one(
        'account.asset', related='asset_id.model_id', string='Asset Model', store=True)
    asset_tag_id = fields.Char(string="Asset Tag ID", copy=False)
    equipment_status = fields.Selection(
        [('active', 'Active'), ('retired_disposed', 'Retired/Disposed'),
         ('lost', 'Lost'), ('sold', 'Sold'), ('broken', 'Broken')],
        default='active', string="Status", copy=False, tracking=True)
    purchase_line_id = fields.Many2one('purchase.order.line', string='Purchase Order')
    equipment_brand = fields.Char(string="Brand")
    purchase_date = fields.Date(string="Purchase Date")
    expected_end_of_life = fields.Date(
        string="Expected End of Life", compute='_compute_expected_end_of_life',
        compute_sudo=True, store=True,
        help="On basis of Purchase Date this field is set as adding default 3 years.")
    end_of_life_cycle = fields.Float(string="End of Life Cycle")
    parent_id = fields.Many2one('maintenance.equipment', string="Parent Equipment")
    equipment_component_count = fields.Integer(
        compute='_compute_equipment_component_count', string="Equipment Component Count")
    employee_user_id = fields.Many2one(
        'res.users', related='employee_id.user_id', store=True)
    employee_status = fields.Boolean(related='employee_id.active', string="Employee Status")
    period_selection = fields.Selection([('1', '1 Year'), ('2', '2 Years'), ('3', '3 Years')])

    @api.model
    def update_expected_end(self):
        if self.purchase_date:
            self.expected_end_of_life = self.purchase_date + relativedelta(years=+3)

    @api.onchange('period_selection')
    def _set_warranty_date(self):
        if self.period_selection and self.purchase_date:
            self.warranty_date = self.purchase_date + \
                                 relativedelta(years=+int(self.period_selection))

    @api.onchange('purchase_date')
    def _set_expected_end_life(self):
        if self.purchase_date:
            self.expected_end_of_life = self.purchase_date + relativedelta(years=+3)

    def action_reassign_equipment(self):
        action = self.env.ref('asset_equipment.action_wizard_reassign_euipment').read()[0]
        action['context'] = dict(self.env.context)
        return action

    @api.onchange('asset_id')
    def onchange_asset_id(self):
        warning = {}
        if not self.asset_id:
            return {}
        equipment_ids = self.search([('asset_id', '=', self.asset_id.id)])
        if equipment_ids:
            warning = {
                'title': _("Warning for %s") % self.asset_id.name,
                'message': "Asset is already assigned to %s" % ' , '.join(
                    equipment_ids.mapped('name'))}
        return {'warning': warning}

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive equipments.'))
        return True

    # Asset Details Tab fields
    product_info = fields.Char(string="Product Info")
    date_create = fields.Date(
        string="Create Date", default=fields.Date.context_today)

    # Following fields are related to computers equipment category only
    mac_address = fields.Char(string="MAC Address")
    memory = fields.Selection(
        [('8', '8'), ('16', '16'), ('32', '32'), ('64', '64'),
         ('other', 'Other')], string="Memory(GB)")
    disk_space = fields.Selection(
        [('128', '128'), ('256', '256'), ('512', '512'), ('1_TB', '1TB'),
         ('2_TB', '2TB'), ('other', 'Other')], string="Disk Space(GB)")
    processor = fields.Selection(
        [('intel', 'Intel'), ('amd', 'AMD'), ('other', 'Other')], string="Processor")
    cpu_speed = fields.Float(string="CPU Speed(GHZ)")
    bluetooth_mac = fields.Char(string="Bluetooth MAC")
    euipment_calibration_doc = fields.Binary(string="Calibration")
    calibration_filename = fields.Char(string="Calibration FileName")
    euipment_warranty_doc = fields.Binary(string="Warranty Document")
    warranty_doc_filename = fields.Char(string="Warranty Document FileName")
    sale_date = fields.Date(string="Sale Date")
    sold_to = fields.Char(string="Sold To")
    disposal_document = fields.Binary(string="Disposal Document")
    disposal_document_filename = fields.Char(string="Disposal Document FileName")
    retired_note = fields.Text(string="Retired Note")
    sale_amount = fields.Float(string="Sale Amount")
    currency_id = fields.Many2one(related='company_id.currency_id', string="Currency", store=True)
    location_id = fields.Many2one(
        'stock.location', string="Location", domain="[('usage', '=', 'internal')]", tracking=True)
    display_cate_field = fields.Boolean(
        related='category_id.display_cate_field', store=True)
    show_mac_address = fields.Boolean(
        related='category_id.show_mac_address', store=True)

    _sql_constraints = [
        ('asset_tag_id_unique_kernel', 'unique(asset_tag_id)', 'Asset ID must be unique !'), ]

    @api.onchange('purchase_line_id')
    def onchange_purchase_line_id(self):
        if not self.purchase_line_id:
            self.purchase_date = False
            self.cost = 0.00
            self.partner_id = False
        self.purchase_date = self.purchase_line_id.date_planned
        self.cost = self.purchase_line_id.price_subtotal
        self.partner_id = self.purchase_line_id.order_id.partner_id.id

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if not self.employee_id:
            self.department_id = False
        self.department_id = self.employee_id.department_id and \
                             self.employee_id.department_id.id or False


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        res = super(PurchaseOrderLine, self)._name_search(
            name=name, args=args, operator=operator,
            limit=limit, name_get_uid=name_get_uid)
        if self._context.get('from_equipment', False):
            if args is None:
                args = []
            args += ([('order_id.name', operator, name)])
            po_lines = self.search(args)
            return po_lines.name_get()
        return res

    def name_get(self):
        if not self._context.get('from_equipment', ''):
            return super(PurchaseOrderLine, self).name_get()
        return [(line.id, '[%s] %s' % (
            line.order_id.name, str(line.name))) for line in self]


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    cost = fields.Float(string="Cost")
    currency_id = fields.Many2one(
        related='company_id.currency_id', string="Currency", store=True)
    maintenance_type = fields.Selection(
        [('corrective', 'Repair'), ('preventive', 'Calibration')],
        string='Maintenance Type', default="corrective")
    next_action_date = fields.Date(
        related='equipment_id.next_action_date', string='Next Preventative Maintenance', store=True)
