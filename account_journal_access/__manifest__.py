# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': 'Account Journal Access',
    'version': '13.0.1.0.0',
    'summary': """This module developed for view access of account
        journal for specific users only.""",
    'description': """
        This module developed for view access of account
        journal for specific users only.
    """,
    'category': 'Extra Tools',
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "http://www.bistasolutions.com",
    'depends': ['base', 'account'],
    'data': [
        'security/reconcile_security.xml',
        'security/ir.model.access.csv',
        'views/res_users_view.xml',
    ],
    'installable': True,
    'application': False,
}
