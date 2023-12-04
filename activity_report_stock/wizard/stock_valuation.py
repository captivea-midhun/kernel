# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

import base64
import tempfile
from datetime import datetime

import pytz
import xlwt
from dateutil import parser

from odoo import models, api, fields, _
from odoo.exceptions import Warning, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from . import xls_format
from ..report.stock_valuation import StockValuationCategory


class StockValuationDateReport(models.TransientModel, StockValuationCategory):
    _name = 'stock.valuation.ondate.report'
    _description = 'Valuation Report'

    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    warehouse_ids = fields.Many2many('stock.warehouse', string='warehouse')
    location_id = fields.Many2many('stock.location', string='Location')
    start_date = fields.Date(string='From Date',
                             required=True,
                             default=lambda *a: (parser.parse(datetime.now().strftime(DF))))
    end_date = fields.Date(string='To Date', required=True,
                           default=lambda *a: (parser.parse(datetime.now().strftime(DF))))
    filter_product_ids = fields.Many2many('product.product', string='Products')
    filter_product_categ_ids = fields.Many2many('product.category', string='Categories')
    report_data = fields.Binary()

    def find_warehouses(self, company_id):
        warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', company_id)])
        return warehouse_ids

    @api.onchange('warehouse_ids')
    def onchange_warehouse(self):
        location_obj = self.env['stock.location']
        company_id = self.company_id.id
        if not company_id:
            company_id = self.env.user.company_id.id
        warehouse_ids = self.warehouse_ids
        if warehouse_ids:
            locations_ids = location_obj.search(
                [('id', 'child_of', warehouse_ids.mapped('view_location_id').ids),
                 ('usage', '=', 'internal')]).ids
        else:
            warehouse_ids = self.find_warehouses(company_id)
            locations_ids = location_obj.search(
                [('id', 'child_of', warehouse_ids.mapped('view_location_id').ids),
                 ('usage', '=', 'internal')]).ids
        sel_location_ids = self.location_id.ids
        if sel_location_ids:
            new_location_ids = list(set(sel_location_ids).intersection(locations_ids))
            self.write({'location_id': [(6, 0, new_location_ids)]})
        return {'domain': {'location_id': [('id', 'in', locations_ids)]}}

    @api.constrains('start_date', 'end_date')
    def check_date(self):
        if self.start_date and self.end_date and (self.start_date > self.end_date):
            raise ValidationError(_('End date should be greater than start date.'))

    def print_report(self):
        """
            Print report either by warehouse or product-category
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        datas = {
            'form':
                {'company_id': self.company_id and [self.company_id.id] or [],
                 'warehouse_ids': [y.id for y in self.warehouse_ids],
                 'location_id': self.location_id and self.location_id.id or False,
                 'start_date': self.start_date,
                 'end_date': self.end_date,
                 'id': self.id,
                 'filter_product_ids': [p.id for p in self.filter_product_ids],
                 'filter_product_categ_ids': [p.id for p in self.filter_product_categ_ids]}}

        if [y.id for y in self.warehouse_ids] and (not self.company_id):
            self.warehouse_ids = []
            raise Warning(_(
                'Please select company of those warehouses to get correct view.\
                You should remove all warehouses first from selection field.'))
        return self.env.ref(
            'activity_report_stock.action_stock_valuation_ondate'
        ).with_context(landscape=True).report_action(self, data=datas)

    def _to_company(self, company_ids):
        company_obj = self.env['res.company']
        warehouse_obj = self.env['stock.warehouse']
        if not company_ids:
            company_ids = [x.id for x in company_obj.search([])]
        selected_companies = []
        for company_id in company_ids:
            if warehouse_obj.search([('company_id', '=', company_id)]):
                selected_companies.append(company_id)
        return selected_companies

    def xls_get_warehouses(self, warehouses, company_id):
        warehouse_obj = self.env['stock.warehouse']
        if not warehouses:
            return 'ALL'

        warehouse_rec = warehouse_obj.search([
            ('id', 'in', warehouses), ('company_id', '=', company_id)])
        return warehouse_rec and ",".join([x.name for x in warehouse_rec]) or '-'

    @api.model
    def _po_not_received_qty(self, product_id):
        product = self.env['product.product'].browse(product_id)
        po_line_ids = self.env['purchase.order.line'].search(
            [('product_id', '=', product.id), ('state', '=', 'purchase'),
             ('order_id.picking_ids', '!=', False)])
        total_po_not_received_qty = 0
        for po_line_id in po_line_ids.filtered(lambda line: line.product_qty > line.qty_received):
            remaining_qty = po_line_id.product_qty - po_line_id.qty_received
            total_po_not_received_qty += remaining_qty
        return total_po_not_received_qty or 0.0

    def _product_detail(self, product_id):
        product = self.env['product.product'].browse(product_id)
        variable_attributes = product.attribute_line_ids.filtered(
            lambda l: len(l.value_ids) > 1).mapped('attribute_id')
        variant = False
        variant = product.product_template_attribute_value_ids._get_combination_name()

        if variable_attributes:
            variant = product.product_template_attribute_value_ids._get_combination_name()
        product_name = variant and "%s (%s)" % (
            product.name, variant) or product.name
        return product_name, product.barcode, product.default_code

    def _get_location_ids(self):
        """
        Get Location ids based on selected warehouse and selected location,
        :return: locations_ids : List of location ids
        """
        location_obj = self.env['stock.location']
        company_id = self.company_id.id
        if not company_id:
            company_id = self.env.user.company_id.id
        warehouse_ids = self.warehouse_ids
        if not warehouse_ids:
            # Get all warehouses
            warehouse_ids = self.find_warehouses(company_id)
        locations = self.location_id.ids
        if not locations:
            # Get location based on Warehouse
            locations_ids = location_obj.search(
                [('id', 'child_of', warehouse_ids.mapped('view_location_id').ids),
                 ('usage', '=', 'internal')]).ids
        else:
            # Get child location of selected location
            locations_ids = location_obj.search([('id', 'child_of', locations)]).ids
        return locations_ids

    def _get_location(self, product_id):
        """
        Get location name based on ending date
        :param product_id: Integer Product Id
        :return: location_name_str: String of location name
        """
        locations_names = []
        location_obj = self.env['stock.location']
        company_id = self.company_id.id
        if not company_id:
            company_id = self.env.user.company_id.id
        wh_ids = self.warehouse_ids
        if not wh_ids:
            wh_ids = self.find_warehouses(company_id)
        locations_list = self.location_id.ids
        if not locations_list:
            locations_ids = location_obj.search(
                [('id', 'child_of', wh_ids.mapped('view_location_id').ids),
                 ('usage', '=', 'internal')])
        else:
            # Get child location of selected location
            locations_ids = location_obj.search([('id', 'child_of', locations_list)])

        end_date = self.end_date.strftime("%Y-%m-%d 23:59:59")
        e_date = datetime.strptime(str(end_date), '%Y-%m-%d %H:%M:%S')
        e_date = e_date.replace(tzinfo=pytz.timezone(
            self.env.user.tz or 'UTC')).astimezone(pytz.timezone('UTC'))
        sml_ids = self.env['stock.move.line'].search(
            [('product_id', '=', product_id), ('state', '=', 'done'),
             ('date', '<=', e_date), ('prod_type', '=', 'product')])
        if sml_ids:
            for location_id in locations_ids:
                ending_qty = 0.0
                # Incoming stock move line
                inc_sml_ids = sml_ids.filtered(
                    lambda sml: sml.location_dest_id.id == location_id.id)
                if inc_sml_ids:
                    ending_qty += sum(inc_sml_ids.mapped('qty_done'))

                # Outgoing stock move line
                out_sml_ids = sml_ids.filtered(lambda sml: sml.location_id.id == location_id.id)
                if out_sml_ids:
                    ending_qty -= sum(out_sml_ids.mapped('qty_done'))

                if ending_qty != 0.0 and location_id.display_name not in locations_names:
                    locations_names.append(location_id.display_name)
        location_name_str = ', '.join([location_name for location_name in locations_names])
        return location_name_str

    def _get_lot(self, product_id):
        """
        Check tracking on product
        :param product_id: integer product id
        :return: string: Yes/no
        """
        product_id = self.env['product.product'].browse(product_id)
        if product_id.tracking == 'none':
            return 'No'
        else:
            return 'Yes'

    def _get_reserved_qty(self, product_id, locations_ids):
        """
        Get Reserve Quantity between From Date and To Date (Both Date included)
        Quantity Calculated Based On selected Location and Warehouse. If not selected, Calculating for all locations
        locations_ids : Contain List of effective locations
        Reserve Quantity =  Manufacturing Order Reserve Qty
        :param product_id: Integer Product Id
        :param locations_ids: Integer Location ids list
        :return: total_reserved_qty: Float Reserve Quantity
        """
        start_date = self.start_date.strftime("%Y-%m-%d %H:%M:%S")
        end_date = self.end_date.strftime("%Y-%m-%d 23:59:59")
        e_date = datetime.strptime(str(end_date), '%Y-%m-%d %H:%M:%S')
        e_date = e_date.replace(tzinfo=pytz.timezone(
            self.env.user.tz or 'UTC')).astimezone(pytz.timezone('UTC'))
        stock_move_rec = self.env['stock.move.line'].search([
            ('product_id', '=', product_id), ('product_uom_qty', '>', 0),
            ('date', '<=', e_date), '|', ('location_id', 'in', locations_ids),
            ('location_id', '=', 548),
            ('prod_type', '=', 'product'),
            ('state', 'not in', ['draft', 'done', 'cancel']), ('production_id', '!=', False),
            ('production_id.state', 'not in', ['draft', 'done', 'cancel']),
            ('move_id.raw_material_production_id', '!=', False)])
        sm_ids = stock_move_rec.mapped('move_id')
        total_reserved_qty = sum(sm_ids.mapped('reserved_availability'))
        return total_reserved_qty or 0.0

    def _get_unit_of_measure(self, product_id):
        uom = ''
        move_rec = self.env['stock.move.line'].search([('product_id', '=', product_id)])
        for move in move_rec:
            uom = move.move_id.product_uom.name
        return uom

    def _get_accounting_cost(self, product_id):
        accounting_cost = 0
        product_rec = self.env['product.product'].search([('id', '=', product_id)])
        for product in product_rec:
            accounting_cost = product.standard_price
        return round(accounting_cost, 3) or 0.0

    @api.model
    def _value_existed(
            self, beginning_inventory, product_qty_in, product_qty_out, product_qty_internal,
            product_qty_adjustment, subcontracting_qty, get_po_not_recieved_qty):
        value_existed = False
        if beginning_inventory or product_qty_in or product_qty_out or product_qty_internal or \
                product_qty_adjustment or subcontracting_qty or get_po_not_recieved_qty:
            value_existed = True
        return value_existed

    def _get_beginning_value(self, product_id_int, beginning_inventory_qty):
        """
        Get Inventory Value at Start Date
        :param product_id_int: Integer Product id
        :param beginning_inventory_qty: Inventory Quantity at Start Date
        :return: Float Value: Value of Inventory at Start Date
        """
        product_id = self.env['product.product'].browse(product_id_int)
        cost_value = product_id.standard_price * beginning_inventory_qty
        return round(cost_value, 3) or 0.0

    def _get_ending_value(self, product_id_int, inventory_ending_qty):
        """
        Get Inventory Value at Ending Date
        :param product_id_int: Integer Product id
        :param inventory_ending_qty: Inventory Quantity at Ending date
        :return: Float Value: Value of Inventory at Ending Date
        """
        product_id = self.env['product.product'].browse(product_id_int)
        cost_value = product_id.standard_price * inventory_ending_qty
        return round(cost_value, 3) or 0.0

    def _get_receive_qty(self, product_id, incoming_qty, locations_ids):
        """
        Update Received Quantity based on from date and to date (both date included)
        Received Quantity = Calculated Incoming Quantity - Return Purchase order
        :param product_id: integer Product Id
        :param incoming_qty: Calculated Incoming Quantity
        :param locations_ids: list of location ids
        :return: incoming_qty: Updated Incoming Quantity
        """
        start_date = self.start_date.strftime("%Y-%m-%d %H:%M:%S")
        end_date = self.end_date.strftime("%Y-%m-%d 23:59:59")
        s_date = datetime.strptime(str(start_date), '%Y-%m-%d %H:%M:%S')
        s_date = s_date.replace(tzinfo=pytz.timezone(
            self.env.user.tz or 'UTC')).astimezone(pytz.timezone('UTC'))
        e_date = datetime.strptime(str(end_date), '%Y-%m-%d %H:%M:%S')
        e_date = e_date.replace(tzinfo=pytz.timezone(
            self.env.user.tz or 'UTC')).astimezone(pytz.timezone('UTC'))

        stock_move_ids = self.env['stock.move.line'].search(
            [('product_id', '=', product_id), ('state', '=', 'done'),
             ('move_id.purchase_line_id', '!=', False),
             ('move_id.picking_type_id.code', '=', 'outgoing'),
             ('location_id', 'in', locations_ids), ('date', '>=', s_date),
             ('date', '<=', e_date), ('prod_type', '=', 'product')])
        if stock_move_ids:
            incoming_qty -= sum(stock_move_ids.mapped('qty_done'))
        return incoming_qty

    def _get_sale_qty(self, product_id, locations_ids):
        """
        Get Sale Quantity of product between From Date and To Date(Both Date Included)
        locations_ids : Contain List of effective locations
        :param product_id:Integer Id of Product
        :param locations_ids: list of location ids
        :return: sale_qty:Float Quantity Value
        """
        sale_qty = 0.0
        start_date = self.start_date.strftime("%Y-%m-%d %H:%M:%S")
        end_date = self.end_date.strftime("%Y-%m-%d 23:59:59")
        s_date = datetime.strptime(str(start_date), '%Y-%m-%d %H:%M:%S')
        s_date = s_date.replace(tzinfo=pytz.timezone(
            self.env.user.tz or 'UTC')).astimezone(pytz.timezone('UTC'))
        e_date = datetime.strptime(str(end_date), '%Y-%m-%d %H:%M:%S')
        e_date = e_date.replace(tzinfo=pytz.timezone(
            self.env.user.tz or 'UTC')).astimezone(pytz.timezone('UTC'))
        stock_move_line_ids = self.env['stock.move.line'].search(
            [('product_id', '=', product_id), ('move_id.sale_line_id', '!=', False),
             ('state', '=', 'done'), ('date', '>=', s_date), ('date', '<=', e_date),
             ('prod_type', '=', 'product')])

        if stock_move_line_ids:
            stock_move_ids = stock_move_line_ids
            sm_ids_outgoing = stock_move_ids.filtered(
                lambda sm: sm.move_id.picking_type_id.code == 'outgoing' and
                           sm.location_id.id in locations_ids)
            if sm_ids_outgoing:
                sale_qty = -(sum(sm_ids_outgoing.mapped('qty_done')))
            sm_ids_incoming = stock_move_ids.filtered(
                lambda sm: sm.move_id.picking_type_id.code == 'incoming' and
                           sm.location_dest_id.id in locations_ids)
            if sm_ids_incoming:
                sale_qty += sum(sm_ids_incoming.mapped('qty_done'))
        return sale_qty

    def _get_consumed_mo_qty(self, product_id, locations_ids):
        """
        Get Consumed Quantity of raw material(product) in Manufacturing Order between From Date and
        To Date(Both Date Included)
        Real Consumed Quantity = Consumed Quantity - Unbuild Order Quantity(Reverse Quantity)
        locations_ids : Contain List of effective locations
        :param product_id:Integer Id of Product
        :param locations_ids: list of location ids
        :return: cosu_qty:Float Quantity Value
        """
        cosu_qty = 0.0
        start_date = self.start_date.strftime("%Y-%m-%d %H:%M:%S")
        end_date = self.end_date.strftime("%Y-%m-%d 23:59:59")
        s_date = datetime.strptime(str(start_date), '%Y-%m-%d %H:%M:%S')
        s_date = s_date.replace(tzinfo=pytz.timezone(
            self.env.user.tz or 'UTC')).astimezone(pytz.timezone('UTC'))
        e_date = datetime.strptime(str(end_date), '%Y-%m-%d %H:%M:%S')
        e_date = e_date.replace(tzinfo=pytz.timezone(
            self.env.user.tz or 'UTC')).astimezone(pytz.timezone('UTC'))
        stock_move_line_ids = self.env['stock.move.line'].search(
            [('product_id', '=', product_id), ('state', '=', 'done'), ('date', '>=', s_date),
             ('date', '<=', e_date), ('prod_type', '=', 'product')])
        if stock_move_line_ids:
            stock_move_ids = stock_move_line_ids
            cosu_qty = -(sum(stock_move_ids.filtered(
                lambda
                    sm: sm.move_id.raw_material_production_id and not sm.move_id.scrapped_return and not
                sm.move_id.scrapped and sm.location_id.id in locations_ids).mapped('qty_done')))
            unbuild_sm_ids = stock_move_ids.filtered(
                lambda sm: sm.move_id.unbuild_id and sm.location_dest_id.id in locations_ids)
            if unbuild_sm_ids:
                cosu_qty += sum(unbuild_sm_ids.mapped('qty_done'))
        return cosu_qty

    def _get_produced_qty(self, product_id, locations_ids):
        """
        Get Produced Quantity of Product from Manufacturing Order between From Date and To Date(Both Date Included)
        Real Produced Quantity = Produced Quantity of Product from Manufacturing Order - Unbuild Order Quantity(Reverse
        Quantity)
        locations_ids : Contain List of effective locations
        :param product_id:Integer Id of Product
        :param locations_ids: list of location ids
        :return: produced_qty:Float Quantity Value
        """
        produced_qty = 0.0
        start_date = self.start_date.strftime("%Y-%m-%d %H:%M:%S")
        end_date = self.end_date.strftime("%Y-%m-%d 23:59:59")
        s_date = datetime.strptime(str(start_date), '%Y-%m-%d %H:%M:%S')
        s_date = s_date.replace(tzinfo=pytz.timezone(
            self.env.user.tz or 'UTC')).astimezone(pytz.timezone('UTC'))
        e_date = datetime.strptime(str(end_date), '%Y-%m-%d %H:%M:%S')
        e_date = e_date.replace(tzinfo=pytz.timezone(
            self.env.user.tz or 'UTC')).astimezone(pytz.timezone('UTC'))
        stock_move_line_ids = self.env['stock.move.line'].search(
            [('product_id', '=', product_id), ('state', '=', 'done'), ('date', '>=', s_date),
             ('date', '<=', e_date), ('move_id.scrapped', '!=', True),
             ('move_id.scrapped_return', '!=', True), ('prod_type', '=', 'product')])
        if stock_move_line_ids:
            stock_move_ids = stock_move_line_ids
            produced_qty = sum(
                stock_move_ids.filtered(
                    lambda sm: sm.move_id.production_id and
                               sm.location_dest_id.id in locations_ids).mapped('qty_done'))
            unbuild_sm_ids = stock_move_ids.filtered(
                lambda sm: sm.move_id.unbuild_id and
                           sm.location_id.id in locations_ids)
            if unbuild_sm_ids:
                produced_qty -= sum(unbuild_sm_ids.mapped('qty_done'))
        return produced_qty

    def _get_subcontracting_qty(self, product_id, locations_ids):
        """
        Get Subcontracting Qty of product between From Date and To Date(Both Date Included)
        Subcontracting Qty = Received From Purchase (+)
        or
        Subcontracting Qty = Outgoing Transfer From Manufacturing Order(-)
        locations_ids : Contain List of effective locations
        :param product_id: Integer Id of Product
        :param locations_ids: list of location ids
        :return: subcontracting_qty: Float Quantity Value
        """
        subcontracting_qty = 0.0
        start_date = self.start_date.strftime("%Y-%m-%d %H:%M:%S")
        end_date = self.end_date.strftime("%Y-%m-%d 23:59:59")
        s_date = datetime.strptime(str(start_date), '%Y-%m-%d %H:%M:%S')
        s_date = s_date.replace(tzinfo=pytz.timezone(
            self.env.user.tz or 'UTC')).astimezone(pytz.timezone('UTC'))
        e_date = datetime.strptime(str(end_date), '%Y-%m-%d %H:%M:%S')
        e_date = e_date.replace(tzinfo=pytz.timezone(
            self.env.user.tz or 'UTC')).astimezone(pytz.timezone('UTC'))
        stock_move_line_ids = self.env['stock.move.line'].search(
            [('product_id', '=', product_id), ('state', '=', 'done'),
             '|', '&', ('location_id', 'in', locations_ids),
             ('location_dest_id', 'not in', locations_ids),
             '&', ('location_id', 'not in', locations_ids),
             ('location_dest_id', 'in', locations_ids), ('move_id.group_id', '!=', False),
             ('move_id.picking_type_id', '!=', False), ('date', '>=', s_date),
             ('date', '<=', e_date), ('prod_type', '=', 'product')])
        if stock_move_line_ids:
            stock_move_ids = stock_move_line_ids.mapped('move_id')
            incoming_sm_ids = stock_move_ids.filtered(
                lambda sm: (sm.is_subcontract or not sm.purchase_line_id) and
                           sm.picking_type_id.code == 'incoming')
            if incoming_sm_ids:
                subcontracting_qty += sum(incoming_sm_ids.mapped('product_qty'))
            procurement_group_ids = self.env['stock.move'].search(
                [('product_id', '=', product_id),
                 ('raw_material_production_id', '!=', False)]).mapped(
                'raw_material_production_id').mapped('procurement_group_id').ids
            outgoing_sm_ids = stock_move_ids.filtered(
                lambda sm: sm.group_id.id in procurement_group_ids and
                           sm.picking_type_id.code == 'outgoing')
            if outgoing_sm_ids:
                subcontracting_qty -= sum(outgoing_sm_ids.mapped('product_qty'))
        return subcontracting_qty

    def _get_adjustment_qty(self, product_id, locations_ids):
        """
        Get Adjustment Quantity of product in between From Date and To Date (Both Date Included)
        Quantity Calculated based on selected Location and Warehouse if not selected then taking all
        Adjustment Quantity = -|+(Inventory Adjustment Quantity) + Internal Transfer - Return Internal Transfer
        locations_ids : Contain List of effective locations
        :param product_id:Integer Id of Product
        :param locations_ids: list of location ids
        :return: adjustment_qty: Float Adjustment Quantity
        """
        adjustment_qty = 0.0
        start_date = self.start_date.strftime("%Y-%m-%d %H:%M:%S")
        end_date = self.end_date.strftime("%Y-%m-%d 23:59:59")
        s_date = datetime.strptime(str(start_date), '%Y-%m-%d %H:%M:%S')
        s_date = s_date.replace(tzinfo=pytz.timezone(
            self.env.user.tz or 'UTC')).astimezone(pytz.timezone('UTC'))
        e_date = datetime.strptime(str(end_date), '%Y-%m-%d %H:%M:%S')
        e_date = e_date.replace(tzinfo=pytz.timezone(
            self.env.user.tz or 'UTC')).astimezone(pytz.timezone('UTC'))
        domain = [('product_id', '=', product_id), ('prod_type', '=', 'product'),
                  ('state', '=', 'done'), ('date', '>=', s_date), ('date', '<=', e_date),
                  '|', '&', ('location_id', 'in', locations_ids),
                  ('location_dest_id', 'not in', locations_ids),
                  '&', ('location_id', 'not in', locations_ids),
                  ('location_dest_id', 'in', locations_ids),
                  '|', '|', '&', ('move_id.picking_type_id', '!=', False),
                  ('move_id.picking_type_id.code', '=', 'internal'),
                  '&', ('move_id.picking_type_id', '=', False),
                  ('move_id.inventory_id', '!=', False),
                  '&', ('move_id.inventory_id', '=', False), ('move_id.qty_adjust', '=', True)]
        stock_move_line_ids = self.env['stock.move.line'].search(domain)
        if stock_move_line_ids:
            stock_move_ids = stock_move_line_ids
            incoming_sm_ids = stock_move_ids.filtered(
                lambda sm: sm.location_dest_id.id in locations_ids)
            if incoming_sm_ids:
                adjustment_qty += sum(incoming_sm_ids.mapped('qty_done'))
            outgoing_sm_ids = stock_move_ids.filtered(lambda sm: sm.location_id.id in locations_ids)
            if outgoing_sm_ids:
                adjustment_qty -= sum(outgoing_sm_ids.mapped('qty_done'))
        return adjustment_qty

    def _get_product_scrapped_qty(self, product_id, locations_ids):
        """
        Get Product Scrapped Quantity in between From Date and To Date (Both Date Included)
        Quantity calculated based on selected location and Warehouse if not selected then taking all
        locations_ids : Contain List of effective locations
        :param product_id:Integer Id of Product
        :param locations_ids: list of location ids
        :return: scrap_qty: Float Scrapped Quantity
        """
        scrap_qty = 0.0
        start_date = self.start_date.strftime("%Y-%m-%d %H:%M:%S")
        end_date = self.end_date.strftime("%Y-%m-%d 23:59:59")
        s_date = datetime.strptime(str(start_date), '%Y-%m-%d %H:%M:%S')
        s_date = s_date.replace(tzinfo=pytz.timezone(
            self.env.user.tz or 'UTC')).astimezone(pytz.timezone('UTC'))
        e_date = datetime.strptime(str(end_date), '%Y-%m-%d %H:%M:%S')
        e_date = e_date.replace(tzinfo=pytz.timezone(
            self.env.user.tz or 'UTC')).astimezone(pytz.timezone('UTC'))
        stock_move_line_ids = self.env['stock.move.line'].search([
            ('product_id', '=', product_id), ('state', '=', 'done'),
            '|', '&', ('move_id.scrapped', '=', True), ('location_id', 'in', locations_ids),
            '&', ('move_id.scrapped_return', '=', True), ('location_dest_id', 'in', locations_ids),
            ('date', '>=', s_date), ('date', '<=', e_date), ('prod_type', '=', 'product')])
        if stock_move_line_ids:
            stock_move_ids = stock_move_line_ids
            outgoing_sm_ids = stock_move_ids.filtered(
                lambda sm: sm.move_id.scrapped and sm.location_id.id in locations_ids)
            if outgoing_sm_ids:
                scrap_qty -= sum(outgoing_sm_ids.mapped('qty_done'))
            incoming_sm_ids = stock_move_ids.filtered(
                lambda sm: sm.move_id.scrapped_return and sm.location_dest_id.id in locations_ids)
            if incoming_sm_ids:
                scrap_qty += sum(incoming_sm_ids.mapped('qty_done'))
        return scrap_qty

    def _get_product_line(self, product_id):
        """
        Get Product Line data from Product
        :param product_id: Integer Product Id
        :return: product_line: String
        """
        product_id = self.env['product.product'].browse(product_id)
        if product_id and product_id.tag_ids:
            if len(product_id.tag_ids) == 1:
                product_line = product_id.tag_ids.name
            else:
                product_line = 'Multiple'
        else:
            product_line = ''
        return product_line

    def print_xls_report(self):
        """
            Print ledger report
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        tmp = tempfile.NamedTemporaryFile(prefix="xlsx", delete=False)
        file_path = tmp.name
        workbook = xlwt.Workbook()

        M_header_tstyle = xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=400, color='grey')
        header_tstyle_c = xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=180, color='grey')
        other_tstyle_c = xls_format.font_style(
            position='center', fontos='black', font_height=180, color='grey')
        other_tstyle_cr = xls_format.font_style(
            position='center', fontos='purple_ega', bold=1, font_height=180, color='grey')
        other_tstyle_r = xls_format.font_style(
            position='right', fontos='purple_ega', bold=1, font_height=180, color='grey')
        other_tstyle_r.num_format_str = '0.000'
        other_tstyle_grandc = xls_format.font_style(
            position='center', fontos='purple_ega', bold=1, border=1, font_height=180, color='grey')
        other_tstyle_grandr = xls_format.font_style(
            position='right', fontos='purple_ega', bold=1, border=1, font_height=180, color='grey')
        other_tstyle_grandr.num_format_str = '0.000'
        datas = {
            'form':
                {'company_id': self.company_id and [self.company_id.id] or [],
                 'warehouse_ids': [y.id for y in self.warehouse_ids],
                 'location_id': self.location_id and self.location_id.ids or False,
                 'start_date': self.start_date.isoformat(),
                 'end_date': self.end_date.isoformat(),
                 'id': self.id,
                 'filter_product_ids': [p.id for p in self.filter_product_ids],
                 'filter_product_categ_ids': [p.id for p in self.filter_product_categ_ids]}}
        company_ids = self._to_company(
            self.company_id and [self.company_id.id] or [])
        company_obj = self.env['res.company']
        summary = 'Summary Report' or 'Detail Report'
        for company in company_ids:
            c_rec = company_obj.sudo().browse(company)
            Hedaer_Text = '%s' % (str(c_rec.name))
            sheet = workbook.add_sheet(Hedaer_Text)
            sheet.set_panes_frozen(True)
            sheet.set_horz_split_pos(9)
            sheet.row(0).height = 256 * 3
            sheet.write_merge(0, 0, 0, 20, Hedaer_Text, M_header_tstyle)
            total_lines = self._get_lines(datas, company)
            warehouses = self.xls_get_warehouses([y.id for y in self.warehouse_ids], company)
            sheet_start_header = 3
            sheet_start_value = 4
            sheet.write_merge(sheet_start_header, sheet_start_header, 0, 2, 'Date', header_tstyle_c)
            sheet.write_merge(
                sheet_start_value, sheet_start_value, 0, 2,
                self.start_date.isoformat() + ' To ' + self.end_date.isoformat(), other_tstyle_cr)
            sheet.write_merge(sheet_start_header, sheet_start_header, 3, 5, 'Company',
                              header_tstyle_c)
            sheet.write_merge(sheet_start_value, sheet_start_value, 3, 5, c_rec.name,
                              other_tstyle_c)
            sheet.write_merge(sheet_start_header, sheet_start_header, 6, 12, 'Warehouse(s)',
                              header_tstyle_c)
            sheet.write_merge(sheet_start_value, sheet_start_value, 6, 12, warehouses,
                              other_tstyle_c)
            sheet.write_merge(sheet_start_header, sheet_start_header, 13, 15, 'Currency',
                              header_tstyle_c)
            sheet.write_merge(sheet_start_value, sheet_start_value, 13, 15, c_rec.currency_id.name,
                              other_tstyle_c)
            sheet.write_merge(sheet_start_header, sheet_start_header, 16, 20, 'Display',
                              header_tstyle_c)
            sheet.write_merge(sheet_start_value, sheet_start_value, 16, 20, summary, other_tstyle_c)
            header_row_start = 8
            sheet.row(8).height = 256 * 2
            sheet.write(header_row_start, 0, 'Category Name ', header_tstyle_c)
            sheet.col(0).width = 256 * 20
            sheet.write(header_row_start, 1, 'Product SKU ', header_tstyle_c)
            sheet.col(1).width = 256 * 40
            sheet.write(header_row_start, 2, 'Product Name ', header_tstyle_c)
            sheet.col(2).width = 256 * 40
            sheet.write(header_row_start, 3, 'Product Line', header_tstyle_c)
            sheet.col(3).width = 256 * 20
            sheet.write(header_row_start, 4, 'Location at Ending ', header_tstyle_c)
            sheet.col(4).width = 256 * 20
            sheet.write(header_row_start, 5, 'Lot/Serial Number ', header_tstyle_c)
            sheet.col(5).width = 256 * 20
            sheet.write(header_row_start, 6, 'Beginning', header_tstyle_c)
            sheet.col(6).width = 256 * 20
            sheet.write(header_row_start, 7, 'Purchased', header_tstyle_c)
            sheet.col(7).width = 256 * 20
            sheet.write(header_row_start, 8, 'PO Not Received', header_tstyle_c)
            sheet.col(20).width = 256 * 20
            sheet.write(header_row_start, 9, 'Sold', header_tstyle_c)
            sheet.col(8).width = 256 * 20
            sheet.write(header_row_start, 10, 'Consumed in Mo', header_tstyle_c)
            sheet.col(9).width = 256 * 20
            sheet.write(header_row_start, 11, 'Created from MO', header_tstyle_c)
            sheet.col(10).width = 256 * 20
            sheet.write(header_row_start, 12, 'Subcontracting Qty', header_tstyle_c)
            sheet.col(11).width = 256 * 20
            sheet.write(header_row_start, 13, 'Adjustments', header_tstyle_c)
            sheet.col(12).width = 256 * 20
            sheet.write(header_row_start, 14, 'Scrapped', header_tstyle_c)
            sheet.col(13).width = 256 * 20
            sheet.write(header_row_start, 15, 'Inventory Qty Ending Date', header_tstyle_c)
            sheet.col(14).width = 256 * 20
            sheet.write(header_row_start, 16, 'MO Reserved Qty', header_tstyle_c)
            sheet.col(15).width = 256 * 20
            sheet.write(header_row_start, 17, 'Unit of Measures', header_tstyle_c)
            sheet.col(16).width = 256 * 20
            sheet.write(header_row_start, 18, 'Accounting Cost', header_tstyle_c)
            sheet.col(17).width = 256 * 20
            sheet.write(header_row_start, 19, 'Value of Inventory at Beginning Date',
                        header_tstyle_c)
            sheet.col(18).width = 256 * 20
            sheet.write(header_row_start, 20, 'Value of Inventory at Ending Date', header_tstyle_c)
            sheet.col(19).width = 256 * 20
            row = 9
            grand_total_qty_in, grand_total_qty_out = 0.0, 0.0
            grand_total_qty_internal, grand_total_product_qty_adjustment = 0.0, 0.0
            grand_total_beginning_inventory, grand_total_ending_inventory = 0.0, 0.0
            grand_total_subtotal_cost = 0.0
            grand_total_inventory_value, grand_total_beginning_value = 0.0, 0.0,
            grand_total_ending_value, grand_total_production_qty = 0.0, 0.0
            grand_total_reserved_qty = 0.0
            sale_qty, total_sale_qty = 0.0, 0.0
            consumed_qty, produced_qty, total_consumed_qty, total_produced_qty = 0.0, 0.0, 0.0, 0.0
            subcontracting_qty, total_subcontracting_qty = 0.0, 0.0
            product_scrapped_qty, total_product_scrapped_qty = 0.0, 0.0

            # Get Effective Location ids List
            location_ids = self._get_location_ids()
            grand_total_po_not_recieved_qty = 0.0

            for values in total_lines.values():
                for line in values:
                    qty_in = line.get('product_qty_in', 0.0) or 0.0
                    product_qty_in = self._get_receive_qty(
                        line.get('product_id'), qty_in, location_ids)
                    product_qty_out = line.get('product_qty_out', 0.0) or 0.0
                    product_qty_internal = line.get('product_qty_internal', 0.0) or 0.0
                    product_qty_adjustment = self._get_adjustment_qty(
                        line.get('product_id'), location_ids)
                    beginning_inventory = self._get_beginning_inventory(
                        datas, company, line.get('product_id', '') or '', line)

                    # Get Subcontracting Qty and Total
                    subcontracting_qty = self._get_subcontracting_qty(
                        line.get('product_id'), location_ids)
                    total_subcontracting_qty += subcontracting_qty

                    ## Get PO Not Recieved Qty.
                    get_po_not_recieved_qty = self._po_not_received_qty(
                        line.get('product_id', '') or '')
                    grand_total_po_not_recieved_qty += get_po_not_recieved_qty

                    if self._value_existed(
                            beginning_inventory, product_qty_in, product_qty_out,
                            product_qty_internal, product_qty_adjustment, subcontracting_qty,
                            get_po_not_recieved_qty):
                        convert = self.end_date.isoformat()
                        product_name, product_barcode, product_code = \
                            self._product_detail(line.get('product_id', '') or '')
                        get_location = self._get_location(line.get('product_id'))
                        get_lot = self._get_lot(line.get('product_id'))
                        reserved_qty = self._get_reserved_qty(line.get('product_id'), location_ids)
                        get_unit_of_measure = self._get_unit_of_measure(
                            line.get('product_id', '') or '')
                        get_accounting_cost = self._get_accounting_cost(
                            line.get('product_id', '') or '')
                        get_beginning_value = self._get_beginning_value(
                            line.get('product_id'), beginning_inventory)
                        grand_total_reserved_qty += reserved_qty
                        grand_total_beginning_value += get_beginning_value
                        grand_total_beginning_inventory += beginning_inventory
                        grand_total_qty_in += product_qty_in
                        grand_total_qty_out += product_qty_out
                        grand_total_qty_internal += product_qty_internal
                        grand_total_product_qty_adjustment += product_qty_adjustment
                        # Get Sale Quantity/ Out Going Quantity and Total
                        sale_qty = self._get_sale_qty(line.get('product_id'), location_ids)
                        total_sale_qty += sale_qty
                        # Get Consumed Quantity in Manufacturing and Total
                        consumed_qty = self._get_consumed_mo_qty(
                            line.get('product_id'), location_ids)
                        total_consumed_qty += consumed_qty

                        # Get Manufactured(Produced) Quantity and Total
                        produced_qty = self._get_produced_qty(line.get('product_id'), location_ids)
                        total_produced_qty += produced_qty

                        # Get Scrap Quantity and Total
                        product_scrapped_qty = self._get_product_scrapped_qty(
                            line.get('product_id'), location_ids)
                        total_product_scrapped_qty += product_scrapped_qty

                        # Get Inventory Qty Ending Date and Total
                        ending_inventory_qty = beginning_inventory + product_qty_in + sale_qty + \
                                               consumed_qty + produced_qty + product_qty_adjustment \
                                               + product_scrapped_qty + subcontracting_qty
                        inventory_value = round(ending_inventory_qty, 3)
                        grand_total_inventory_value += inventory_value

                        # Get Value of Inventory at Ending Date and Total
                        get_ending_value = self._get_ending_value(
                            line.get('product_id'), inventory_value)
                        grand_total_ending_value += get_ending_value

                        # Get Product Line
                        product_line = self._get_product_line(line.get('product_id'))
                        sheet.write(row, 0, self._get_categ(line.get('categ_id', '') or ''),
                                    other_tstyle_c)
                        sheet.write(row, 1, product_code or '', other_tstyle_c)
                        sheet.write(row, 2, product_name or '', other_tstyle_c)
                        sheet.write(row, 3, product_line or '', other_tstyle_c)
                        sheet.write(row, 4, get_location or '', other_tstyle_c)
                        sheet.write(row, 5, get_lot or '', other_tstyle_c)
                        sheet.write(row, 6, round(beginning_inventory, 3), other_tstyle_r)
                        sheet.write(row, 7, round(product_qty_in, 3), other_tstyle_r)
                        sheet.write(row, 8, round(get_po_not_recieved_qty, 3), other_tstyle_r)
                        sheet.write(row, 9, round(sale_qty, 3), other_tstyle_r)
                        sheet.write(row, 10, round(consumed_qty, 3), other_tstyle_r)
                        sheet.write(row, 11, round(produced_qty, 3), other_tstyle_r)
                        sheet.write(row, 12, round(subcontracting_qty, 3), other_tstyle_r)
                        sheet.write(row, 13, round(product_qty_adjustment, 3), other_tstyle_r)
                        sheet.write(row, 14, round(product_scrapped_qty, 3), other_tstyle_r)
                        sheet.write(row, 15, round(inventory_value, 3), other_tstyle_r)
                        sheet.write(row, 16, round(reserved_qty, 3), other_tstyle_r)
                        sheet.write(row, 17, get_unit_of_measure or '', other_tstyle_r)
                        sheet.write(row, 18, get_accounting_cost, other_tstyle_r)
                        sheet.write(row, 19, round(get_beginning_value, 3), other_tstyle_r)
                        sheet.write(row, 20, round(get_ending_value, 3), other_tstyle_r)
                        row += 1

            sheet.write(row, 5, "Grand Total", other_tstyle_grandc)
            sheet.write(row, 6, round(grand_total_beginning_inventory, 3), other_tstyle_grandr)
            sheet.write(row, 7, round(grand_total_qty_in, 3), other_tstyle_grandr)
            sheet.write(row, 8, round(grand_total_po_not_recieved_qty, 3), other_tstyle_grandr)
            sheet.write(row, 9, round(total_sale_qty, 3), other_tstyle_grandr)
            sheet.write(row, 10, round(total_consumed_qty, 3), other_tstyle_grandr)
            sheet.write(row, 11, round(total_produced_qty, 3), other_tstyle_grandr)
            sheet.write(row, 12, round(total_subcontracting_qty, 3), other_tstyle_grandr)
            sheet.write(row, 13, round(grand_total_product_qty_adjustment, 3), other_tstyle_grandr)
            sheet.write(row, 14, round(total_product_scrapped_qty, 3), other_tstyle_grandr)
            sheet.write(row, 15, round(grand_total_inventory_value, 3), other_tstyle_grandr)
            sheet.write(row, 16, round(grand_total_reserved_qty, 3), other_tstyle_grandr)
            sheet.write(row, 17, "-", other_tstyle_grandr)
            sheet.write(row, 18, "-", other_tstyle_grandr)
            sheet.write(row, 19, round(grand_total_beginning_value, 3), other_tstyle_grandr)
            sheet.write(row, 20, round(grand_total_ending_value, 3), other_tstyle_grandr)

        workbook.save(file_path + ".xlsx")
        buffer_data = base64.encodestring(open(file_path + '.xlsx', 'rb').read())
        if buffer_data:
            self.write({'report_data': buffer_data})
        filename = 'Inventory Valuation Report.xls'
        return {
            'name': 'Inventory Valuation Report',
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=stock.valuation.ondate.report&id=" + str(
                self.id) + "&filename_field=filename&field=report_data&download=true&filename=" + filename,
            'target': 'self',
        }
