# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': 'COA Kernel',
    'version': '13.0.0.1.1',
    'sequence': 7,
    'category': 'Localization',
    'summary': "COA of Kernel",
    'description': """
Kernel Accounting
======================================================================================
    * This module is provide configure COA for Kernel company.
    """,
    'website': 'https://www.bistasolutions.com',
    'author': 'Bista Solutions Pvt. Ltd.',
    'depends': ['account'],
    'data': [
        'data/account_chart_data.xml',
        'data/account.account.template.csv',
        'data/l10n_kernel_chart_data.xml',
        'data/account_chart_template_data.xml',
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}
