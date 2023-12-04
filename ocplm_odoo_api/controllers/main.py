"""Part of odoo. See LICENSE file for full copyright and licensing details."""

import functools
import json
import logging
from odoo import http
from odoo.addons.ocplm_odoo_api.common import invalid_response
from odoo.http import request

_logger = logging.getLogger(__name__)


def validate_token(func):
    """."""

    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        access_token = request.httprequest.headers.get("access_token")
        if not access_token:
            return invalid_response(
                "access_token_not_found", "missing access token in request header", 402
            )
        access_token_data = (
            request.env["api.access_token"]
            .sudo()
            .search([("token", "=", access_token)], order="id DESC", limit=1)
        )
        if (
            access_token_data.find_one_or_create_token(
                user_id=access_token_data.user_id.id
            )
            != access_token
        ):
            return invalid_response(
                "access_token", "token seems to have expired or invalid", 402
            )
        request.session.uid = access_token_data.user_id.id
        request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)
    return wrap


_routes_create_partner = ["/api/create_partner_from_ocplm_odoo"]
_routes_create_part = ["/api/create_part_from_ocplm_odoo"] 
_routes_standard_cost = ["/api/odoo_standard_cost_ocplm"]
_routes_product_category = ["/api/odoo_product_category_ocplm"]
_routes_create_bom = ["/api/create_bom_from_ocplm_odoo"]


