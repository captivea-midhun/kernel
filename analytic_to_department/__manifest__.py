# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Kernel - Analytic To Department",
    'version': "13.0.0.1.1",
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "https://www.bistasolutions.com",
    'category': "Accounting",
    'summary': """Account Extension""",
    'description': """
        Kernel - Analytic Account Related Customization,
        Rename Analytic Account to Department.
    """,
    'depends': ['account', 'account_asset', 'account_reports', 'purchase'],
    'data': [
        'views/assets_templates.xml',
        'views/analytic_account_view_inherit.xml',
    ],
    'installable': True
}
