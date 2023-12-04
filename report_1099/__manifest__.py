# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    "name": "Report 1099",
    "summary": "Report 1099",
    "version": "13.0.0.1.1",
    "description": """
Report 1099
============================================
This module help to print Report 1099.
    """,
    "category": "Reporting",
    "website": "https://www.bistasolutions.com",
    "author": "Bista Solutions Pvt. Ltd.",
    "depends": ['purchase', 'account'
                ],
    "data": [
        'security/report_1099_security.xml',
        'security/ir.model.access.csv',
        'views/account_invoice_view.xml',
        'views/res_partner_view.xml',
        'views/report_1099_view.xml',
        'wizard/wiz_report_1099_view.xml',
        'views/account_payment_view.xml',
        'report/report_1099_reg.xml',
        'report/report_1099_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,

}
