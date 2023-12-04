# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from collections import OrderedDict
from datetime import datetime

from odoo import fields, api, models, _
from odoo.exceptions import AccessError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
        ('lot', 'By Lots'),
        ('none', 'No Tracking')],
        help="""Ensure the traceability of a storable
        product in your warehouse.""", default='none', required=True)
    type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Inventory Product')], string='Product Type', default='product', required=True,
        help=''''A storable product is a product for which you manage stock.
                The Inventory app has to be installed.\n'''
             '''A consumable product is a product for
                 which stock is not managed.\n'''
             '''A service is a non-material product you provide.''')

    # Custom mandatory fields
    is_material = fields.Boolean()
    is_thread_size = fields.Boolean()
    is_cat_length = fields.Boolean()
    is_cat_id = fields.Boolean()
    is_od = fields.Boolean()
    is_dash = fields.Boolean()
    is_wire_diameter = fields.Boolean()
    is_free_length = fields.Boolean()
    is_brand = fields.Boolean()
    is_resistance = fields.Boolean()
    is_size = fields.Boolean()
    is_capacitance = fields.Boolean()
    is_turn_ratio = fields.Boolean()
    is_inductance = fields.Boolean()
    is_cat_type = fields.Boolean()
    is_cat_solder = fields.Boolean()
    is_cat_3dprint = fields.Boolean()
    is_signals = fields.Boolean()
    is_gauge = fields.Boolean()
    is_coating = fields.Boolean()
    is_focal_length = fields.Boolean()
    is_polarization = fields.Boolean()
    is_thickness = fields.Boolean()
    is_width = fields.Boolean()
    is_barcode = fields.Boolean()

    # Custom optional fields
    is_magnetism = fields.Boolean()
    is_compressed_length = fields.Boolean()
    is_press_slip = fields.Boolean()
    is_pins = fields.Boolean()
    is_finish = fields.Boolean()
    is_weight = fields.Boolean()
    is_brand_opt = fields.Boolean()
    is_warranty = fields.Boolean()
    is_pdp_url = fields.Boolean()
    is_mac_address = fields.Boolean()
    is_mac_bluetooth = fields.Boolean()
    is_disk_space = fields.Boolean()
    is_memory = fields.Boolean()
    is_processor = fields.Boolean()
    is_cpu_speed = fields.Boolean()
    is_opt_cat_id = fields.Boolean()
    is_opt_od = fields.Boolean()


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    _sql_constraints = [
        ('sku_uniq', 'unique(default_code)', 'SKU must be unique !')]

    # Custom mandatory fields checkbox
    is_material = fields.Boolean()
    is_thread_size = fields.Boolean()
    is_cat_length = fields.Boolean()
    is_cat_id = fields.Boolean()
    is_od = fields.Boolean()
    is_dash = fields.Boolean()
    is_wire_diameter = fields.Boolean()
    is_free_length = fields.Boolean()
    is_brand = fields.Boolean()
    is_resistance = fields.Boolean()
    is_size = fields.Boolean()
    is_capacitance = fields.Boolean()
    is_turn_ratio = fields.Boolean()
    is_inductance = fields.Boolean()
    is_cat_type = fields.Boolean()
    is_cat_solder = fields.Boolean()
    is_cat_3dprint = fields.Boolean()
    is_signals = fields.Boolean()
    is_gauge = fields.Boolean()
    is_coating = fields.Boolean()
    is_focal_length = fields.Boolean()
    is_polarization = fields.Boolean()
    is_width = fields.Boolean()
    is_thickness = fields.Boolean()
    is_barcode = fields.Boolean()
    # Custom optional fields checkbox
    is_magnetism = fields.Boolean()
    is_compressed_length = fields.Boolean()
    is_press_slip = fields.Boolean()
    is_pins = fields.Boolean()
    is_finish = fields.Boolean()
    is_weight = fields.Boolean()
    is_brand_opt = fields.Boolean()
    is_warranty = fields.Boolean()
    is_pdp_url = fields.Boolean()
    is_mac_address = fields.Boolean()
    is_mac_bluetooth = fields.Boolean()
    is_disk_space = fields.Boolean()
    is_memory = fields.Boolean()
    is_processor = fields.Boolean()
    is_cpu_speed = fields.Boolean()
    is_opt_cat_id = fields.Boolean()
    is_opt_od = fields.Boolean()

    # Custom mandatory fields
    material = fields.Char()
    thread_size = fields.Char()
    cat_length = fields.Char()
    cat_id = fields.Char()
    od = fields.Char()
    dash = fields.Char()
    wire_diameter = fields.Char()
    free_length = fields.Char()
    brand = fields.Char()
    resistance = fields.Char()
    size = fields.Char()
    capacitance = fields.Char()
    turn_ratio = fields.Char()
    inductance = fields.Char()
    cat_type = fields.Selection(selection=[
        ('ic', 'Integrated Circuit'), ('led', 'LED'), ('diode', 'Diode'),
        ('photodiode', 'Photodiode')], help='Semiconductors Type.')
    cat_type_solder = fields.Selection(selection=[
        ('wire', 'Wire'), ('paste', 'Paste')], help='Solder Type')
    cat_3dprint = fields.Selection(selection=[
        ('filament', 'Filament'), ('resin', 'Resin')], help='3D Print')
    signals = fields.Char()
    gauge = fields.Char()
    coating = fields.Char()
    focal_length = fields.Char()
    polarization = fields.Char()
    thickness = fields.Char()
    width = fields.Char()

    # Custom optional fields
    magnetism = fields.Selection(selection=[
        ('none', 'None'), ('low', 'Low'),
        ('high', 'High'), ('unknown', 'Unknown')], help='Select Types.')
    compressed_length = fields.Char()
    press_slip = fields.Selection(selection=[
        ('press', 'Press'), ('slip', 'Slip')], help='Select Press/Slip.')
    pins = fields.Char()
    finish = fields.Char()
    kernel_weight = fields.Char()
    brand_opt = fields.Char()
    warranty = fields.Selection(selection=[
        ('applecare', 'AppleCare+'), ('one', '1 Year'), ('two', '2 Year'),
        ('three', '3 Year'), ('other', 'Other'), ], help='Select Warranty.')
    pdp_url = fields.Char()
    mac_address = fields.Char()
    mac_bluetooth = fields.Char()
    disk_space = fields.Selection(selection=[
        ('ds128', '128GB'), ('ds256', '256GB'), ('ds512', '512GB'),
        ('1tb', '1TB'), ('2tb', '2TB'), ('other', 'Other'), ], help='Select Disk Space.')
    memory = fields.Selection(selection=[
        ('m8', '8GB'), ('m16', '16GB'), ('m32', '32GB'),
        ('m64', '64GB'), ('other', 'Other'), ], help='Select Memory.')
    processor = fields.Selection(selection=[
        ('pi3', 'i3'), ('pi5', 'i5'), ('pi7', 'i7'), ('pi9', 'i9'), ('other', 'Other'), ],
        help='Select Processor.')
    cpu_speed = fields.Char()
    opt_cat_id = fields.Char()
    opt_od = fields.Char()

    type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Inventory Product')], string='Product Type', required=True,
        help='A inventory Product is a product for which you manage stock. '
             'The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock '
             'is not managed.\n'
             'A service is a non-material product you provide.')
    sale_ok = fields.Boolean('Can be Sold', default=False)
    purchase_ok = fields.Boolean('Can be Purchased', default=True)
    putaway_rule_ids = fields.One2many('stock.putaway.rule', 'product_tmpl_id')
    user_archived_id = fields.Many2one('res.users', string="User Archived", copy=False)
    date_archived = fields.Datetime(string="Date Archived", copy=False)

    @api.depends('putaway_rule_ids')
    def _get_location(self):
        for product in self:
            product.location_id = product.putaway_rule_ids and product.putaway_rule_ids[
                0].location_out_id.id or False

    location_id = fields.Many2one('stock.location', string="Location", store=True,
                                  compute='_get_location', compute_sudo=True)

    @api.model
    def default_get(self, field_lst):
        res = super(ProductTemplate, self).default_get(field_lst)
        res.update({'type': False})
        if res.get('categ_id', False):
            res.update({'categ_id': False})
        return res

    def _get_onchange_create(self):
        return OrderedDict([
            ('_onchange_categ_id', [
                'is_material', 'is_thread_size', 'is_cat_length',
                'is_cat_id', 'is_od', 'is_dash', 'is_wire_diameter',
                'is_free_length', 'is_brand', 'is_resistance',
                'is_size', 'is_capacitance', 'is_turn_ratio', 'is_inductance',
                'is_cat_type', 'is_cat_solder', 'is_cat_3dprint', 'is_signals',
                'is_gauge', 'is_coating', 'is_focal_length', 'is_polarization',
                'is_width', 'is_thickness', 'is_barcode', 'is_magnetism',
                'is_compressed_length', 'is_press_slip', 'is_pins',
                'is_finish', 'is_weight', 'is_brand_opt', 'is_warranty',
                'is_pdp_url', 'is_mac_address', 'is_mac_bluetooth',
                'is_disk_space', 'is_memory', 'is_processor',
                'is_cpu_speed', 'is_opt_cat_id', 'is_opt_od'])])

    @api.model
    def create(self, vals):
        onchanges = self._get_onchange_create()
        for onchange_method, changed_fields in onchanges.items():
            if any(f not in vals for f in changed_fields):
                category = self.new(vals)
                getattr(category, onchange_method)()
                for field in changed_fields:
                    if field not in vals and category[field]:
                        vals[field] = category._fields[
                            field].convert_to_write(category[field], category)
        return super(ProductTemplate, self).create(vals)

    @api.onchange('type')
    def _onchange_type(self):
        res = super(ProductTemplate, self)._onchange_type()
        if self.type == 'service':
            msg = """Reminder: The Service category is for anything with time as the unit of purchase.

Examples: Training, Extended Warranty, Consulting Hours.

If you’re unsure, review the “Odoo Product Category Cheat Sheet” in Confluence as needed. Link below.

https://confluence.kernel.corp/pages/viewpage.action?pageId=443619295"""
            warning = {'title': _("Product Category"), 'message': msg, }
            res.update({'warning': warning})
        return res

    @api.onchange('categ_id')
    def _onchange_categ_id(self):
        if self.categ_id:
            self.tracking = self.categ_id.tracking
            self.type = self.categ_id.type
            product_category = self.env['product.category']
            product_category_ids = product_category.search(
                [('id', 'parent_of', self.categ_id.id)])
            if [categ for categ in product_category_ids if categ.is_material]:
                self.is_material = True
                self.material = False
            else:
                if self.material:
                    self.material = False
                self.is_material = False

            if [categ for categ in product_category_ids if categ.is_thread_size]:
                self.is_thread_size = True
                self.thread_size = False
            else:
                if self.thread_size:
                    self.thread_size = False
                self.is_thread_size = False

            if [categ for categ in product_category_ids if categ.is_cat_length]:
                self.is_cat_length = True
                self.cat_length = False
            else:
                if self.cat_length:
                    self.cat_length = False
                self.is_cat_length = False

            if [categ for categ in product_category_ids if categ.is_cat_id]:
                self.is_cat_id = True
                self.cat_id = False
            else:
                if self.cat_id:
                    self.cat_id = False
                self.is_cat_id = False

            if [categ for categ in product_category_ids if categ.is_od]:
                self.is_od = True
                self.od = False
            else:
                if self.od:
                    self.od = False
                self.is_od = False

            if [categ for categ in product_category_ids if categ.is_dash]:
                self.is_dash = True
                self.dash = False
            else:
                if self.dash:
                    self.dash = False
                self.is_dash = False

            if [categ for categ in product_category_ids if categ.is_wire_diameter]:
                self.is_wire_diameter = True
                self.wire_diameter = False
            else:
                if self.wire_diameter:
                    self.wire_diameter = False
                self.is_wire_diameter = False

            if [categ for categ in product_category_ids if categ.is_free_length]:
                self.is_free_length = True
                self.free_length = False
            else:
                if self.free_length:
                    self.free_length = False
                self.is_free_length = False

            if [categ for categ in product_category_ids if categ.is_brand]:
                self.is_brand = True
                self.brand = False
            else:
                if self.brand:
                    self.brand = False
                self.is_brand = False

            if [categ for categ in product_category_ids if categ.is_resistance]:
                self.is_resistance = True
                self.resistance = False
            else:
                if self.resistance:
                    self.resistance = False
                self.is_resistance = False

            if [categ for categ in product_category_ids if categ.is_size]:
                self.is_size = True
                self.size = False
            else:
                if self.size:
                    self.size = False
                self.is_size = False

            if [categ for categ in product_category_ids if categ.is_capacitance]:
                self.is_capacitance = True
                self.capacitance = False
            else:
                if self.capacitance:
                    self.capacitance = False
                self.is_capacitance = False

            if [categ for categ in product_category_ids if categ.is_turn_ratio]:
                self.is_turn_ratio = True
                self.turn_ratio = False
            else:
                if self.turn_ratio:
                    self.turn_ratio = False
                self.is_turn_ratio = False

            if [categ for categ in product_category_ids if categ.is_inductance]:
                self.is_inductance = True
                self.inductance = False
            else:
                if self.inductance:
                    self.inductance = False
                self.is_inductance = False

            if [categ for categ in product_category_ids if categ.is_signals]:
                self.is_signals = True
                self.signals = False
            else:
                if self.signals:
                    self.signals = False
                self.is_signals = False

            if [categ for categ in product_category_ids if categ.is_gauge]:
                self.is_gauge = True
                self.gauge = False
            else:
                if self.gauge:
                    self.gauge = False
                self.is_gauge = False

            if [categ for categ in product_category_ids if categ.is_coating]:
                self.is_coating = True
                self.coating = False
            else:
                if self.coating:
                    self.coating = False
                self.is_coating = False

            if [categ for categ in product_category_ids if categ.is_focal_length]:
                self.is_focal_length = True
                self.focal_length = False
            else:
                if self.focal_length:
                    self.focal_length = False
                self.is_focal_length = False

            if [categ for categ in product_category_ids if categ.is_polarization]:
                self.is_polarization = True
                self.polarization = False
            else:
                if self.polarization:
                    self.polarization = False
                self.is_polarization = False

            if [categ for categ in product_category_ids if categ.is_thickness]:
                self.is_thickness = True
                self.thickness = False
            else:
                if self.thickness:
                    self.thickness = False
                self.is_thickness = False

            if [categ for categ in product_category_ids if categ.is_width]:
                self.is_width = True
                self.width = False
            else:
                if self.width:
                    self.width = False
                self.is_width = False

            if [categ for categ in product_category_ids if categ.is_barcode]:
                self.is_barcode = True
                self.barcode = False
            else:
                if self.barcode:
                    self.barcode = False
                self.is_barcode = False

            if [categ for categ in product_category_ids if categ.is_compressed_length]:
                self.is_compressed_length = True
                self.compressed_length = False
            else:
                if self.compressed_length:
                    self.compressed_length = False
                self.is_compressed_length = False

            if [categ for categ in product_category_ids if categ.is_press_slip]:
                self.is_press_slip = True
                self.press_slip = False
            else:
                if self.press_slip:
                    self.press_slip = False
                self.is_press_slip = False

            if [categ for categ in product_category_ids if categ.is_pins]:
                self.is_pins = True
                self.pins = False
            else:
                if self.pins:
                    self.pins = False
                self.is_pins = False

            if [categ for categ in product_category_ids if categ.is_finish]:
                self.is_finish = True
                self.finish = False
            else:
                if self.finish:
                    self.finish = False
                self.is_finish = False

            if [categ for categ in product_category_ids if categ.is_weight]:
                self.is_weight = True
                self.kernel_weight = False
            else:
                if self.kernel_weight:
                    self.kernel_weight = False
                self.is_weight = False

            if [categ for categ in product_category_ids if categ.is_pdp_url]:
                self.is_pdp_url = True
                self.pdp_url = False
            else:
                if self.pdp_url:
                    self.pdp_url = False
                self.is_pdp_url = False

            if [categ for categ in product_category_ids if categ.is_mac_address]:
                self.is_mac_address = True
                self.mac_address = False
            else:
                if self.mac_address:
                    self.mac_address = False
                self.is_mac_address = False

            if [categ for categ in product_category_ids if categ.is_mac_bluetooth]:
                self.is_mac_bluetooth = True
                self.mac_bluetooth = False
            else:
                if self.mac_bluetooth:
                    self.mac_bluetooth = False
                self.is_mac_bluetooth = False

            if [categ for categ in product_category_ids if categ.is_cpu_speed]:
                self.is_cpu_speed = True
                self.cpu_speed = False
            else:
                if self.cpu_speed:
                    self.cpu_speed = False
                self.is_cpu_speed = False

            if [categ for categ in product_category_ids if categ.is_cat_type]:
                self.is_cat_type = True
                self.cat_type = False
            else:
                if self.cat_type:
                    self.cat_type = False
                self.is_cat_type = False

            if [categ for categ in product_category_ids if categ.is_cat_solder]:
                self.is_cat_solder = True
                self.cat_type_solder = False
            else:
                if self.cat_type_solder:
                    self.cat_type_solder = False
                self.is_cat_solder = False

            if [categ for categ in product_category_ids if categ.is_cat_3dprint]:
                self.is_cat_3dprint = True
                self.cat_3dprint = False
            else:
                if self.cat_3dprint:
                    self.cat_3dprint = False
                self.is_cat_3dprint = False

            if [categ for categ in product_category_ids if categ.is_magnetism]:
                self.is_magnetism = True
                self.magnetism = 'unknown'
            else:
                if self.magnetism:
                    self.magnetism = False
                self.is_magnetism = False

            if [categ for categ in product_category_ids if categ.is_brand_opt]:
                self.is_brand_opt = True
                self.brand_opt = False
            else:
                if self.brand_opt:
                    self.brand_opt = False
                self.is_brand_opt = False

            if [categ for categ in product_category_ids if categ.is_warranty]:
                self.is_warranty = True
                self.warranty = False
            else:
                if self.warranty:
                    self.warranty = False
                self.is_warranty = False

            if [categ for categ in product_category_ids if categ.is_disk_space]:
                self.is_disk_space = True
                self.disk_space = False
            else:
                if self.disk_space:
                    self.disk_space = False
                self.is_disk_space = False

            if [categ for categ in product_category_ids if categ.is_memory]:
                self.is_memory = True
                self.memory = False
            else:
                if self.memory:
                    self.memory = False
                self.is_memory = False

            if [categ for categ in product_category_ids if categ.is_processor]:
                self.is_processor = True
                self.processor = False
            else:
                if self.processor:
                    self.processor = False
                self.is_processor = False

            if [categ for categ in product_category_ids if categ.is_opt_cat_id]:
                self.is_opt_cat_id = True
                self.opt_cat_id = False
            else:
                if self.opt_cat_id:
                    self.opt_cat_id = False
                self.is_opt_cat_id = False

            if [categ for categ in product_category_ids if categ.is_opt_od]:
                self.is_opt_od = True
                self.opt_od = False
            else:
                if self.opt_od:
                    self.opt_od = False
                self.is_opt_od = False

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if 'active' in vals and len(vals) == 1 and 'default_type' not in self._context:
            if not self.env.user.has_group('product_extension.group_product_archive_access'):
                raise AccessError(_("You do not have access to archive or unarchive product."))
            else:
                for rec in self:
                    if vals['active'] is False:
                        rec.message_post(body="Product archived")
                        rec.user_archived_id = self.env.user.id
                        rec.date_archived = fields.Datetime.now()
                    else:
                        rec.message_post(body="Product unarchived")
                        rec.user_archived_id = False
                        rec.date_archived = False
        return res

    def set_quantity_zero(self):
        for rec in self:
            inventory = self.env['stock.inventory'].create({
                'name': 'Set Quantity Zero',
                'product_ids': [(6, 0, rec.product_variant_ids.ids)],
                'accounting_date': datetime.now().date(),
                'prefill_counted_quantity': 'zero',
                'description': 'Product Archive',
            })
            inventory.action_start()
            inventory.action_validate()


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('type')
    def _onchange_type(self):
        res = {}
        if self.type == 'service':
            msg = """Reminder: The Service category is for anything with time as the unit of purchase.

Examples: Training, Extended Warranty, Consulting Hours.

If you’re unsure, review the “Odoo Product Category Cheat Sheet” in Confluence as needed. Link below.

https://confluence.kernel.corp/pages/viewpage.action?pageId=443619295"""

            warning = {'title': _("Product Category"), 'message': msg}
            res.update({'warning': warning})
        return res

    # Custom mandatory fields checkbox
    is_material = fields.Boolean()
    is_thread_size = fields.Boolean()
    is_cat_length = fields.Boolean()
    is_cat_id = fields.Boolean()
    is_od = fields.Boolean()
    is_dash = fields.Boolean()
    is_wire_diameter = fields.Boolean()
    is_free_length = fields.Boolean()
    is_brand = fields.Boolean()
    is_resistance = fields.Boolean()
    is_size = fields.Boolean()
    is_capacitance = fields.Boolean()
    is_turn_ratio = fields.Boolean()
    is_inductance = fields.Boolean()
    is_cat_type = fields.Boolean()
    is_cat_solder = fields.Boolean()
    is_cat_3dprint = fields.Boolean()
    is_signals = fields.Boolean()
    is_gauge = fields.Boolean()
    is_coating = fields.Boolean()
    is_focal_length = fields.Boolean()
    is_polarization = fields.Boolean()
    is_width = fields.Boolean()
    is_thickness = fields.Boolean()
    is_barcode = fields.Boolean()
    # Custom optional fields checkbox
    is_magnetism = fields.Boolean()
    is_compressed_length = fields.Boolean()
    is_press_slip = fields.Boolean()
    is_pins = fields.Boolean()
    is_finish = fields.Boolean()
    is_weight = fields.Boolean()
    is_brand_opt = fields.Boolean()
    is_warranty = fields.Boolean()
    is_pdp_url = fields.Boolean()
    is_mac_address = fields.Boolean()
    is_mac_bluetooth = fields.Boolean()
    is_disk_space = fields.Boolean()
    is_memory = fields.Boolean()
    is_processor = fields.Boolean()
    is_cpu_speed = fields.Boolean()
    is_opt_cat_id = fields.Boolean()
    is_opt_od = fields.Boolean()

    # Custom mandatory fields
    material = fields.Char()
    thread_size = fields.Char()
    cat_length = fields.Char()
    cat_id = fields.Char()
    od = fields.Char()
    dash = fields.Char()
    wire_diameter = fields.Char()
    free_length = fields.Char()
    brand = fields.Char()
    resistance = fields.Char()
    size = fields.Char()
    capacitance = fields.Char()
    turn_ratio = fields.Char()
    inductance = fields.Char()
    cat_type = fields.Selection(selection=[
        ('ic', 'Integrated Circuit'), ('led', 'LED'), ('diode', 'Diode'),
        ('photodiode', 'Photodiode')], help='Semiconductors Type.')
    cat_type_solder = fields.Selection(selection=[
        ('wire', 'Wire'),
        ('paste', 'Paste')], help='Solder Type')
    cat_3dprint = fields.Selection(selection=[
        ('filament', 'Filament'),
        ('resin', 'Resin')], help='3D Print')
    signals = fields.Char()
    gauge = fields.Char()
    coating = fields.Char()
    focal_length = fields.Char()
    polarization = fields.Char()
    thickness = fields.Char()
    width = fields.Char()

    # Custom optional fields
    magnetism = fields.Selection(selection=[
        ('none', 'None'), ('low', 'Low'),
        ('high', 'High')], help='Select Types.')
    compressed_length = fields.Char()
    press_slip = fields.Selection(selection=[
        ('press', 'Press'), ('slip', 'Slip')], help='Select Press/Slip.')
    pins = fields.Char()
    finish = fields.Char()
    kernel_weight = fields.Char()
    brand_opt = fields.Char()
    warranty = fields.Selection(selection=[
        ('applecare', 'AppleCare+'), ('one', '1 Year'), ('two', '2 Year'),
        ('three', '3 Year'), ('other', 'Other'), ], help='Select Warranty.')
    pdp_url = fields.Char()
    mac_address = fields.Char()
    mac_bluetooth = fields.Char()
    disk_space = fields.Selection(selection=[
        ('ds128', '128GB'), ('ds256', '256GB'), ('ds512', '512GB'),
        ('1tb', '1TB'), ('2tb', '2TB'), ('other', 'Other'), ], help='Select Disk Space.')
    memory = fields.Selection(selection=[
        ('m8', '8GB'), ('m16', '16GB'), ('m32', '32GB'),
        ('m64', '64GB'), ('other', 'Other'), ], help='Select Memory.')
    processor = fields.Selection(selection=[
        ('pi3', 'i3'), ('pi5', 'i5'), ('pi7', 'i7'), ('pi9', 'i9'), ('other', 'Other'), ],
        help='Select Processor.')
    cpu_speed = fields.Char()
    opt_cat_id = fields.Char()
    opt_od = fields.Char()

    putaway_rule_ids = fields.One2many('stock.putaway.rule', 'product_id')

    user_archived_id = fields.Many2one('res.users', string="User Archived", copy=False)
    date_archived = fields.Datetime(string="Date Archived", copy=False)

    @api.depends('putaway_rule_ids')
    def _get_location(self):
        for product in self:
            product.location_id = product.putaway_rule_ids and product.putaway_rule_ids[
                0].location_out_id.id or False

    location_id = fields.Many2one('stock.location', string="Location",
                                  compute='_get_location', compute_sudo=True)

    @api.model
    def default_get(self, field_lst):
        res = super(ProductProduct, self).default_get(field_lst)
        if res.get('categ_id', False):
            res.update({'categ_id': False})
        return res

    def _get_onchange_create(self):
        return OrderedDict([
            ('_onchange_categ_id', [
                'is_material', 'is_thread_size', 'is_cat_length',
                'is_cat_id', 'is_od', 'is_dash', 'is_wire_diameter',
                'is_free_length', 'is_brand', 'is_resistance',
                'is_size', 'is_capacitance', 'is_turn_ratio', 'is_inductance',
                'is_cat_type', 'is_cat_solder', 'is_cat_3dprint', 'is_signals',
                'is_gauge', 'is_coating', 'is_focal_length', 'is_polarization',
                'is_width', 'is_thickness', 'is_barcode', 'is_magnetism',
                'is_compressed_length', 'is_press_slip', 'is_pins',
                'is_finish', 'is_weight', 'is_brand_opt', 'is_warranty',
                'is_pdp_url', 'is_mac_address', 'is_mac_bluetooth',
                'is_disk_space', 'is_memory', 'is_processor',
                'is_cpu_speed', 'is_opt_cat_id', 'is_opt_od'])
        ])

    @api.model
    def create(self, vals):
        onchanges = self._get_onchange_create()
        for onchange_method, changed_fields in onchanges.items():
            if any(f not in vals for f in changed_fields):
                category = self.new(vals)
                getattr(category, onchange_method)()
                for field in changed_fields:
                    if field not in vals and category[field]:
                        vals[field] = category._fields[
                            field].convert_to_write(category[field], category)
        return super(ProductProduct, self).create(vals)

    @api.onchange('categ_id')
    def _onchange_categ_id(self):
        if self.categ_id:
            self.tracking = self.categ_id.tracking
            self.type = self.categ_id.type
            product_category = self.env['product.category']
            product_category_ids = product_category.search(
                [('id', 'parent_of', self.categ_id.id)])
            if [categ for categ in product_category_ids if categ.is_material]:
                self.is_material = True
                self.material = False
            else:
                if self.material:
                    self.material = False
                self.is_material = False

            if [categ for categ in product_category_ids if categ.is_thread_size]:
                self.is_thread_size = True
                self.thread_size = False
            else:
                if self.thread_size:
                    self.thread_size = False
                self.is_thread_size = False

            if [categ for categ in product_category_ids if categ.is_cat_length]:
                self.is_cat_length = True
                self.cat_length = False
            else:
                if self.cat_length:
                    self.cat_length = False
                self.is_cat_length = False

            if [categ for categ in product_category_ids if categ.is_cat_id]:
                self.is_cat_id = True
                self.cat_id = False
            else:
                if self.cat_id:
                    self.cat_id = False
                self.is_cat_id = False

            if [categ for categ in product_category_ids if categ.is_od]:
                self.is_od = True
                self.od = False
            else:
                if self.od:
                    self.od = False
                self.is_od = False

            if [categ for categ in product_category_ids if categ.is_dash]:
                self.is_dash = True
                self.dash = False
            else:
                if self.dash:
                    self.dash = False
                self.is_dash = False

            if [categ for categ in product_category_ids if categ.is_wire_diameter]:
                self.is_wire_diameter = True
                self.wire_diameter = False
            else:
                if self.wire_diameter:
                    self.wire_diameter = False
                self.is_wire_diameter = False

            if [categ for categ in product_category_ids if categ.is_free_length]:
                self.is_free_length = True
                self.free_length = False
            else:
                if self.free_length:
                    self.free_length = False
                self.is_free_length = False

            if [categ for categ in product_category_ids if categ.is_brand]:
                self.is_brand = True
                self.brand = False
            else:
                if self.brand:
                    self.brand = False
                self.is_brand = False

            if [categ for categ in product_category_ids if categ.is_resistance]:
                self.is_resistance = True
                self.resistance = False
            else:
                if self.resistance:
                    self.resistance = False
                self.is_resistance = False

            if [categ for categ in product_category_ids if categ.is_size]:
                self.is_size = True
                self.size = False
            else:
                if self.size:
                    self.size = False
                self.is_size = False

            if [categ for categ in product_category_ids if categ.is_capacitance]:
                self.is_capacitance = True
                self.capacitance = False
            else:
                if self.capacitance:
                    self.capacitance = False
                self.is_capacitance = False

            if [categ for categ in product_category_ids if categ.is_turn_ratio]:
                self.is_turn_ratio = True
                self.turn_ratio = False
            else:
                if self.turn_ratio:
                    self.turn_ratio = False
                self.is_turn_ratio = False

            if [categ for categ in product_category_ids if categ.is_inductance]:
                self.is_inductance = True
                self.inductance = False
            else:
                if self.inductance:
                    self.inductance = False
                self.is_inductance = False

            if [categ for categ in product_category_ids if categ.is_signals]:
                self.is_signals = True
                self.signals = False
            else:
                if self.signals:
                    self.signals = False
                self.is_signals = False

            if [categ for categ in product_category_ids if categ.is_gauge]:
                self.is_gauge = True
                self.gauge = False
            else:
                if self.gauge:
                    self.gauge = False
                self.is_gauge = False

            if [categ for categ in product_category_ids if categ.is_coating]:
                self.is_coating = True
                self.coating = False
            else:
                if self.coating:
                    self.coating = False
                self.is_coating = False

            if [categ for categ in product_category_ids if categ.is_focal_length]:
                self.is_focal_length = True
                self.focal_length = False
            else:
                if self.focal_length:
                    self.focal_length = False
                self.is_focal_length = False

            if [categ for categ in product_category_ids if categ.is_polarization]:
                self.is_polarization = True
                self.polarization = False
            else:
                if self.polarization:
                    self.polarization = False
                self.is_polarization = False

            if [categ for categ in product_category_ids if categ.is_thickness]:
                self.is_thickness = True
                self.thickness = False
            else:
                if self.thickness:
                    self.thickness = False
                self.is_thickness = False

            if [categ for categ in product_category_ids if categ.is_width]:
                self.is_width = True
                self.width = False
            else:
                if self.width:
                    self.width = False
                self.is_width = False

            if [categ for categ in product_category_ids if categ.is_barcode]:
                self.is_barcode = True
                self.barcode = False
            else:
                if self.barcode:
                    self.barcode = False
                self.is_barcode = False

            if [categ for categ in product_category_ids if categ.is_compressed_length]:
                self.is_compressed_length = True
                self.compressed_length = False
            else:
                if self.compressed_length:
                    self.compressed_length = False
                self.is_compressed_length = False

            if [categ for categ in product_category_ids if categ.is_press_slip]:
                self.is_press_slip = True
                self.press_slip = False
            else:
                if self.press_slip:
                    self.press_slip = False
                self.is_press_slip = False

            if [categ for categ in product_category_ids if categ.is_pins]:
                self.is_pins = True
                self.pins = False
            else:
                if self.pins:
                    self.pins = False
                self.is_pins = False

            if [categ for categ in product_category_ids if categ.is_finish]:
                self.is_finish = True
                self.finish = False
            else:
                if self.finish:
                    self.finish = False
                self.is_finish = False

            if [categ for categ in product_category_ids if categ.is_weight]:
                self.is_weight = True
                self.kernel_weight = False
            else:
                if self.kernel_weight:
                    self.kernel_weight = False
                self.is_weight = False

            if [categ for categ in product_category_ids if categ.is_pdp_url]:
                self.is_pdp_url = True
                self.pdp_url = False
            else:
                if self.pdp_url:
                    self.pdp_url = False
                self.is_pdp_url = False

            if [categ for categ in product_category_ids if categ.is_mac_address]:
                self.is_mac_address = True
                self.mac_address = False
            else:
                if self.mac_address:
                    self.mac_address = False
                self.is_mac_address = False

            if [categ for categ in product_category_ids if categ.is_mac_bluetooth]:
                self.is_mac_bluetooth = True
                self.mac_bluetooth = False
            else:
                if self.mac_bluetooth:
                    self.mac_bluetooth = False
                self.is_mac_bluetooth = False

            if [categ for categ in product_category_ids if categ.is_cpu_speed]:
                self.is_cpu_speed = True
                self.cpu_speed = False
            else:
                if self.cpu_speed:
                    self.cpu_speed = False
                self.is_cpu_speed = False

            if [categ for categ in product_category_ids if categ.is_cat_type]:
                self.is_cat_type = True
                self.cat_type = False
            else:
                if self.cat_type:
                    self.cat_type = False
                self.is_cat_type = False

            if [categ for categ in product_category_ids if categ.is_cat_solder]:
                self.is_cat_solder = True
                self.cat_type_solder = False
            else:
                if self.cat_type_solder:
                    self.cat_type_solder = False
                self.is_cat_solder = False

            if [categ for categ in product_category_ids if categ.is_cat_3dprint]:
                self.is_cat_3dprint = True
                self.cat_3dprint = False
            else:
                if self.cat_3dprint:
                    self.cat_3dprint = False
                self.is_cat_3dprint = False

            if [categ for categ in product_category_ids if categ.is_magnetism]:
                self.is_magnetism = True
                self.magnetism = False
            else:
                if self.magnetism:
                    self.magnetism = False
                self.is_magnetism = False

            if [categ for categ in product_category_ids if categ.is_brand_opt]:
                self.is_brand_opt = True
                self.brand_opt = False
            else:
                if self.brand_opt:
                    self.brand_opt = False
                self.is_brand_opt = False

            if [categ for categ in product_category_ids if categ.is_warranty]:
                self.is_warranty = True
                self.warranty = False
            else:
                if self.warranty:
                    self.warranty = False
                self.is_warranty = False

            if [categ for categ in product_category_ids if categ.is_disk_space]:
                self.is_disk_space = True
                self.disk_space = False
            else:
                if self.disk_space:
                    self.disk_space = False
                self.is_disk_space = False

            if [categ for categ in product_category_ids if categ.is_memory]:
                self.is_memory = True
                self.memory = False
            else:
                if self.memory:
                    self.memory = False
                self.is_memory = False

            if [categ for categ in product_category_ids if categ.is_processor]:
                self.is_processor = True
                self.processor = False
            else:
                if self.processor:
                    self.processor = False
                self.is_processor = False

            if [categ for categ in product_category_ids if categ.is_opt_cat_id]:
                self.is_opt_cat_id = True
                self.opt_cat_id = False
            else:
                if self.opt_cat_id:
                    self.opt_cat_id = False
                self.is_opt_cat_id = False

            if [categ for categ in product_category_ids if categ.is_opt_od]:
                self.is_opt_od = True
                self.opt_od = False
            else:
                if self.opt_od:
                    self.opt_od = False
                self.is_opt_od = False

    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        if 'active' in vals and len(vals) == 1 and 'default_type' not in self._context:
            if not self.env.user.has_group('product_extension.group_product_archive_access'):
                raise AccessError(_("You do not have access to archive or unarchive product."))
            else:
                for rec in self:
                    if vals['active'] is False:
                        rec.message_post(body="Product archived")
                        rec.user_archived_id = self.env.user.id
                        rec.date_archived = fields.Datetime.now()
                    else:
                        rec.message_post(body="Product unarchived")
                        rec.user_archived_id = False
                        rec.date_archived = False
        return res

    def set_quantity_zero(self):
        for rec in self:
            inventory = self.env['stock.inventory'].create({
                'name': 'Set Quantity Zero',
                'product_ids': [(4, rec.id)],
                'accounting_date': datetime.now().date(),
                'prefill_counted_quantity': 'zero',
                'description': 'Product Archive'})
            inventory.action_start()
            inventory.action_validate()
