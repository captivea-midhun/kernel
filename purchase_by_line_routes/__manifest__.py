# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Purchase by Line Routes",
    'version': "13.0.0.1.1",
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "https://www.bistasolutions.com",
    'category': "Purchase",
    'summary': """Receive products based on selected routes on
    product and product category.""",
    'description': """This modules helps to receive products based on selected
    routes on product and product category.""",
    'depends': ['purchase_stock'],
    'data': [
        'views/product_category_view.xml',
        'views/product_view.xml',
        'views/purchase_view.xml'
    ],
    'installable': True,
    'auto_install': False
}
