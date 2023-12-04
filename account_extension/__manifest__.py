# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Kernel - Account Extension",
    'version': "13.0.0.1.1",
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "https://www.bistasolutions.com",
    'category': "Accounting",
    'summary': """Account Extension""",
    'description': """
        Kernel - Accounting Related Customization.
    """,
    'depends': ['account', 'stock_account'],
    'data': [
        'views/product_view.xml',
        'views/res_partner_view.xml',
        'views/account_invoice_view.xml'
    ],
    'installable': True,
    'auto_install': False
}
