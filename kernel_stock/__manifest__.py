# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Kernel Stock",

    'summary': """ Contain Stock Modification """,

    'description': """
        Module contain stock modification
    """,

    'author': "Bista Solutions Inc.",
    'website': "http://www.bistasolutions.com",

    'category': 'Stock',
    'version': '13.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['mrp'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_move_line_views.xml',
        'views/stock_scrap_views.xml',
        'views/stock_quant_view.xml',
    ],

    'installable': True,
    'auto_install': False
}
