# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from datetime import datetime
from itertools import groupby
from operator import itemgetter

import pytz

from odoo import models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class StockValuationCategory(models.AbstractModel):
    _name = 'report.activity_report_stock.stock_valuation_ondate_report'
    _description = 'Valuation Report'

    def _get_beginning_inventory(self, data, company_id, product_id, current_record):
        """
        Process:
            -Pass locations , start date and product_id
        Return:
            - Beginning inventory of product for exact date
        """
        location_obj = self.env['stock.location']
        wh_ids = self.warehouse_ids
        if not wh_ids:
            wh_ids = self.find_warehouses(company_id)
        locations_list = self.location_id.ids
        if not locations_list:
            locations_ids = location_obj.search(
                [('id', 'child_of', wh_ids.mapped('view_location_id').ids),
                 ('usage', '=', 'internal')]).ids
        else:
            locations_ids = location_obj.search([('id', 'child_of', locations_list)]).ids

        f_date = data['form'] and data['form']['start_date'] + ' 00:00:00'
        begining_qty = 0.0
        s_date = datetime.strptime(str(f_date), '%Y-%m-%d %H:%M:%S')
        s_date = s_date.replace(tzinfo=pytz.timezone(
            self.env.user.tz or 'UTC')).astimezone(pytz.timezone('UTC'))
        sml_ids = self.env['stock.move.line'].search([('product_id', '=', product_id),
                                                      ('state', '=', 'done'),
                                                      ('date', '<', s_date),
                                                      ('prod_type', '=', 'product')])

        if sml_ids and locations_ids:
            # Incoming stock move line
            inc_sml_ids = sml_ids.filtered(lambda sml: sml.location_dest_id.id in locations_ids)
            if inc_sml_ids:
                begining_qty += sum(inc_sml_ids.mapped('qty_done'))

            # Outgoing stock move line
            out_sml_ids = sml_ids.filtered(lambda sml: sml.location_id.id in locations_ids)
            if out_sml_ids:
                begining_qty -= sum(out_sml_ids.mapped('qty_done'))
        self.begining_qty = begining_qty
        current_record.update({'begining_qty': begining_qty})
        return round(self.begining_qty, 3) or 0.0

    def category_wise_value(self, start_date, end_date, locations, filter_product_categ_ids=[]):
        """
        Complete data with category wise
            - In Qty (Inward Quantity to given location)
            - Out Qty(Outward Quantity to given location)
            - Internal Qty(Internal Movements(or null movements) to given location: out/in both : out must be - ,In must be + )
            - Adjustment Qty(Inventory Loss movements to given location: out/in both: out must be - ,In must be + )
        Return:
            [{},{},{}...]
        """
        self._cr.execute('''SELECT pp.id AS product_id,pt.categ_id,
                            sum((
                            CASE WHEN spt.code in ('outgoing') AND sm.location_id in %s AND 
                            sourcel.usage !='inventory' AND destl.usage !='inventory' AND sm.prod_type = 'product'
                            THEN -(sm.product_qty * pu.factor / pu2.factor) 
                            ELSE 0.0 
                            END
                            )) AS product_qty_out,
                            
                            sum((
                            CASE WHEN spt.code in ('incoming') AND sm.location_dest_id in %s AND 
                            sourcel.usage !='inventory' AND destl.usage !='inventory' AND sm.sale_line_id is null AND 
                            (sm.is_subcontract is Null or sm.is_subcontract = 'f') AND sm.prod_type = 'product' AND
                            sm.purchase_line_id is not Null
                            THEN (sm.product_qty * pu.factor / pu2.factor) 
                            ELSE 0.0 
                            END
                            )) AS product_qty_in,
                            
                            sum((
                            CASE WHEN (spt.code ='internal' OR spt.code is null) AND 
                            (sm.production_id is not null OR sm.raw_material_production_id is not null) AND
                            sm.location_dest_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' 
                            AND sm.prod_type = 'product'
                            THEN (sm.product_qty * pu.factor / pu2.factor)  
                            WHEN (spt.code ='internal' OR spt.code is null) AND 
                            (sm.production_id is not null OR sm.raw_material_production_id is not null) AND
                            sm.location_id in %s AND sourcel.usage !='inventory' AND 
                            destl.usage !='inventory' AND sm.prod_type = 'product'
                            THEN -(sm.product_qty * pu.factor / pu2.factor) 
                            ELSE 0.0 
                            END
                            )) AS product_qty_internal,
                        
                            sum((
                            CASE WHEN sourcel.usage = 'inventory' AND sm.location_dest_id in %s 
                            AND sm.prod_type = 'product'
                            THEN  (sm.product_qty * pu.factor / pu2.factor)
                            WHEN destl.usage ='inventory' AND sm.location_id in %s AND sm.prod_type = 'product'
                            THEN -(sm.product_qty * pu.factor / pu2.factor)
                            ELSE 0.0 
                            END
                            )) AS product_qty_adjustment
                        
                        FROM product_product pp 
                        LEFT JOIN  stock_move sm ON (sm.product_id = pp.id and sm.date >= %s and 
                        sm.date <= %s and sm.state = 'done' and sm.location_id != sm.location_dest_id)
                        LEFT JOIN stock_picking sp ON (sm.picking_id=sp.id)
                        LEFT JOIN stock_picking_type spt ON (spt.id=sp.picking_type_id)
                        LEFT JOIN stock_location sourcel ON (sm.location_id=sourcel.id)
                        LEFT JOIN stock_location destl ON (sm.location_dest_id=destl.id)
                        LEFT JOIN uom_uom pu ON (sm.product_uom=pu.id)
                        LEFT JOIN uom_uom pu2 ON (sm.product_uom=pu2.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        WHERE pt.active = true and pp.active = true
                        GROUP BY pt.categ_id, pp.id order by pt.categ_id

                        ''',
                         (tuple(locations), tuple(locations), tuple(locations), tuple(locations),
                          tuple(locations), tuple(locations), start_date, end_date))

        values = self._cr.dictfetchall()

        for none_to_update in values:
            if not none_to_update.get('product_qty_out'):
                none_to_update.update({'product_qty_out': 0.0})
            if not none_to_update.get('product_qty_in'):
                none_to_update.update({'product_qty_in': 0.0})

        # filter by categories
        if filter_product_categ_ids:
            values = self._remove_product_cate_ids(values, filter_product_categ_ids)
        else:
            all_filter_product_categ_ids = self.env['product.category'].search(
                [('type', '=', 'product')])
            values = self._remove_product_cate_ids(values, all_filter_product_categ_ids.ids)
        return values

    def _remove_zero_inventory(self, values):
        final_values = []
        for rm_zero in values:
            if rm_zero['product_qty_in'] == 0.0 and rm_zero['product_qty_internal'] == 0.0 \
                    and rm_zero['product_qty_out'] == 0.0 and \
                    rm_zero['product_qty_adjustment'] == 0.0:
                pass
            else:
                final_values.append(rm_zero)
        return final_values

    def _remove_product_cate_ids(self, values, filter_product_categ_ids):
        final_values = []
        for rm_products in values:
            if rm_products['categ_id'] not in filter_product_categ_ids:
                pass
            else:
                final_values.append(rm_products)
        return final_values

    def _get_categ(self, categ):
        """
        Find category name with id
        """
        return self.env['product.category'].browse(categ).read(['name'])[0]['name']

    def find_warehouses(self, company_id):
        """
        Find all warehouses
        """
        return [x.id for x in self.env['stock.warehouse'].search([('company_id', '=', company_id)])]

    def _find_locations(self, warehouses):
        """
            Find all warehouses stock locations and its childs.
        """
        warehouse_obj = self.env['stock.warehouse']
        location_obj = self.env['stock.location']
        stock_ids = []
        for warehouse in warehouses:
            stock_ids.append(warehouse_obj.sudo().browse(warehouse.id).view_location_id.id)
        return [l.id for l in location_obj.search([('location_id', 'child_of', stock_ids)])]

    def convert_withtimezone(self, userdate):
        """
            Convert to Time-Zone with compare to UTC
        """
        user_date = datetime.strptime(userdate, DEFAULT_SERVER_DATETIME_FORMAT)
        tz_name = self.env.context.get('tz') or self.env.user.tz
        if tz_name:
            utc = pytz.timezone('UTC')
            context_tz = pytz.timezone(tz_name)
            user_datetime = user_date  # + relativedelta(hours=24.0)
            local_timestamp = context_tz.localize(user_datetime, is_dst=False)
            user_datetime = local_timestamp.astimezone(utc)
            return user_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return user_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def _get_lines(self, data, company):
        """
        Process:
            Pass start date, end date, locations to get data from moves,
            Merge those data with locations,
        Return:
            {category : [{},{},{}...], category : [{},{},{}...],...}
        """
        date_start = data['form']['start_date']
        date_end = data['form']['end_date']
        if type(date_start) != type(''):
            start = date_start.isoformat()
            end = date_end.isoformat()
            start_date = self.convert_withtimezone(start + ' 00:00:00')
            end_date = self.convert_withtimezone(end + ' 23:59:59')
        else:
            start_date = self.convert_withtimezone(data['form']['start_date'] + ' 00:00:00')
            end_date = self.convert_withtimezone(data['form']['end_date'] + ' 23:59:59')
        location_obj = self.env['stock.location']
        wh_ids_list = data['form'] and data['form'].get('warehouse_ids', []) or []
        wh_ids = self.env['stock.warehouse'].browse(wh_ids_list)
        if not wh_ids:
            wh_ids = self.find_warehouses(company)
        locations_list = data['form'] and data['form'].get('location_id') or False
        if not locations_list:
            locations_ids = location_obj.search(
                [('id', 'child_of', wh_ids.mapped('view_location_id').ids),
                 ('usage', '=', 'internal')]).ids
        else:
            locations_ids = location_obj.search([('id', 'child_of', locations_list)]).ids
        filter_product_categ_ids = data['form'] and data['form'].get(
            'filter_product_categ_ids') or []
        records = self.category_wise_value(start_date, end_date, locations_ids,
                                           filter_product_categ_ids)
        sort_by_categories = sorted(records, key=itemgetter('categ_id'))
        records_by_categories = dict(
            (k, [v for v in itr]) for k, itr in groupby(sort_by_categories, itemgetter('categ_id')))
        self.value_exist = records_by_categories
        return records_by_categories
