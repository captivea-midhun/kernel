# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Product Quantity in Detail",

    'summary': """ Product detailed quantity view """,

    'description': """ 
    Inside product form view, Added buttons for quantity view in detail 
    """,

    'author': "Bista Solutions Inc.",
    'website': "http://www.bistasolutions.com",

    # for the full list
    'category': 'Stock',
    'version': '13.0.0.2',

    # any module necessary for this one to work correctly
    'depends': ['mrp', 'purchase_rfo'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/product_detailed_qty_views.xml',
        'views/product_template_views.xml',
        'views/product_product_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
