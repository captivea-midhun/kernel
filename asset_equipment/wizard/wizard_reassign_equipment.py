# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import fields, models


class WizardReassignEquipment(models.TransientModel):
    _name = 'wizard.reassign.equipment'
    _description = 'Reassign Equipment'

    employee_id = fields.Many2one('hr.employee', string="Assign To")
    location_id = fields.Many2one('stock.location', string="Location")
    department_id = fields.Many2one('hr.department', string="Department")

    def action_notify_reassign_equipment(self, equipment_id, employee_id):
        active_user = self.env.user
        email_to_employees = self.env['hr.employee']
        # Send Mail to New Reassign User
        message_body = """
            <p><span>This is a notification that an equipment record in Odoo has been assigned. Please review the information below and please notify Asset Management of any errors.</span></p>

            <br/>

            <span class="font-weight-bold">Reassignment Info</span><br/>
            <span>[%s] - [%s]</span><br/>
            <span>Assigned by: %s</span><br/><br/>

            <span class="font-weight-bold">New Assignee</span><br/>
            <span>New User: %s </span><br/>
            <span class="class="font-weight-bold">New Location: %s</span><br/><br/>

            <span class="font-weight-bold">Previous Assignee</span><br/>
            <span>User: %s</span><br/>
            <span><span>Location: %s</span><br/>
        """ % (equipment_id.asset_tag_id, equipment_id.display_name,
               active_user.name, self.employee_id.name, self.location_id.display_name,
               employee_id.name if employee_id else '', equipment_id.location_id.display_name)

        user_id = self.env.ref('base.user_admin')
        if employee_id and employee_id.user_id:
            user_id |= employee_id.user_id
        elif employee_id:
            email_to_employees |= employee_id
        if self.employee_id and self.employee_id.user_id:
            user_id |= self.employee_id.user_id
        elif self.employee_id:
            email_to_employees |= self.employee_id

        self.env['mail.mail'].create({
            'body_html': message_body,
            'email_to': ','.join(email_to_employees.mapped('kernel_work_email')),
            'subject': 'Maintenance Reassign Notification',
            'recipient_ids': [(6, 0, user_id.mapped('partner_id').ids)],
            'email_from': active_user.company_id.email,
            'model': 'maintenance.equipment',
            'res_id': equipment_id.id}).send()
        return True

    def wizard_action_reassign_equipment(self):
        assign_user_id = False
        context = dict(self._context) or {}
        if context.get('active_model') and context.get('active_model') != 'maintenance.equipment':
            return {'type': 'ir.actions.act_window_close'}
        equipment_ids = self.env[context['active_model']].browse(context.get('active_ids', []))
        for equipment_id in equipment_ids:
            orignal_employee_id = equipment_id.employee_id
            vals = {'location_id': self.location_id.id, }

            # Update Employee
            employee_id = False
            if self.employee_id and not orignal_employee_id:
                employee_id = self.employee_id
            elif self.employee_id and orignal_employee_id:
                employee_id = self.employee_id
            vals.update({'employee_id': employee_id and employee_id.id or False})

            # Update Department
            department_id = False
            if self.department_id and not equipment_id.department_id:
                department_id = self.department_id
            elif self.department_id and equipment_id.department_id:
                department_id = self.department_id
            vals.update({'department_id': department_id and department_id.id or False})
            self.action_notify_reassign_equipment(equipment_id, orignal_employee_id)
            equipment_id.write(vals)
        return True
