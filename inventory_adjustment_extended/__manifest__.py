# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': 'Inventory Adjustment Extended',
    "version": "1.0",
    "author": "Bista Solutions",
    "website": "http://www.bistasolutions.com",
    'depends': ['stock_account'],
    'description': """ 
Inventory Adjustment Extended
=============================
This module sets Expense account on journal items during Inventory Adjustment.
    """,
    'data': [
        'data/inventory_adjustment_sequence.xml',
        'views/res_config_settings_view.xml',
        'views/inventory_adjustment_view.xml',
        'views/template.xml',
    ],
    'installable': True,
    'auto_install': False,
}
