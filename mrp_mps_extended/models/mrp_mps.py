from collections import defaultdict
from math import log10
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.tools.date_utils import add, subtract
from odoo.tools.float_utils import float_round
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools.misc import split_every
from odoo.osv.expression import OR, AND

PRODUCTS = []
LEVEL_SET = []
HAS_DOMAIN = []


class MrpProductionSchedule(models.Model):
    _inherit = 'mrp.production.schedule'

    def get_impacted_schedule(self, domain=False):
        """
        Author : Raumil Dhandhukia (Setu Consulting Services Private Ltd.)
        Purpose : Reflect quantities on products components while searching and editing both will take place.
        Date : 2nd Nov 2021
        """
        if domain:
            HAS_DOMAIN.append(True)
            return super(MrpProductionSchedule, self.with_context(
                from_mps_custom_search_view=True, from_impacted_schedule_method=True)).get_impacted_schedule(domain)
        HAS_DOMAIN.append(False)
        return super(MrpProductionSchedule, self).get_impacted_schedule([])

    # def set_order_of_products(self, parents, base_parents, seq=1):
    #     """
    #     Author : Raumil Dhandhukia (Setu Consulting Services Private Ltd.)
    #     Purpose : Set sequence in which products and their components will be shown in MPS view.
    #     Date : 1st Nov 2021
    #     """
    #     for p in parents:
    #         p.mps_tmp_seq = seq
    #         seq += 1
    #         bom = self.env['mrp.bom'].search(
    #             ['|', ('product_id', '=', p.id), ('product_tmpl_id', '=', p.product_tmpl_id.id)])
    #         if bom:
    #             children = bom.bom_line_ids.mapped('product_id')
    #             children -= base_parents
    #             seq = self.set_order_of_products(children, base_parents, seq)
    #     return seq
    def set_order_of_products(self, parents, base_parents, seq=1):
        """
        Author : Raumil Dhandhukia (Setu Consulting Services Private Ltd.)
        Purpose : Set sequence in which products and their components will be shown in MPS view.
        Date : 1st Nov 2021
        """
        for p in parents:
            p.mps_tmp_seq = seq
            seq += 1
        templates = parents.mapped('product_tmpl_id')
        templates = templates.ids if templates else []
        bom = self.env['mrp.bom'].search(
            ['|', ('product_id', '=', parents.ids), ('product_tmpl_id', 'in', templates)])
        if bom:
            children = bom.bom_line_ids.mapped('product_id')
            if children:
                children_which_are_in_mps = self.env['mrp.production.schedule'].search(
                    [('product_id', 'in', children.ids)]).mapped('product_id')
                children = children_which_are_in_mps
                children -= base_parents
                seq = self.set_order_of_products(children, base_parents, seq)
        return seq

    def level_builder(self, level, sub_level):
        """
        Author : Raumil Dhandhukia (Setu Consulting Services Private Ltd.)
        Purpose : Returns next level.
        Date : 1st Nov 2021
        """
        adder = ''
        level_list = list(level.split("."))
        level_list.pop()
        level_list = [x + '.' for x in level_list]
        level = adder.join(level_list) + f'{sub_level}'
        return level

    # def set_level_of_products(self, parents, base_parents, level='1', create_new_level=False):
    #     """
    #     Author : Raumil Dhandhukia (Setu Consulting Services Private Ltd.)
    #     Purpose : Set level in products and their components.
    #     Date : 1st Nov 2021
    #     """
    #     if parents == base_parents:
    #         parents.mps_tmp_level = level
    #         for p in parents:
    #             bom_id = self.env['mrp.bom'].search(
    #                 ['|', ('product_id', '=', p.id), ('product_tmpl_id', '=', p.product_tmpl_id.id)])
    #             if bom_id:
    #                 children = bom_id.bom_line_ids.mapped('product_id')
    #                 mps_ids = self.env['mrp.production.schedule'].search([('product_id', 'in', children.ids)])
    #                 if mps_ids:
    #                     children = mps_ids.mapped('product_id')
    #                 children -= parents
    #                 ids = list(children.ids)
    #                 ids.sort(key=lambda ch: self.env['product.product'].browse(ch).mps_tmp_seq)
    #                 children = self.env['product.product'].browse(ids)
    #                 self.set_level_of_products(children, base_parents, level, True)
    #     else:
    #         sub_level = 1
    #         if create_new_level:
    #             level = str(level) + f'.{sub_level}'
    #             create_new_level = False
    #         else:
    #             level = self.level_builder(level, sub_level)
    #         for p in parents:
    #             if p.id in PRODUCTS:
    #                 p.mps_tmp_level = ' - MX'
    #             else:
    #                 p.mps_tmp_level = level
    #             PRODUCTS.append(p.id)
    #             bom_id = self.env['mrp.bom'].search(
    #                 ['|', ('product_id', '=', p.id), ('product_tmpl_id', '=', p.product_tmpl_id.id)])
    #             if bom_id:
    #                 children = bom_id.bom_line_ids.mapped('product_id')
    #                 mps_ids = self.env['mrp.production.schedule'].search([('product_id', 'in', children.ids)])
    #                 if mps_ids:
    #                     children = mps_ids.mapped('product_id')
    #                 # children -= parents
    #                 ids = list(children.ids)
    #                 ids.sort(key=lambda ch: self.env['product.product'].browse(ch).mps_tmp_seq)
    #                 children = self.env['product.product'].browse(ids)
    #                 self.set_level_of_products(children, base_parents, level, True)
    #             sub_level += 1
    #             level = self.level_builder(level, sub_level)

    def set_level_of_products(self, parents, base_parents, level=0):
        if not LEVEL_SET:
            LEVEL_SET.append(self.env['product.product'])
        # parents = base_parents
        for l in parents:
            if l in LEVEL_SET[0] and l not in base_parents:
                l.mps_tmp_level = 'MP'
        parents -= LEVEL_SET[0]
        if parents != base_parents:
            parents -= base_parents
        parents.mps_tmp_level = level
        level += 1
        LEVEL_SET[0] = LEVEL_SET[0] | parents

        bom_ids = self.env['mrp.bom'].search(
            ['|', ('product_id', 'in', parents.ids), ('product_tmpl_id', 'in', parents.product_tmpl_id.ids)])
        if bom_ids:
            for bom in bom_ids:
                # base_parents = parents

                children = bom.bom_line_ids.mapped('product_id')
                if children:
                    children_which_are_in_mps = self.env['mrp.production.schedule'].search(
                        [('product_id', 'in', children.ids)]).mapped('product_id')
                    children = children_which_are_in_mps

                    self.set_level_of_products(children, base_parents, level)

    @api.model
    def get_mps_view_state(self, domain=False):
        """
        Author : Raumil Dhandhukia (Setu Consulting Services Private Ltd.)
        Purpose : To set sequence and levelize the products and their components.
        Date : 1st Nov 2021
        """
        tag_text = ""
        domain_dict = {}
        if domain:

            domain_tmp = domain
            try:
                while True:
                    domain_tmp.remove('&')
            except ValueError:
                pass
            try:
                while True:
                    domain_tmp.remove('|')
            except ValueError:
                pass
            domain_dict = {x[0]: x[2] for x in domain_tmp}
            if 'product_id' in domain_dict:
                res = super(MrpProductionSchedule,
                            self.with_context(from_mps_custom_search_view=True,
                                              has_domain_in_search=True)).get_mps_view_state(
                    domain=domain)
                if res and 'production_schedule_ids' in res.keys():
                    data = res['production_schedule_ids']
                    mps_ids = self.with_context(from_mps_custom_search_view=False).search(domain)
                    parents = mps_ids.mapped('product_id')
                    self.set_order_of_products(parents, parents)
                    self.set_level_of_products(parents, parents, False)
                    LEVEL_SET.clear()
                    PRODUCTS.clear()

                    data.sort(key=lambda x: self.env['product.product'].browse(x['product_id'][0]).mps_tmp_seq)
                    for i in range(len(data)):
                        mps = data[i]
                        if self.env['product.product'].browse(mps['product_id'][0]).mps_tmp_level and self.env[
                            'product.product'].browse(mps['product_id'][0]).mps_tmp_level != '0':
                            product_id = self.env['product.product'].sudo().search([('id', '=', mps['product_id'][0])])
                            product_name = product_id.display_name
                            if self.env['product.product'].browse(mps['product_id'][0]).mps_tmp_level == 'MP':
                                product_name_string = str(
                                    self.env['product.product'].browse(mps['product_id'][0]).mps_tmp_level) + ' - ' + \
                                                      product_name
                            else:
                                product_name_string = 'L' + str(
                                    self.env['product.product'].browse(mps['product_id'][0]).mps_tmp_level) + ' - ' + \
                                                      product_name
                            mps['product_id'] = (mps['product_id'][0], product_name_string)
                    res['production_schedule_ids'] = data
            else:
                res = super(MrpProductionSchedule,
                            self.with_context(from_mps_custom_search_view=True,
                                              has_domain_in_search=True)).get_mps_view_state(domain=domain)
        else:
            res = super(MrpProductionSchedule, self.with_context(from_mps_custom_search_view=True,
                                                                 has_domain_in_search=False)).get_mps_view_state(
                domain=domain)
        mps_recs = res['production_schedule_ids']

        for i in range(len(mps_recs)):
            mps = mps_recs[i]
            if 'product_uom_id' in mps:
                del mps['product_uom_id']
            if 'warehouse_id' in mps:
                del mps['warehouse_id']
            if 'product_id' in mps and len(mps['product_id']) == 2:
                product_id = self.env['product.product'].sudo().search([('id', '=', mps['product_id'][0])])
                tags = product_id.tag_ids
                tag_text = " - " + ", ".join(tags.mapped('name')) if tags else ""
                categ_text = (product_id.categ_id and product_id.categ_id.category_emoji_id and " - " + product_id.categ_id.category_emoji_id.logo) or (product_id.categ_id and " - " + product_id.categ_id.name) or ""
                type_text = ' - ' + dict(self.env['product.template']._fields['type'].selection).get(product_id.type)
                product_name = mps['product_id'][1] if len(mps['product_id'][1]) <= 40 else mps['product_id'][1][
                                                                                            0:37] + '...'
                mps['product_id'] = (
                    mps['product_id'][0],
                    product_name + tag_text + categ_text + type_text)
            # if 'product_id' in mps and len(mps['product_id']) == 2 and len(mps['product_id'][1]) > 40:
            #     mps['product_id'] = (mps['product_id'][0], mps['product_id'][1][0:37] + '...')
            if domain_dict:
                if 'product_to_replenish' in domain_dict:
                    if domain_dict['product_to_replenish']:
                        if not any(set(x['replenish_qty'] for x in mps['forecast_ids'])):
                            mps_recs[i] = {}
                    else:
                        if any(set(x['replenish_qty'] for x in mps['forecast_ids'])):
                            mps_recs[i] = {}
        try:
            while True:
                res['production_schedule_ids'].remove({})
        except ValueError:
            pass
        if res['production_schedule_ids']:
            date_type = False
            if self.env.context.get('lang', False):
                date_type = self.env['res.lang'].search([('code', '=', self.env.context.get('lang'))],
                                                        limit=1).date_format
            if date_type:
                week_start_dates = [',' + str(x['date_start'].strftime(date_type)) for x in
                                    res['production_schedule_ids'][0]['forecast_ids']]
            else:
                week_start_dates = [',' + str(x['date_start']) for x in
                                    res['production_schedule_ids'][0]['forecast_ids']]
            for i in range(len(res['dates'])):
                res['dates'][i] = res['dates'][i] + week_start_dates[i]

        return res

    @api.model
    def _default_warehouse_id(self):
        mps_warehouse_ids = self.env['stock.warehouse'].search(
            [('use_in_mps', '=', True), ('company_id', '=', self.env.company.id)], limit=1)
        if not mps_warehouse_ids:
            raise ValidationError(_("No Warehouse selected, Please select a Warehouse in Inventory configuration!"))
        return mps_warehouse_ids

    # Override this field because of need to add domain
    warehouse_id = fields.Many2one('stock.warehouse', 'Production Warehouse', domain=[('use_in_mps', '=', True)],
                                   required=True,
                                   default=lambda self: self._default_warehouse_id())
    categ_id = fields.Many2one('product.category', related='product_id.categ_id')
    product_type = fields.Selection([('consu', 'Consumable'),
                                     ('product', 'Storable Product'),
                                     ('service', 'Service')], compute='_compute_product_type', store=True)

    purchase_ok = fields.Boolean(compute='_compute_purchase_ok', store=True)

    tag_ids = fields.Many2many(comodel_name='product.template.tag',
                               relation="mrp_tag_rel",
                               column1="mrp_id",
                               column2="tag_id", compute='_compute_tag_ids', store=True)
    parent_id = fields.Many2one('mrp.production.schedule')
    product_to_replenish = fields.Boolean(default=True)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """
        Author : Raumil Dhandhukia (Setu Consulting Services Private Ltd.)
        Purpose : Search method inherited for customized use.
        Date : 1st Nov 2021
        """

        if self.env.context.get('from_impacted_schedule_method', False):
            args = args[2:]
        for dom in args:
            if dom[0] == 'product_to_replenish' and not dom[2]:
                dom[2] = True
        res = super(MrpProductionSchedule, self).search(args=args, offset=offset, limit=limit, order=order, count=count)
        domain = args
        try:
            while True:
                domain.remove('&')
        except ValueError:
            pass
        try:
            while True:
                domain.remove('|')
        except ValueError:
            pass
        domain_dict = {}
        if domain:
            domain_dict = {x[0]: x[2] for x in domain}
        # if res and args and self.env.context.get('from_mps_custom_search_view', False) and args[0] and args[0][
        #     0] == 'product_id' and len(args) == 1:
        if res and domain_dict and self.env.context.get('from_mps_custom_search_view',
                                                        False) and 'product_id' in domain_dict:
            domain_extender = domain_dict.copy()
            del domain_extender['product_id']
            products = res.mapped('product_id')
            expanded_products = self.get_expanded_products(products)
            if expanded_products:
                # domain = [[x, '=', y] for x, y in domain_extender.items()]
                domain = [('product_id', 'in', expanded_products.ids)]
                res = super(MrpProductionSchedule, self).search(args=domain,
                                                                offset=offset, limit=limit, order=order, count=count)
        return res

    def get_expanded_products(self, products):
        """
        Author : Raumil Dhandhukia (Setu Consulting Services Private Ltd.)
        Purpose : Will get all components from product's BoM.
        Date : 1st Nov 2021
        """
        components = self.env['product.product']
        product_bom = self.env['mrp.bom'].search(
            ['|', ('product_tmpl_id', 'in', products.product_tmpl_id.ids), ('product_id', 'in', products.ids)])
        if product_bom:
            components = product_bom.bom_line_ids.mapped('product_id')
            components -= products
        if components:
            return products | self.get_expanded_products(components)
        return products

    @api.depends('product_id', 'product_id.tag_ids')
    def _compute_tag_ids(self):
        """
        Author : Raumil Dhandhukia (Setu Consulting Services Private Ltd.)
        Purpose : Get tag_ids.
        Date : 1st Nov 2021
        """
        for rec in self:
            rec.tag_ids = rec.product_id and rec.product_id.tag_ids or False

    @api.depends('product_id', 'product_id.product_tmpl_id', 'product_id.product_tmpl_id.purchase_ok')
    def _compute_purchase_ok(self):
        """
        Author : Raumil Dhandhukia (Setu Consulting Services Private Ltd.)
        Purpose : Get purchase ok.
        Date : 1st Nov 2021
        """
        for rec in self:
            rec.purchase_ok = rec.product_id and rec.product_tmpl_id and rec.product_tmpl_id.purchase_ok or False

    @api.depends('product_id', 'product_id.type')
    def _compute_product_type(self):
        """
        Author : Raumil Dhandhukia (Setu Consulting Services Private Ltd.)
        Purpose : Get product type.
        Date : 1st Nov 2021
        """
        for rec in self:
            rec.product_type = rec.product_id and rec.product_id.type or False

    def _get_procurement_extra_values(self, forecast_values):
        res = super(MrpProductionSchedule, self)._get_procurement_extra_values(forecast_values)
        res.update({
            'is_replanished_from_mps': True
        })
        return res

    # def action_replenish(self, based_on_lead_time=False):
    # """
    # Override By : Sagar Sakaria | Emipro Technologies Pvt. Ltd
    # Date : 26th March, 2020
    # Override method for the changes in order qty if demanded qty < product.minimum than order qty is minimum qty,
    # and set the multiple in product than consider the next multiple number for order qty
    # Cancel and unlink the MO and PO which have a created from MPS and in draft or confim state

    # :param based_on_lead_time:
    # :return:
    # """
    # """ Run the procurement for production schedule in self. Once the
    # procurements are launched, mark the forecast as launched (only used
    # for state 'to_relaunch')

    # :param based_on_lead_time: 2 replenishment options exists in MPS.
    # based_on_lead_time means that the procurement for self will be launched
    # based on lead times.
    # e.g. period are daily and the product have a manufacturing period
    # of 5 days, then it will try to run the procurements for the 5 first
    # period of the schedule.
    # If based_on_lead_time is False then it will run the procurement for the
    # first period that need a replenishment
    # """

    # forecast_ids = self.env['mrp.product.forecast'].search([('x_studio_forecast_automatic', '=', True)])
    # prepare_vals = []
    # for record in forecast_ids:
    # week_num = datetime.strftime(record.date, "%W")

    # sales = self.env['sale.order.line'].search(
    # [('product_id', '=', record.x_studio_part_number), ('x_studio_status', '=', 'sale'),
    # ('x_studio_week_number', '=', week_num)])
    # cons_sales = self.env['stock.move'].search([('picking_type_id', '=', 92), (
    # 'product_id', '=', record.x_studio_part_number), ('state', '!=', 'draft'),
    # ('state', '!=', 'cancel'),
    # ('x_studio_week_number', '=', week_num)])
    # total_qty = sum([qty.product_uom_qty for qty in sales])

    # total_cons_qty = sum([qty.product_uom_qty for qty in cons_sales])
    # total_sales = total_qty + total_cons_qty
    # forecast = record.x_studio_forecast
    # prepare_vals.append((record.id, total_sales, total_qty, total_cons_qty, forecast if forecast >= total_sales else total_sales))

    # if prepare_vals:
    # self._cr.execute("""UPDATE mrp_product_forecast as t
    # set x_studio_total_sales = c.x_studio_total_sales,
    # x_studio_sales = c.x_studio_sales,
    # x_studio_consignment_sales = c.x_studio_consignment_sales,
    # forecast_qty = c.forecast_qty
    # from
    # (values
    # {}) as c(column_id, x_studio_total_sales, x_studio_sales, x_studio_consignment_sales, forecast_qty)
    # where c.column_id = t.id
    # """.format(str(prepare_vals).strip('[]')))
    # self._cr.commit()

    # production_ids = self.env['mrp.production'].search(
    # [('state', 'in', ['draft', 'confirmed']), ('origin', '=', 'MPS'),
    # ('product_tmpl_id', 'in', self.product_id.product_tmpl_id.ids)])
    # if production_ids:
    # for production_id in split_every(100, production_ids.ids):
    # production = self.env['mrp.production'].browse(production_id)
    # production.action_cancel()
    # production.unlink()
    # purchase_ids = self.env['purchase.order'].search([('state', 'in', ['draft', 'sent']), ('origin', '=', 'MPS'),
    # ('order_line.product_id', 'in', self.product_id.ids)])
    # if purchase_ids:
    # for purchase_id in split_every(100, purchase_ids.ids):
    # purchase = self.env['purchase.order'].browse(purchase_id)
    # purchase.button_cancel()
    # purchase.unlink()
    # return super(MrpProductionSchedule, self).action_replenish(based_on_lead_time)

    def _get_incoming_qty(self, date_range):
        """ Get the incoming quantity from RFQ and existing moves.

        param: list of time slots used in order to group incoming quantity.
        return: a dict with as key a production schedule and as values a list
        of incoming quantity for each date range.
        """
        incoming_qty = defaultdict(float)
        incoming_qty_done = defaultdict(float)
        after_date = date_range[0][0]
        before_date = date_range[-1][1]
        # Get quantity in RFQ
        rfq_domain = self._get_rfq_domain(after_date, before_date)
        rfq_lines = self.env['purchase.order.line'].search(rfq_domain, order='date_planned')

        index = 0
        for line in rfq_lines:
            # Skip to the next time range if the planned date is not in the
            # current time interval.
            while not (date_range[index][0] <= line.date_planned.date() and
                       date_range[index][1] >= line.date_planned.date()):
                index += 1
            quantity = line.product_uom._compute_quantity(line.product_qty, line.product_id.uom_id)
            incoming_qty[date_range[index], line.product_id, line.order_id.picking_type_id.warehouse_id] += quantity

        # Get quantity on incoming moves
        # TODO: issue since it will use one search by move. Should use a
        # read_group with a group by location.
        domain_moves_confirmed, domain_moves_done = self._get_moves_domain(after_date, before_date, 'incoming')
        stock_moves_confirmed = self.env['stock.move'].search(domain_moves_confirmed, order='date_expected')
        stock_moves_done = self.env['stock.move'].search(domain_moves_done, order='date')
        index = 0
        past_domain_moves_confirmed, past_domain_moves_done = self._get_moves_domain(after_date.min,
                                                                                after_date - relativedelta(days=1),
                                                                                'incoming')
        if past_domain_moves_confirmed:
            past_stock_moves_confirmed = self.env['stock.move'].search(past_domain_moves_confirmed,
                                                                       order='date_expected')
            for move in past_stock_moves_confirmed.filtered(lambda m: m.purchase_line_id or m.production_id):
                # more_qty = sum(past_stock_moves_confirmed.mapped('product_uom_qty'))
                key = (date_range[index], move.product_id, move.location_dest_id.get_warehouse())
                incoming_qty[key] += move.product_uom_qty
        for move in stock_moves_confirmed:
            # Skip to the next time range if the planned date is not in the
            # current time interval.
            while not (date_range[index][0] <= move.date_expected.date() and
                       date_range[index][1] >= move.date_expected.date()):
                index += 1
            key = (date_range[index], move.product_id, move.location_dest_id.get_warehouse())
            incoming_qty[key] += move.product_qty
            """
            MY CHANGES
            """
            # if index == 0:
            #     past_domain_moves_confirmed, domain_moves_done = self._get_moves_domain(after_date.min, after_date - relativedelta(days=1), 'incoming')
            #     if past_domain_moves_confirmed:
            #         past_stock_moves_confirmed = self.env['stock.move'].search(past_domain_moves_confirmed, order='date_expected')
            #         if past_stock_moves_confirmed:
            #             more_qty = sum(past_stock_moves_confirmed.mapped('product_uom_qty'))
            #             incoming_qty[key] += more_qty
            """
            MY CHANGES
            """

        index = 0
        for move in stock_moves_done:
            # Skip to the next time range if the planned date is not in the
            # current time interval.
            while not (date_range[index][0] <= move.date.date() and
                       date_range[index][1] >= move.date.date()):
                index += 1
            key = (date_range[index], move.product_id, move.location_dest_id.get_warehouse())
            incoming_qty_done[key] += move.product_qty

        return incoming_qty, incoming_qty_done

    def _get_outgoing_qty(self, date_range):
        """ Get the outgoing quantity from existing moves.
        return a dict with as key a production schedule and as values a list
        of outgoing quantity for each date range.
        """
        outgoing_qty = defaultdict(float)
        outgoing_qty_done = defaultdict(float)
        after_date = date_range[0][0]
        before_date = date_range[-1][1]
        # Get quantity on incoming moves

        domain_moves_confirmed, domain_moves_done = self._get_moves_domain(after_date, before_date, 'outgoing')
        domain_moves_confirmed = AND([domain_moves_confirmed, [('raw_material_production_id', '=', False)]])
        domain_moves_done = AND([domain_moves_done, [('raw_material_production_id', '=', False)]])

        stock_moves_confirmed = self.env['stock.move'].search(domain_moves_confirmed, order='date_expected')
        index = 0
        # FROM HERE
        more_qty = False
        past_confirmed, past_done = self._get_moves_domain(after_date.min, after_date - relativedelta(days=1),
                                                           'outgoing')
        past_confirmed = AND([past_confirmed, [('raw_material_production_id', '=', False)]])

        if past_confirmed:
            past_stock_moves_confirmed = self.env['stock.move'].search(past_confirmed, order='date_expected')
            for move in past_stock_moves_confirmed.filtered(lambda m: m.sale_line_id):
                # more_qty = sum(past_stock_moves_confirmed.mapped('product_uom_qty'))
                key = (date_range[index], move.product_id, move.location_id.get_warehouse())
                outgoing_qty[key] += move.product_uom_qty

        # TO HERE

        for move in stock_moves_confirmed:
            # Skip to the next time range if the planned date is not in the
            # current time interval.

            while not (date_range[index][0] <= move.date_expected.date() and
                       date_range[index][1] >= move.date_expected.date()):
                index += 1
            key = (date_range[index], move.product_id, move.location_id.get_warehouse())
            outgoing_qty[key] += move.product_uom_qty
            """
            Changes
            """
            # if index == 0:
            #     past_confirmed, past_done = self._get_moves_domain(after_date.min, after_date- relativedelta(days=1), 'outgoing')
            #     past_confirmed = AND([past_confirmed, [('raw_material_production_id', '=', False)]])
            #
            #     if past_confirmed:
            #         past_stock_moves_confirmed = self.env['stock.move'].search(past_confirmed, order='date_expected')
            #         if past_stock_moves_confirmed:
            #             more_qty = sum(past_stock_moves_confirmed.mapped('product_uom_qty'))
            #             outgoing_qty[key] += more_qty

            """
            Changes
            """

        stock_moves_done = self.env['stock.move'].search(domain_moves_done, order='date')
        index = 0
        for move in stock_moves_done:
            # Skip to the next time range if the planned date is not in the
            # current time interval.
            while not (date_range[index][0] <= move.date.date() and
                       date_range[index][1] >= move.date.date()):
                index += 1
            key = (date_range[index], move.product_id, move.location_id.get_warehouse())
            outgoing_qty_done[key] += move.product_uom_qty

        return outgoing_qty, outgoing_qty_done

    def get_production_schedule_view_state(self):
        """
        Use: Override this method because of filter the data warehouse wise
        Added by: Jignesh Bharadiya @Emipro Technologies
        Added on: 4/1/20
        """
        """ Prepare and returns the fields used by the MPS client action.
        For each schedule returns the fields on the model. And prepare the cells
        for each period depending the manufacturing period set on the company.
        The forecast cells contains the following information:
        - forecast_qty: Demand forecast set by the user
        - date_start: First day of the current period
        - date_stop: Last day of the current period
        - replenish_qty: The quantity to replenish for the current period. It
        could be computed or set by the user.
        - replenish_qty_updated: The quantity to replenish has been set manually
        by the user.
        - starting_inventory_qty: During the first period, the quantity
        available. After, the safety stock from previous period.
        - incoming_qty: The incoming moves and RFQ for the specified product and
        warehouse during the current period.
        - outgoing_qty: The outgoing moves quantity.
        - indirect_demand_qty: On manufacturing a quantity to replenish could
        require a need for a component in another schedule. e.g. 2 product A in
        order to create 1 product B. If the replenish quantity for product B is
        10, it will need 20 product A.
        - safety_stock_qty:
        starting_inventory_qty - forecast_qty - indirect_demand_qty + replenish_qty
        """
        # jigneshb
        self.flush()
        stock_warehouse_obj = self.env['stock.warehouse']
        stock_location_obj = self.env['stock.location']
        company_id = self.env.company
        date_range = company_id._get_date_range()

        # We need to get the schedule that impact the schedules in self. Since
        # the state is not saved, it needs to recompute the quantity to
        # replenish of finished products. It will modify the indirect
        # demand and replenish_qty of schedules in self.
        schedules_to_compute = self.env['mrp.production.schedule'].browse(self.get_impacted_schedule()) | self

        # Dependencies between schedules
        indirect_demand_trees = schedules_to_compute._get_indirect_demand_tree()
        # Get the schedules that do not depends from other in first position in
        # order to compute the schedule state only once.
        indirect_demand_order = schedules_to_compute._get_indirect_demand_order(indirect_demand_trees)
        indirect_demand_qty = defaultdict(float)
        incoming_qty, incoming_qty_done = self._get_incoming_qty(date_range)
        outgoing_qty, outgoing_qty_done = self._get_outgoing_qty(date_range)
        read_fields = [
            'forecast_target_qty',
            'min_to_replenish_qty',
            'max_to_replenish_qty',
            'product_id',
        ]
        if self.env.user.has_group('stock.group_stock_multi_warehouses'):
            read_fields.append('warehouse_id')
        if self.env.user.has_group('uom.group_uom'):
            read_fields.append('product_uom_id')
        production_schedule_states = schedules_to_compute.read(read_fields)
        production_schedule_states_by_id = {mps['id']: mps for mps in production_schedule_states}
        i = 0
        for production_schedule in indirect_demand_order:
            i += 1
            # Bypass if the schedule is only used in order to compute indirect
            # demand.
            rounding = production_schedule.product_id.uom_id.rounding
            lead_time = production_schedule._get_lead_times()
            production_schedule_state = production_schedule_states_by_id[production_schedule['id']]
            if production_schedule in self:
                procurement_date = add(fields.Date.today(), days=lead_time)
                precision_digits = max(0, int(-(log10(production_schedule.product_uom_id.rounding))))
                production_schedule_state['precision_digits'] = precision_digits
                production_schedule_state['forecast_ids'] = []
            indirect_demand_ratio = schedules_to_compute._get_indirect_demand_ratio_mps(indirect_demand_trees)

            # jigneshb
            mps_warehouse_ids = stock_warehouse_obj.search(
                [('use_in_mps', '=', True), ('company_id', '=', self.env.company.id)])
            if not mps_warehouse_ids:
                raise ValidationError(_("No Warehouse selected, Please select a Warehouse in Inventory configuration!"))
            # changes by sagars
            parent_location = stock_location_obj.search(
                [('id', 'in', mps_warehouse_ids.mapped('view_location_id').ids), ('usage', '=', 'view')])
            mps_location_ids = stock_location_obj.search(
                [('id', 'child_of', parent_location.ids), ('use_in_mps', '=', True)])
            if not mps_location_ids:
                raise ValidationError(_("No Location selected, Please select a Location in Inventory configuration!"))
            starting_inventory_qty = production_schedule.product_id.with_context(
                location=mps_location_ids.ids).qty_available
            # Stop changes sagars
            # if len(date_range):
            #     starting_inventory_qty -= incoming_qty_done.get(
            #         (date_range[0], production_schedule.product_id, production_schedule.warehouse_id), 0.0)
            #     starting_inventory_qty += outgoing_qty_done.get(
            #         (date_range[0], production_schedule.product_id, production_schedule.warehouse_id), 0.0)
            ind = 0
            for date_start, date_stop in date_range:
                forecast_values = {}
                key = ((date_start, date_stop), production_schedule.product_id, production_schedule.warehouse_id)
                existing_forecasts = production_schedule.forecast_ids.filtered(
                    lambda p: p.date >= date_start and p.date <= date_stop)
                if production_schedule in self:
                    forecast_values['date_start'] = date_start
                    forecast_values['date_stop'] = date_stop
                    if ind==0:
                        ind+=1
                        forecast_values['incoming_qty'] = float_round(
                            incoming_qty.get(key, 0.0), precision_rounding=rounding)
                        forecast_values['outgoing_qty'] = float_round(
                            outgoing_qty.get(key, 0.0), precision_rounding=rounding)
                    else:
                        forecast_values['incoming_qty'] = float_round(
                            incoming_qty.get(key, 0.0) + incoming_qty_done.get(key, 0.0), precision_rounding=rounding)
                        forecast_values['outgoing_qty'] = float_round(
                            outgoing_qty.get(key, 0.0) + outgoing_qty_done.get(key, 0.0), precision_rounding=rounding)

                forecast_values['indirect_demand_qty'] = float_round(indirect_demand_qty.get(key, 0.0),
                                                                     precision_rounding=rounding)
                replenish_qty_updated = False
                if existing_forecasts:
                    forecast_values['forecast_qty'] = float_round(sum(existing_forecasts.mapped('forecast_qty')),
                                                                  precision_rounding=rounding)
                    forecast_values['replenish_qty'] = float_round(sum(existing_forecasts.mapped('replenish_qty')),
                                                                   precision_rounding=rounding)

                    # Check if the to replenish quantity has been manually set or
                    # if it needs to be computed.
                    replenish_qty_updated = any(existing_forecasts.mapped('replenish_qty_updated'))
                    forecast_values['replenish_qty_updated'] = replenish_qty_updated
                else:
                    forecast_values['forecast_qty'] = 0.0

                if not replenish_qty_updated:
                    replenish_qty = production_schedule._get_replenish_qty(
                        starting_inventory_qty - forecast_values['forecast_qty'] - forecast_values[
                            'indirect_demand_qty'])
                    forecast_values['replenish_qty'] = float_round(replenish_qty, precision_rounding=rounding)
                    forecast_values['replenish_qty_updated'] = False

                forecast_values['starting_inventory_qty'] = float_round(starting_inventory_qty,
                                                                        precision_rounding=rounding)
                forecast_values['safety_stock_qty'] = float_round(
                    starting_inventory_qty - forecast_values['forecast_qty'] - forecast_values['indirect_demand_qty'] +
                    forecast_values['replenish_qty'], precision_rounding=rounding)

                if production_schedule in self:
                    production_schedule_state['forecast_ids'].append(forecast_values)
                starting_inventory_qty = forecast_values['safety_stock_qty']
                # Set the indirect demand qty for children schedules.
                for (product, ratio) in indirect_demand_ratio[
                    (production_schedule.warehouse_id, production_schedule.product_id)].items():
                    if not forecast_values['replenish_qty']:
                        continue
                    related_date = max(subtract(date_start, days=lead_time), fields.Date.today())
                    index = next(i for i, (dstart, dstop) in enumerate(date_range) if
                                 related_date <= dstart or (related_date >= dstart and related_date <= dstop))
                    related_key = (date_range[index], product, production_schedule.warehouse_id)
                    indirect_demand_qty[related_key] += ratio * forecast_values['replenish_qty']

            if production_schedule in self:
                # The state is computed after all because it needs the final
                # quantity to replenish.
                forecasts_state = production_schedule._get_forecasts_state(production_schedule_states_by_id, date_range,
                                                                           procurement_date)
                forecasts_state = forecasts_state[production_schedule.id]
                for index, forecast_state in enumerate(forecasts_state):
                    production_schedule_state['forecast_ids'][index].update(forecast_state)

                # The purpose is to hide indirect demand row if the schedule do not
                # depends from another.
                has_indirect_demand = any(
                    forecast['indirect_demand_qty'] != 0 for forecast in production_schedule_state['forecast_ids'])
                production_schedule_state['has_indirect_demand'] = has_indirect_demand
        if not self.env.context.get('from_mps_custom_search_view', False):
            production_schedule_states.sort(
                key=lambda x: self.env['product.product'].browse(x['product_id'][0]).mps_tmp_seq)

            if HAS_DOMAIN and HAS_DOMAIN[0]:
                for i in range(len(production_schedule_states)):
                    mps = production_schedule_states[i]
                    if self.env['product.product'].browse(mps['product_id'][0]).mps_tmp_level and self.env[
                        'product.product'].browse(mps['product_id'][0]).mps_tmp_level != '0':
                        product_id = self.env['product.product'].sudo().search([('id', '=', mps['product_id'][0])])
                        product_name = product_id.display_name
                        if self.env['product.product'].browse(mps['product_id'][0]).mps_tmp_level == 'MP':
                            product_name_string = str(
                                self.env['product.product'].browse(mps['product_id'][0]).mps_tmp_level) + ' - ' + \
                                                  product_name
                        else:
                            product_name_string = 'L' + str(
                                self.env['product.product'].browse(mps['product_id'][0]).mps_tmp_level) + ' - ' + \
                                                  product_name
                        mps['product_id'] = (mps['product_id'][0], product_name_string)
                    production_schedule_states[i] = mps

            for i in range(len(production_schedule_states)):
                mps = production_schedule_states[i]
                if 'product_uom_id' in mps:
                    del mps['product_uom_id']
                if 'warehouse_id' in mps:
                    del mps['warehouse_id']
                if 'product_id' in mps and len(mps['product_id']) == 2:
                    product_id = self.env['product.product'].sudo().search([('id', '=', mps['product_id'][0])])
                    tags = product_id.tag_ids
                    tag_text = " - " + ", ".join(tags.mapped('name')) if tags else ""
                    categ_text = (product_id.categ_id and product_id.categ_id.category_emoji_id and " - " + product_id.categ_id.category_emoji_id.logo) or (product_id.categ_id and " - " + product_id.categ_id.name) or ""
                    type_text = ' - ' + dict(self.env['product.template']._fields['type'].selection).get(
                        product_id.type)
                    product_name = mps['product_id'][1] if len(mps['product_id'][1]) <= 40 else mps['product_id'][1][
                                                                                                0:37] + '...'
                    mps['product_id'] = (
                        mps['product_id'][0],
                        product_name + tag_text + categ_text + type_text)
        # if IS_SEARCHED:
        #     IS_SEARCHED.clear()
        HAS_DOMAIN.clear()
        return [p for p in production_schedule_states if p['id'] in self.ids]

    def _get_replenish_qty(self, after_forecast_qty):
        """
        Added By Sagars,
        Added on: 22nd Apr, 2020
        Inherited function
        Purpose: Consider minimum and multiple of product in replenish qty
        :param after_forecast_qty:
        :return: replenish qty
        """
        res = super(MrpProductionSchedule, self)._get_replenish_qty(after_forecast_qty)
        if res > 0:
            qty = max(res, self.product_id.minimum_qty)
            reminder = self.product_id.multiple_qty > 0 and qty % self.product_id.multiple_qty or 0.0
            if reminder > 0:
                qty += self.product_id.multiple_qty - reminder
            res = qty
        return res

    @api.model
    def create(self, vals):
        """
        Author : Udit Ramani (Setu Consulting Services Private Ltd.)
        Purpose : To add product to MPS.
        Date : 29th Oct 2021
        """
        res = super(MrpProductionSchedule, self).create(vals)
        for rec in res:
            rec.product_id.with_context(mps_is_created_from_screen='yes').use_in_mps = True
        return res

    def unlink(self):
        """
        Author : Udit Ramani (Setu Consulting Services Private Ltd.)
        Purpose : Auto Add/Remove product to/from MPS.
        Date : 29th Oct 2021
        """
        if self.env.context.get('do_not_set_use_in_mps_to_false', False):
            return super(MrpProductionSchedule, self).unlink()
        else:
            for rec in self:
                rec.product_id.with_context(mps_is_deleted_from_screen='yes').use_in_mps = False
            return super(MrpProductionSchedule, self).unlink()
