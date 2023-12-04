# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Kernel - MRP Account",
    'category': "Accounting",
    'version': '13.0.1.0.0',
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "http://www.bistasolutions.com",

    'summary': """Links manufacturing order reference to journal entry""",
    'description': """
        This module links manufacturing order reference to journal entry.
    """,

    'depends': ['account', 'mrp', 'product_extension'],

    'data': [
        'security/mrp_security.xml',
        'views/account_move_view.xml',
        'views/account_move_line_view.xml',
    ],
    'installable': True,
    'auto_install': True
}