class APIController(http.Controller):
    """."""

    def __init__(self):
        self._model = "ir.model"

    def validate_product_category(self, categ_id):
        product_category = request.env['product.category'].search([('name', '=', categ_id)])
        if product_category:
            return product_category
        return False

    def validate_product_uom(self, uom_id):
        product_uom = request.env['uom.uom'].search([('id', '=', uom_id)])
        if product_uom:
            return product_uom
        return False

    def validate_field_name(self, name):
        if name.strip() != '':
            return name.strip()
        return False

    def validate_product_tracking(self, tracking):
        if tracking in ['serial', 'lot', 'none']:
            return tracking
        return False

    def validate_product_type(self, pro_type):
        if pro_type in ['consu','service','product']:
            return pro_type
        return False

    def validate_product_default_code(self, default_code):
        if str(default_code).strip() != '':
            match_found = request.env['product.template'].search([('default_code', '=', default_code)])
            if not match_found:
                return str(default_code).strip()
        return False

    def validate_country(self, country_id):
        country = request.env['res.country'].search([('id','=',country_id)])
        if country:
            return country
        return False

    def validate_state(self, state_id):
        state = request.env['res.country.state'].search([('id','=',state_id)])
        if state:
            return state
        return False

    def validate_ready_to_produce(self, ready_to_produce):
        if ready_to_produce in ['all_available', 'asap']:
            return ready_to_produce
        return False

    def validate_consumption(self, consumption):
        if consumption in ['strict', 'flexible']:
            return consumption
        return False

    def validate_bom_type(self, pro_type):
        if pro_type in ['normal','phantom','subcontract']:
            return pro_type
        return False

    def validate_route_ids(self, route_ids):
        route_id = request.env['stock.location.route'].search([('name', 'in', route_ids)])
        if route_id:
            return route_id.ids
        else:
            return False

    @validate_token
    @http.route(_routes_create_partner, auth="none", type="json", methods=["POST"], csrf=False)
    def create_partner_from_ocplm_odoo(self, **payload):
        """To create a partner"""
        valid_response_list = []
        try:
            payload_list = json.loads(request.httprequest.data.decode())
        except Exception as e:
            valid_response_list.append({'default_code': '', 'status': False, 'id': 0, 'msg': str(e)})
            return json.dumps(valid_response_list)
        try:
            request_data = payload_list.get('request_data', [])
            if not request_data:
                valid_response_list.append({'default_code': '', 'status': False, 'id': 0, 'msg': 'request_data key not found.'})
                return json.dumps(valid_response_list)
        except Exception as e:
            valid_response_list.append(
                {'default_code': '', 'status': False, 'id': 0, 'msg': str(e)})
            return json.dumps(valid_response_list)
        for data in request_data:
            data.update({'company_type': 'company', 'customer_rank': 0, 'supplier_rank': 1, 'nda': 0, 'nda_note': ''})
            valid_record = True
            if 'name' in data.keys():
                product_name = self.validate_field_name(data.get('name'))
                if not product_name:
                    valid_record = False
                    valid_response_list.append({'default_code': data.get('name'), 'status': False, 'id': 0, 'msg': 'Enter Partner name.'})
            else:
                valid_response_list.append({'default_code': data.get('name'), 'status': False, 'id': 0, 'msg': 'name key is missing.'})

            if 'country_id' in data.keys():
                country_name = self.validate_country(data.get('country_id'))
                if not country_name:
                    valid_record = False
                    valid_response_list.append({'default_code': data.get('name'), 'status': False, 'id': 0, 'msg': 'Enter Valid Country.'})
            if 'state_id' in data.keys():
                state_name = self.validate_state(data.get('state_id'))
                if not state_name:
                    valid_record = False
                    valid_response_list.append({'default_code': data.get('name'), 'status': False, 'id': 0, 'msg': 'Enter Valid State.'})
            if valid_record:
                try:
                    with request.env.cr.savepoint():
                        new_partner = request.env['res.partner'].create(data)
                        valid_response_list.append({'name': new_partner.name, 'status': True, 'id': new_partner.id, 'msg': 'Successfully created'})
                except Exception as e:
                        valid_response_list.append({'name': data.get('name'), 'status': False, 'id': 0, 'msg': str(e)})
        return json.dumps(valid_response_list)

    def validate_payload(self,request_data):
        validate = False
        valid_response_list = []
        for data in request_data:
            data.update({'active': 1, 'uom_id': 1})
            valid_record = True
            if 'name' in data.keys():
                product_name = self.validate_field_name(data.get('name'))
                if not product_name:
                    valid_response_list.append({'default_code': data.get('default_code'), 'status': False, 'id': 0, 'msg': 'Enter product name.'})
                    return json.dumps(valid_response_list)
            if 'categ_id' in data.keys():
                product_cat = self.validate_product_category(data.get('categ_id'))
                if not product_cat:
                    valid_response_list.append({'default_code': data.get('default_code'), 'status': False, 'id': 0, 'msg': 'Product category not exist'})
                    return json.dumps(valid_response_list)
            else:
                valid_response_list.append({'default_code': data.get('default_code'), 'status': False, 'id': 0, 'msg': 'categ_id key is missing.'})
                return json.dumps(valid_response_list)
            if 'tracking' in data.keys():
                tracking = self.validate_product_tracking(data.get('tracking'))
                if not tracking:
                    valid_response_list.append({'default_code': data.get('default_code'), 'status': False, 'id': 0, 'msg': 'Product tracking is not valid'})
                    return json.dumps(valid_response_list)
            else:
                valid_response_list.append({'default_code': data.get('default_code'), 'status': False, 'id': 0, 'msg': 'tracking key is missing.'})
                return json.dumps(valid_response_list)
            if 'default_code' in data.keys():
                default_code = self.validate_product_default_code(data.get('default_code'))
                if not default_code:
                    valid_response_list.append({'default_code': data.get('default_code'), 'status': False, 'id': 0, 'msg': 'Product default_code must be unique.'})
                    return json.dumps(valid_response_list)
            else:
                valid_response_list.append({'default_code': data.get('default_code'), 'status': False, 'id': 0, 'msg': 'default_code key is missing.'})
                return json.dumps(valid_response_list)
            data_route_ids = []
            if 'route_ids' in data.keys():
                data_route_ids = self.validate_route_ids(data.get('route_ids'))
                if not data_route_ids:
                    valid_record = False
                    valid_response_list.append(
                        {'default_code': data.get('default_code'),
                         'status': False, 'id': 0,
                         'msg': 'route_ids is not valid'})
                    return json.dumps(valid_response_list)
            else:
                valid_record = False
                valid_response_list.append(
                    {'default_code': data.get('default_code'), 'status': False,
                     'id': 0, 'msg': 'route_ids key is missing.'})
                return json.dumps(valid_response_list)
        return True



    @validate_token
    @http.route(_routes_create_part, auth="none", type="json", methods=["POST"], csrf=False)
    def create_part_from_ocplm_odoo(self, **payload):
        """To create a part"""
        valid_response_list = []
        try:
            payload_list = json.loads(request.httprequest.data.decode())
        except Exception as e:
            valid_response_list.append({'default_code': '', 'status': False, 'id': 0, 'msg': str(e)})
            return json.dumps(valid_response_list)
        try:
            request_data = payload_list.get("request_data", [])
            if not request_data:
                valid_response_list.append({'default_code': '', 'status': False, 'id': 0, 'msg': str('request_data key not found.')})
                return json.dumps(valid_response_list)
        except Exception as e:
            valid_response_list.append(
                {'default_code': '', 'status': False, 'id': 0, 'msg': str(e)})
            return json.dumps(valid_response_list)
        validate = self.validate_payload(request_data)
        if validate == True:
            for data in request_data:
                data.update({'active': 1, 'uom_id': 1})
                product_cat = self.validate_product_category(data.get('categ_id'))
                data.pop("categ_id")
                data.update({'categ_id' : product_cat.id})
                data.update({'type': product_cat.type})
                data_route_ids = []
                try:
                    with request.env.cr.savepoint():
                        route_data = data.get('route_ids')
                        data_route_ids = self.validate_route_ids(data.get('route_ids'))
                        data.pop('route_ids')
                        new_part = request.env['product.template'].create(data)
                        new_part.update({'sale_ok':False})
                        if data.get('image'):
                            new_part.update({'image_1920': data.get('image')})

                        product = request.env['product.product'].search(
                            [('product_tmpl_id', '=', new_part.id)])

                        for att in data.get('attachment'):

                            attachment = self.env['ir.attachment'].create({
                                'datas': att.get('Content'),
                                'name': att.get('filename'),
                                'type': 'binary',
                            })
                            product.message_post(attachment_ids=[attachment.id])

                        if 'Buy' not in route_data:
                            new_part.update({'purchase_ok' : False})
                        if data_route_ids:
                            new_part.update(
                                    {'route_ids': [(6, 0, data_route_ids)]})
                except Exception as e:
                    valid_response_list.append({'default_code': data.get('default_code'), 'status': False, 'id': 0, 'msg': str(e)})
                    return json.dumps(valid_response_list)
                valid_response_list.append({'default_code': new_part.default_code, 'status': True, 'id': new_part.id,
                                                'msg': 'Successfully created'})
            return json.dumps(valid_response_list)
        else:
            return validate

    @validate_token
    @http.route(_routes_standard_cost, auth="none", type="json", methods=["POST"], csrf=False)
    def odoo_standard_cost_ocplm(self, **payload):
        """To Send the standard cost from ODOO to OCPPLM"""
        valid_response_list = []

        try:
            payload_list = json.loads(request.httprequest.data.decode())
        except Exception as e:
            valid_response_list.append({'default_code': '','status': False,'msg': str(e)})
            return json.dumps(valid_response_list)
        if not payload_list['default_code']:
            valid_response_list.append({'default_code': '', 'status': False, 'msg': "data not found"})
            return json.dumps(valid_response_list)
        try:
            # with environment() as env:
            with request.env.cr.savepoint():
                    products = request.env['product.product'].search([('default_code', 'in', payload_list.get('default_code'))])
                    for product in products:
                        valid_response_list.append({'default_code': product.default_code, 'cost': product.standard_price})
        except Exception as e:
                valid_response_list.append({'default_code': '','status': False,'msg': str(e)})
        return json.dumps(valid_response_list)
    
    @validate_token
    @http.route(_routes_product_category, auth="none", type="json", methods=["POST"], csrf=False)
    def odoo_product_category_ocplm(self, **payload):
        """To Send the standard cost from ODOO to OCPPLM"""
        valid_response_list = []
        try:
            # with environment() as env:
            with request.env.cr.savepoint():
                categorys = request.env['product.category'].search([])
                for category in categorys:
                    valid_response_list.append({'id': category.id, 'name': category.name})
        except Exception:
                valid_response_list.append({'id': 0, 'name': False})
        return json.dumps(valid_response_list)

    @validate_token
    @http.route(_routes_create_bom, auth="none", type="json", methods=["POST"], csrf=False)
    def create_bom_from_ocplm_odoo(self, **payload):
        """To create a bom"""
        valid_response_list = []
        try:
            payload_list = json.loads(request.httprequest.data.decode())
        except Exception as e:
            valid_response_list.append({'default_code': '', 'status': False, 'id': 0, 'msg': str(e)})
            return json.dumps(valid_response_list)
        try:
            request_data = payload_list.get("request_data", [])
            if not request_data:
                valid_response_list.append({'default_code': '', 'status': False, 'id': 0, 'msg': str('request_data key not found.')})
                return json.dumps(valid_response_list)
        except Exception as e:
            valid_response_list.append(
                {'default_code': '', 'status': False, 'id': 0, 'msg': str(e)})
            return json.dumps(valid_response_list)
        for data in request_data:
            data['bom'].update({'ready_to_produce': 'all_available'})
            valid_record = True
            data_bom = data['bom']
            bom_line = data['bom_line']
            vals = {}
            if data.get('bom'):
                if 'default_code' in data_bom.keys():
                    default_code = data_bom.get('default_code')
                    product_id = request.env['product.template'].search(
                        [('default_code', '=', default_code)]
                    )
                    if not product_id:
                        valid_record = False
                        valid_response_list.append(
                            {'default_code': default_code,
                             'status': False, 'id': 0,
                             'msg': 'Product default_code must be unique.'})
                    vals.update({'product_tmpl_id': product_id.id})
                else:
                    valid_record = False
                    valid_response_list.append({'default_code': data_bom.get('default_code'), 'status': False, 'id': 0, 'msg': 'default_code key is missing.'})

                if 'product_qty' in data_bom.keys():
                    product_qty = data_bom.get('product_qty')
                    vals.update({'product_qty': product_qty})
                if 'is_slot' in data_bom.keys():
                    is_slot = data_bom.get('is_slot')
                    vals.update({'is_slot': is_slot})
                if 'type' in data_bom.keys():
                    pro_type = self.validate_bom_type(data_bom.get('type'))
                    if not pro_type:
                        valid_record = False
                        valid_response_list.append(
                            {'default_code': data_bom.get('default_code'),
                             'status': False, 'id': 0,
                             'msg': 'type is not valid'})
                    vals.update({'type': pro_type})
                else:
                    valid_record = False
                    valid_response_list.append(
                        {'default_code': data_bom.get('default_code'), 'status': False,
                         'id': 0, 'msg': 'type key is missing.'})
                if 'ready_to_produce' in data_bom.keys():
                    ready_to_produce = self.validate_ready_to_produce(data_bom.get('ready_to_produce'))
                    if not ready_to_produce:
                        valid_record = False
                        valid_response_list.append(
                            {'default_code': data_bom.get('default_code'),
                             'status': False, 'id': 0,
                             'msg': 'ready_to_produce is not valid.'}
                        )
                    vals.update({'ready_to_produce': ready_to_produce})
                else:
                    valid_record = False
                    valid_response_list.append(
                        {'default_code': data_bom.get('default_code'),
                         'status': False,
                         'id': 0, 'msg': 'ready_to_produce key is missing.'}
                    )
                if 'consumption' in data_bom.keys():
                    consumption = self.validate_consumption(data_bom.get('consumption'))
                    if not consumption:
                        valid_record = False
                        valid_response_list.append(
                            {'default_code': data_bom.get('default_code'),
                             'status': False, 'id': 0,
                             'msg': 'Consumption not valid.'}
                        )
                    vals.update({'consumption': consumption})
                else:
                    valid_record = False
                    valid_response_list.append(
                        {'default_code': data_bom.get('default_code'),
                         'status': False,
                         'id': 0, 'msg': 'consumption key is missing.'}
                    )
            bom_line_list = []
            for data_bom_line in bom_line:
                data_bom_line.update({'product_uom_id': 1})
                line_vals = {}
                if 'default_code' in data_bom_line.keys():
                    default_code = data_bom_line.get('default_code')
                    product_id = request.env['product.product'].search(
                        [('default_code', '=', default_code)]
                    )
                    if not product_id:
                        valid_record = False
                        valid_response_list.append(
                            {'default_code': data_bom_line.get('default_code'),
                             'status': False, 'id': 0,
                             'msg': 'Product default_code must be unique.'})

                    line_vals.update({'product_id': product_id.id})
                else:
                    valid_record = False
                    valid_response_list.append({'default_code': data_bom_line.get('default_code'), 'status': False, 'id': 0, 'msg': 'default_code key is missing.'})
                if 'product_qty' in data_bom_line.keys():
                    product_qty = data_bom_line.get('product_qty')
                    line_vals.update({'product_qty': product_qty})
                if 'slot' in data_bom_line.keys():
                    slot = data_bom_line.get('slot')
                    line_vals.update({'slot': slot})
                bom_line_list.append((0, 0, line_vals))
            if bom_line_list:
                vals.update({'bom_line_ids': bom_line_list})
            if valid_record:
                try:
                    with request.env.cr.savepoint():
                        new_bom = request.env['mrp.bom'].create(vals)
                        valid_response_list.append({'default_code': new_bom.product_tmpl_id.default_code, 'status': True, 'id': new_bom.id, 'msg': 'Successfully created'})
                except Exception as e:
                    valid_response_list.append({'default_code': data['bom'].get('default_code'), 'status': False, 'id': 0, 'msg': str(e)})
        return json.dumps(valid_response_list)

