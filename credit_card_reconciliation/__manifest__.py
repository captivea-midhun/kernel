# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Kernel - Credit Card Reconciliation",
    'version': "13.0.0.1.1",
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "http://www.bistasolutions.com",
    'category': "Accounting",
    'summary': """Create Credit Card Reconciliation""",
    'description': """
        Create Credit Card Reconciliation
    """,
    'depends': ['account'],
    'data': [
        'views/templates.xml',
    ],
    'qweb': [
        "static/src/xml/account_reconciliation.xml"],
    'installable': True
}
