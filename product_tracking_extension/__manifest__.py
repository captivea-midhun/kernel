# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Product Tracking ",
    'version': "13.0.0.1.1",
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "https://www.bistasolutions.com",
    'category': "Purchase",
    'summary': """Track product based on Lot + Serial option.""",
    'description': """This modules helps to Track Product based on Lot + Serial Option.""",
    'depends': ['product_extension'],
    'data': [
        'views/stock_production_lots.xml',
    ],
    'installable': True,
    'auto_install': False
}
