# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Internal Transfers from Products",
    'version': "13.0.0.1.1",
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "https://www.bistasolutions.com",
    'category': "Operations/Inventory/Products",
    'summary': """Internal Transfers from Product Page""",
    'description': """
        Internal Transfers from Product Page
    """,
    'depends': ['stock_account', 'product_extension'],
    'data': [
        'wizard/transfer_stock_view.xml',
        'views/product_template_view.xml',
        'views/stock_move_line_views.xml',
    ],
    'installable': True,
    'auto_install': False
}
