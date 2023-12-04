# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': 'Deferred Expenses Report',
    'version': '1.1',
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "https://www.bistasolutions.com",
    'summary': 'Deferred Expenses Report',
    'description': """
    Deferred Expenses Report Contain following details.../n
    1)Date \n
    2)Name \n
    3)Original value \n
    4)Expense Account \n
    5)Amount. Period \n
    6)Beg. Accum Amount\n
    7)Period Amount \n
    8)Ending Accum. Amount.\n
    9)Remaining Balance (2)\n
    """,
    'category': 'Accounting',
    'website': 'https://www.bistasolutions.com/',
    'depends': ['base', 'account_reports', 'account_asset'],
    'data': [
        'view/deferred_expenses_wizard_view.xml',
        'report/deferred_expenses_rpt_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
