# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Kernel - Sale Customization",
    'version': "13.0.0.1.1",
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "https://www.bistasolutions.com",
    'category': "Sale",
    'summary': """Sale Customization""",
    'description': """
        Kernel - Sale Related Customization.
    """,
    'depends': ['sale', 'product_extension'],
    'data': [
        'security/sale_security.xml',
        'views/sale_view.xml',
        'views/account_move_view.xml',
        'views/account_move_line_view.xml',
        'reports/sale_report_template.xml',
        'reports/invoice_report_template.xml',
        'reports/invoice_without_payment_report_template.xml',
        'reports/sale_report.xml',
        'reports/account_report.xml',
    ],
    'installable': True,
    'auto_install': False
}
