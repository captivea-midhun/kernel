# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

import ast
import os
import shutil

from odoo import models


class MrpTestResultScheduler(models.Model):
    _name = 'mrp.test.result.scheduler'
    _description = 'MRP Test Result Scheduler'

    def mrp_test_scheduler(self):
        """
        Read data from .txt file and generate record in table record.
        """
        mrp_test_result_config = self.env['mrp.test.result.config'].search([], limit=1)

        file_path = mrp_test_result_config.file_path
        error_file_path = mrp_test_result_config.error_file_read_path
        success_file_path = mrp_test_result_config.success_file_read_path

        if not file_path or not error_file_path or not success_file_path:
            return True

        table_header_obj = self.env['table.header']
        table_subtest_obj = self.env['table.subtest']
        error_obj = self.env['mrp.test.result.error']
        product_obj = self.env['product.product']
        lot_obj = self.env['stock.production.lot']
        header = False
        subheader = False
        header_id = False
        error_file_move = True

        for file in os.listdir(file_path):
            if not file.endswith(".txt"):
                continue
            product_id = False
            lot_id = False
            fp = file_path + file
            table_header_id = table_header_obj.search([('filename', '=', file)])
            if not table_header_id:
                try:
                    for line in open(str(fp), 'r'):
                        vals = {}
                        if 'Header:' in line:
                            header = True
                            subheader = False
                        if 'Subtest:' in line:
                            subheader = True
                            header = False
                        if header and '{' in line:
                            data = ast.literal_eval(line)
                            for k, v in data.items():
                                if k == 'Operator':
                                    vals.update({'operator': v})
                                if k == 'PartNumber':
                                    product_id = product_obj.search(
                                        [('default_code', '=', v.strip())])
                                    if product_id:
                                        vals.update(
                                            {'part_number': v, 'product_id': product_id.id})
                                if k == 'SerialNumber' and product_id:
                                    lot_id = lot_obj.search(
                                        [('product_id', '=', product_id.id),
                                         ('name', '=', v.strip())])
                                    if lot_id:
                                        vals.update({'serial_number': v})
                                if k == 'Station':
                                    vals.update({'station': v})
                                if k == 'Step':
                                    vals.update({'step': v})
                                if k == 'Date time':
                                    vals.update({'datetime': v})
                                if k == 'filename':
                                    # Handles escape sequence in filename
                                    v = v.replace("\t", "\\t")
                                    v = v.replace("\r", "\\r")
                                    vals.update({'filename': v})
                                if k == 'Temperature':
                                    vals.update({'temperature': v})
                                if k == 'Notes':
                                    vals.update({'notes': v})
                                if k == 'PassFail':
                                    if v == '1':
                                        vals.update({'pass_fail': True})
                                    else:
                                        vals.update({'pass_fail': False})
                                if k == 'Bin':
                                    vals.update({'bin': v})
                            if product_id and lot_id:
                                header_id = table_header_obj.create(vals)
                            else:
                                error_obj.create(
                                    {'name': file,
                                     'error_msg': "Product SKU or Serial Number Not Found"})
                                shutil.move(fp, error_file_path)
                                error_file_move = False
                        if subheader and '{' in line and header_id:
                            data = ast.literal_eval(line)
                            for k, v in data.items():
                                if k == 'parameter':
                                    vals.update({'parameter': v})
                                if k == 'result':
                                    vals.update({'result': v})
                                if k == 'pf':
                                    vals.update({'pf': v})
                                if k == 'parentparameter':
                                    vals.update({'parent_parameter': v})
                                if k == 'channel':
                                    vals.update({'channel': v})
                            if vals:
                                vals.update({'hid': header_id.id})
                                table_subtest_obj.create(vals)
                    if header_id:
                        shutil.move(file_path + file, success_file_path)
                        error_file_move = False
                except Exception as e:
                    error_obj.create({'name': file, 'error_msg': str(e)})
                    if error_file_move:
                        shutil.move(fp, error_file_path)
            else:
                error_obj.create(
                    {'name': file, 'error_msg': "Already recorded file in odoo."})
                shutil.move(fp, error_file_path)
        return True
