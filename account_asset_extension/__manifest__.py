# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Kernel - Account Asset Extension",
    'version': "13.0.0.3.1",
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "https://www.bistasolutions.com",
    'category': 'Accounting/Accounting',
    'summary': """Accounting Asset Customization""",
    'description': """
        Kernel - Accounting Asset Customization.
    """,
    'depends': ['account_asset'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'report/reports.xml',
        'wizard/wizard_fixed_asset_report_view.xml',
        'wizard/asset_sell_views.xml',
        'views/account_account_view.xml',
        'report/fixed_asset_report_template.xml',
        'report/cip_report_template.xml',
    ],
    'installable': True,
    'auto_install': False
}
