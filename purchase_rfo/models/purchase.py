# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import fields, api, models, tools, _
from odoo.exceptions import Warning, ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purpose_type = fields.Many2one('purpose.type', string="Purpose")
    current_user = fields.Many2one('res.users', string="Current User",
                                   default=lambda self: self.env.user)
    bista_subcontracted_ids = fields.Many2many(
        "mrp.production",
        "purchase_order_rel_mrp_production_orders",
        "purchase_id",
        "production_id",
        string="Subcontracted",
        copy=False,
        help="Subcontracted Manufacturing Orders")
    bista_manufacturing_orders_count = fields.Integer(
        string="Manufacturing Orders Count", compute='_compute_manufacturing_orders_count')

    @api.depends('invoice_ids', 'invoice_ids.state', 'invoice_ids.amount_residual')
    def _compute_get_payment_journal(self):
        account_payment = self.env['account.payment']
        for order in self:
            account_payment = self.env['account.payment']
            account_payment_ids = account_payment.search(
                [('invoice_ids', 'in', order.invoice_ids.ids),
                 ('state', '=', 'posted')], order="create_date desc", limit=1)
            order.purchase_payment_journal_id = account_payment_ids.journal_id.id

    @api.depends('invoice_ids', 'invoice_ids.state', 'invoice_ids.amount_residual')
    def _compute_get_unpaid_amout(self):
        for order in self:
            unpaid_amount = order.invoice_ids.filtered(
                lambda inv: inv.state == 'posted').mapped('amount_residual')
            order.unpaid_amount = sum(unpaid_amount) or 0.00

    @api.depends('order_line', 'picking_ids', 'order_line.qty_received', 'order_line.product_qty')
    def _compute_unreceived_qty(self):
        for purchase in self:
            unreceived_qty = 0.00
            qty_orderd = sum(purchase.order_line.filtered(
                lambda l: l.product_id.type != 'service').mapped('product_qty'))
            picking_ids = purchase.picking_ids.filtered(
                lambda pick: pick.picking_type_id.code == 'incoming' and pick.state != 'cancel')
            if not picking_ids:
                unreceived_qty = 0.00
            else:
                qty_received = sum(picking_ids.mapped('move_ids_without_package').filtered(
                    lambda mv: mv.state == 'done' and mv.product_id.type != 'service').mapped(
                    'quantity_done'))
                cancelled_qty = sum(picking_ids.mapped('move_ids_without_package').filtered(
                    lambda mv: mv.state == 'cancel' and mv.product_id.type != 'service').mapped(
                    'product_uom_qty'))
                unreceived_qty = qty_orderd - (qty_received + cancelled_qty)
            purchase.unreceived_qty = unreceived_qty

    @api.constrains('user_id')
    def _check_user_allow_access(self):
        if not self.user_id:
            return
        active_user = self.env.user
        if not active_user.has_group('purchase.group_purchase_manager') and \
                self.user_id.id != active_user.id:
            raise ValidationError(_('You have no rights to modify the requestor.'))

    @api.depends('state')
    def _get_approve_rfo(self):
        user_id = self.env.user
        for purchase in self:
            if (purchase.department_id.id in user_id.department_ids.ids or user_id.has_group(
                    'purchase_rfo.group_rfo_approve')):
                purchase.is_approve_rfo = True
            else:
                purchase.is_approve_rfo = False

    rfo_name = fields.Char(string="RFO Reference", copy=False, default='New')
    interchanging_po_sequence = fields.Char(
        'PO Sequence Reference', copy=False)
    department_id = fields.Many2one('hr.department', string="Project")
    manager_id = fields.Many2one('res.users', string='Project Manager')
    state = fields.Selection(selection_add=[
        ('draft', 'RFO'),
        ('sent', 'RFO Sent'),
        ('to approve', 'To Approve'),
        ('awaiting_approval', 'Awaiting Approval'),
        ('approved', 'Approved'),
        ('purchase', 'Purchased'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Department')
    export_restriction = fields.Boolean('Export Control')
    purchase_payment_journal_id = fields.Many2one(
        'account.journal', compute='_compute_get_payment_journal', store=True,
        domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]")
    po_payment_notes = fields.Text(string="Purchasing Notes")
    courier_id = fields.Many2one('purchase.delivery.courier', string="Courier")
    tracking_number = fields.Char(track_visibility='onchange')
    approver_user_id = fields.Many2one(
        'res.users', string="Approved By", track_visibility='onchange', copy=False)
    po_notes = fields.Text(string="PO Notes")
    expected_date = fields.Date(string="Desired Date")
    days_disruption = fields.Selection(
        [('zero_to_three', '0 to 3 days'),
         ('four_to_ten', '4 to 10 days'),
         ('eleven_to_thirty', '11 to 30 days'),
         ('overt_thirty', 'Over 30 days')], default='overt_thirty',
        string="Days to Major Disruption", track_visibility='onchange')
    vendor_days_receive = fields.Selection(
        [('lees_one_week', 'Less than 1 week'),
         ('one_to_four_week', '1 to 4 weeks'),
         ('more_four_week', 'More than 4 weeks'),
         ('no_alternative', 'No reasonable alternative')], default='lees_one_week',
        string="Alternative Vendor Days to Receive", track_visibility='onchange')
    escalation = fields.Selection(
        [('none', 'None'), ('level_one', 'Level 1(Purchasing Manager)'),
         ('level_two', 'Level 2 (Jason)'),
         ('level_three', 'Level 3 (Jason + Team Lead + Bryan)')],
        default='none', string='Escalation', track_visibility='onchange')
    unpaid_amount = fields.Float(compute='_compute_get_unpaid_amout', store=True, compute_sudo=True)
    shipping_address_id = fields.Many2one('res.partner', string="Shipping Address")
    unreceived_qty = fields.Float(compute='_compute_unreceived_qty', store=True, compute_sudo=True)
    nda = fields.Boolean('NDA')
    purchaser_id = fields.Many2one('res.users', string="Purchaser", track_visibility='onchange')
    date_order = fields.Datetime(
        'Order Date', required=True, states={}, index=True, copy=False, default=fields.Datetime.now,
        help="Depicts the date where the Quotation should be validated and converted into a "
             "purchase order.")
    is_approve_rfo = fields.Boolean(compute=_get_approve_rfo, compute_sudo=True)
    purchase_payment_method = fields.Selection(
        [('citibank_bank', 'Citibank: Bank Transfer'),
         ('citibank_check', 'Citibank: Check'),
         ('citibank_paypal', 'Citibank: Paypal'),
         ('american_express', 'American Express'),
         ('credit_terms', 'Credit Terms'),
         ('other', 'Other')], string="Payment Method", track_visibility='onchange')
    rfo_request_reason = fields.Text(string="Reason for the Request")
    invoice_status = fields.Selection([
        ('no', 'Nothing to Bill'),
        ('to invoice', 'Waiting Bills'),
        ('invoiced', 'Fully Billed'),
    ], string='Billing Status', compute='_get_invoiced', store=True,
        readonly=True, copy=False, default='no', track_visibility='onchange')

    @api.onchange('expected_date')
    def onchange_expected_date(self):
        if self.expected_date:
            self.date_planned = self.expected_date

    def _check_users_read_write_access(self):
        for order in self:
            # If access request from mail link than allow to see
            # access request with public user is allowed
            # Requested Ticket Number: 4,749: Issue: Users invited to view PO cannot view PO
            if self.env.user.has_group('purchase.group_purchase_manager') or \
                    self.env.user.id == self.env.ref('base.public_user').id:
                continue
            if self.env.user.department_ids and order.state not in [
                'draft', 'awaiting_approval', 'approved', 'cancel']:
                raise ValidationError(
                    "You do not have rights to modify purchase order in %s state!" %
                    (dict(order._fields['state'].selection).get(order.state)))
            if not self.env.user.department_ids and order.state not in [
                'draft', 'awaiting_approval', 'cancel']:
                raise ValidationError(
                    "You do not have rights to modify RFO in %s state!" %
                    (dict(order._fields['state'].selection).get(order.state)))

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        super(PurchaseOrder, self)._onchange_picking_type_id()
        if self.picking_type_id and self.picking_type_id.warehouse_id and self.picking_type_id.warehouse_id.partner_id:
            self.shipping_address_id = self.picking_type_id.warehouse_id.partner_id.id
        else:
            self.shipping_address_id = False

    @api.onchange('shipping_address_id')
    def _onchange_shipping_address_id(self):
        if self.default_location_dest_id_usage == 'customer':
            self.dest_address_id = self.shipping_address_id

    @api.model
    def default_get(self, fields_list):
        res = super(PurchaseOrder, self).default_get(fields_list)
        res.update({'notes': self.env['ir.config_parameter'].sudo().get_param(
            'purchase_rfo.terms_conditions')})
        return res

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        res = super(PurchaseOrder, self).onchange_partner_id()
        if not self.partner_id:
            self.export_restriction = False
            return res
        self.export_restriction = self.partner_id.export_restriction
        return res

    @api.onchange('department_id')
    def onchange_department_id(self):
        if self.department_id and self.department_id.user_id:
            self.manager_id = self.department_id.user_id.id
        else:
            self.manager_id = False

        if self.department_id and self.department_id.analytic_account_id:
            self.analytic_account_id = self.department_id.analytic_account_id.id
        else:
            self.analytic_account_id = False

    @api.onchange('analytic_account_id')
    def onchange_analytic_account_idd(self):
        self.order_line.update(
            {'account_analytic_id': self.analytic_account_id and
                                    self.analytic_account_id.id or False})

    @api.model
    def create(self, vals):
        """"
            Override the method to create separate sequence for RFO
        """
        if vals.get('name', 'New') == 'New':
            name = self.env['ir.sequence'].next_by_code('purchase.order.rfo') or 'New'
            vals['rfo_name'] = vals['name'] = name
        order_id = super(PurchaseOrder, self).create(vals)
        message = self.env['mail.message'].search(
            [('model', '=', 'purchase.order'), ('res_id', '=', order_id.id)], limit=1)
        if message:
            message.body = message.body.replace("Purchase Order created", "RFO Created")
        return order_id

    def button_awaiting_approval(self):
        if not self.order_line:
            raise Warning(_('Without product items you can not request for approval.'))
        self.write({'state': 'awaiting_approval'})
        context = dict(self.env.context)
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        web_base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        context.update({'web_base_url': web_base_url})
        
        if self.amount_total > 100:
            user_id = self.user_id
            if user_id.email:
                email_from = tools.formataddr((user_id.name, user_id.email))
            else:
                email_from = self.env.company.catchall
            email_template_obj = self.env.ref(
                'purchase_rfo.rfo_approval_email_template')
            email_template_obj.with_context(context).sudo().send_mail(
                self.id, force_send=True, email_values={
                    'email_to': self.manager_id.email, 'email_from': email_from})
        return {}

    def button_approved(self):
        user_id = self.env.user
        if not self.is_approve_rfo and not self._context.get('process'):
            raise Warning(_('Only Department Manager or RFO Approve Manager can approve RFO.'))
        self.write({'state': 'approved', 'approver_user_id': user_id.id})
        context = dict(self.env.context)
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        web_base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        context.update({'web_base_url': web_base_url})
        manager_id = self.manager_id   
        if manager_id.email:
            email_from = tools.formataddr((manager_id.name, manager_id.email))
        else:
            email_from = self.env.company.catchall
        
        if self.amount_total > 1000 and self.department_id.id != 9 and self.department_id.id != 6:
            template_id = self.env['ir.model.data'].sudo().get_object_reference(
            'purchase_rfo', 'rfo_approved_notify_email_template')[1]
            email_template_obj = self.env[
            'mail.template'].sudo().browse(template_id)
            email_template_obj.sudo().with_context(context).send_mail(
            self.id, force_send=True, email_values={'email_to': 'ryan.field@kernel.co',
                                                    'email_from': email_from})     
        else:
            template_id = self.env['ir.model.data'].sudo().get_object_reference(
                'purchase_rfo', 'rfo_approved_email_template')[1]
            email_template_obj = self.env[
                'mail.template'].sudo().browse(template_id)
            email_template_obj.sudo().with_context(context).send_mail(
                self.id, force_send=True, email_values={'email_to': self.user_id.email,
                                                        'email_from': email_from})
        return {}

    def write(self, vals):
        for order in self:
            if vals.get('state') == 'approved' and vals.get('approver_user_id') == \
                    self.env.ref('base.user_root').id:
                vals.update({'approver_user_id': order.manager_id.id})
            if vals.get('state') == 'purchase':
                vals.update({'name': order.rfo_name.replace('RFO', 'PO')})
            order._check_users_read_write_access()
        return super(PurchaseOrder, self).write(vals)

    def button_confirm(self):
        company_curr_id = self.env.company.currency_id
        mrp_production_obj = self.env['mrp.production']
        stock_picking_obj = self.env['stock.picking']
        for order in self:
            if order.state != 'approved':
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step' \
                    or (order.company_id.po_double_validation == 'two_step'
                        and order.amount_total < company_curr_id._convert(
                        order.company_id.po_double_validation_amount,
                        order.currency_id, order.company_id,
                        order.date_order or fields.Date.today())) \
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
                order.purchaser_id = self.env.user.id or False
            else:
                order.write({'state': 'to approve'})
            for picking in order.picking_ids:
                picking.write({'origin': order.name})
                picking.move_lines.write({'origin': order.name})
                data_query = """
                    select sm1.production_id from stock_move sm1 where id in (
                    select smmr.move_orig_id from stock_move_move_rel smmr
                    inner join stock_move sm on sm.id=smmr.move_dest_id 
                    left join stock_picking sp on sp.id=sm.picking_id where sp.id= %s)"""
                self._cr.execute(data_query, (picking.id,))
                for records in self._cr.fetchall():
                    order.write({'bista_subcontracted_ids': [(4, records[0])]})
                    if picking.picking_type_id.code == 'incoming':
                        mrp_production = mrp_production_obj.browse(records[0])
                        stock_picking = stock_picking_obj.search(
                            [('group_id', '=', mrp_production.procurement_group_id.id),
                             ('group_id', '!=', False), ])
                        stock_picking.write(
                            {'bista_incoming_picking_group_id': picking.group_id.id})
            context = dict(self.env.context)
            web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            web_base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
            context.update({'web_base_url': web_base_url})
            manager_id = self.env.user
            if manager_id.email:
                email_from = tools.formataddr((manager_id.name, manager_id.email))
            else:
                email_from = self.env.company.catchall
            template_id = self.env['ir.model.data'].sudo().get_object_reference(
                'purchase_rfo', 'po_email_template')[1]
            email_template_obj = self.env['mail.template'].sudo().browse(template_id)
            email_template_obj.sudo().with_context(context).send_mail(
                self.id, force_send=True, email_values={
                    'email_to': self.user_id.email, 'email_from': email_from})
        return True

    def button_draft(self):
        """"
            Override the method when PO reset to draft update the name field.
        """
        res = super(PurchaseOrder, self).button_draft()
        self.write({'interchanging_po_sequence': self.name, 'name': self.rfo_name})
        return res

    def button_cancel(self):
        for order in self:
            if order.state == 'purchase' and not order.env.user.has_group(
                    'purchase.group_purchase_manager'):
                raise Warning(_('Only Purchase Manager allow to cancel order'))
        return super(PurchaseOrder, self).button_cancel()

    def _cron_approve_purchase_order(self):
        purchase_order = self.env['purchase.order'].search(
            [('state', '=', 'awaiting_approval'), ('amount_total', '<=', 100)])
        for record in purchase_order:
            record.with_context(process='Automated').button_approved()

    def button_fully_billed(self):
        """ Update purchase orders billing status to `fully billed` """

        for order in self:
            if order.state in ('purchase', 'done'):
                order.invoice_status = 'invoiced'
            else:
                raise ValidationError(
                    "The record %s should be in Purchased state!" % (order.name))

    @api.depends('bista_subcontracted_ids')
    def _compute_manufacturing_orders_count(self):
        self.bista_manufacturing_orders_count = len(self.bista_subcontracted_ids)

    def action_manufacturing_orders(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "mrp.production",
            "views": [[self.env.ref('mrp.mrp_production_tree_view').id, "tree"],
                      [self.env.ref('mrp.mrp_production_form_view').id, "form"],
                      [self.env.ref('mrp.view_production_graph').id, "graph"],
                      [self.env.ref('mrp.view_production_pivot').id, "pivot"],
                      [self.env.ref('mrp.view_production_calendar').id, "calendar"],
                      [self.env.ref('mrp.mrp_production_kanban_view').id, "kanban"], ],
            "name": _("Manufacturing Orders"),
            "domain": [["id", "in", self.bista_subcontracted_ids.ids]],
            "context": {"create": False},
        }

    def action_view_picking(self):
        res = super(PurchaseOrder, self).action_view_picking()
        res['context']['form_view_initial_mode'] = 'edit'
        return res

    # Ticket Number: 5, 326: Issue: PO Unreceived Qty: Correction
    def update_po_receive_qty(self):
        """
        Updated to received Qty.
        """
        stock_move_obj = self.env['stock.move'].sudo()
        for line in self.order_line:
            moves = stock_move_obj.search([('purchase_line_id', '=', line.id),
                                           ('state', '=', 'done')])
            sum_quantity_done = sum(moves.mapped('quantity_done'))
            self._cr.execute("UPDATE purchase_order_line SET qty_received = %s, \
                             product_qty=%s WHERE id = %s",
                             [sum_quantity_done, sum_quantity_done, line.id])
            self._cr.execute("update purchase_order set unreceived_qty=%s where id=%s",
                             [0, line.order_id.id])


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id')
    def onchange_product_id(self):
        super(PurchaseOrderLine, self).onchange_product_id()
        product = self.product_id
        if not product:
            self.account_id = False
        if product:
            self.product_sku = product.default_code
            if product.type == 'product':
                # expense_account = self.env['ir.config_parameter'].sudo().get_param(
                #     'purchase_rfo.inventoried_product_expense_account_id')
                # self.account_id = int(expense_account)
                self.set_expense_account()

    product_sku = fields.Char(string="SKU")
    line_url = fields.Char(string="URL", default='')
    account_id = fields.Many2one('account.account', string="Expense Account",
                                 domain=lambda self: [('tag_ids', 'in', self.env.ref(
                                     'purchase_rfo.account_tag_expense_account').ids)])

    @api.model
    def create(self, values):
        line = super(PurchaseOrderLine, self).create(values)
        if line.product_id.type == 'product':
            # expense_account = self.env['ir.config_parameter'].sudo().get_param(
            #     'purchase_rfo.inventoried_product_expense_account_id')
            # line.account_id = int(expense_account)
            line.set_expense_account()
        return line

    def write(self, vals):
        line = super(PurchaseOrderLine, self).write(vals)
        if 'product_qty' in vals:
            for record in self:
                if not record.account_id and record.product_id.type == 'product':
                    # expense_account = self.env['ir.config_parameter'].sudo().get_param(
                    #     'purchase_rfo.inventoried_product_expense_account_id')
                    # self.account_id = int(expense_account)
                    record.set_expense_account()
        return line

    def set_expense_account(self):
        for line in self:
            categ_id = line.product_id.categ_id
            if categ_id:
                res_id_str = 'product.category,' + str(categ_id.id)
                expense_account = self.env['ir.property'].sudo().search([('name', '=', 'property_stock_account_input_categ_id'),
                                                                  ('company_id', '=', line.order_id.company_id.id),
                                                                  ('res_id', '=', res_id_str)], limit=1)
                if not expense_account:
                    expense_account = self.env['ir.property'].sudo().search(
                        [('name', '=', 'property_stock_account_input_categ_id'),
                         ('company_id', '=', line.order_id.company_id.id)], limit=1)
                expense_account_id = expense_account and expense_account.value_reference and ',' in expense_account.value_reference and \
                                     expense_account.value_reference.split(',')[1]
                if expense_account_id:
                    line.account_id = self.env['account.account'].sudo().browse(int(expense_account_id))
