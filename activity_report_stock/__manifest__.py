# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': 'Stock Inventory Valuation Report',
    'version': '1.0',
    'category': 'stock',
    'summary': 'Stock Valuation between Start Date and End Date in XLS/PDF formatted reports',
    'description': """
        Stock Valuation Report between Start Date and End Date,
        ----------------------------------
    """,
    'author': 'Bista Solutions',
    'website': 'https://bistasolutions.com',
    'depends': ['purchase_rfo', 'inventory_adjustment_extended', 'kernel_stock'],
    'data': [
        'wizard/stock_valuation.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
