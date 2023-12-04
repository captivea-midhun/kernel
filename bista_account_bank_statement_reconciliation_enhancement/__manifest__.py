# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Online Bank Statement Synchronization Enhancements",
    'category': 'Accounting/Accounting',
    'summary': "Resolve bank statement reconciliation issue cause by online synchronization",
    'description': """
Account Bank Statement,
===================================================================
    *This module is used to run scheduler to check the online synchronized bank statement errors where sometimes odoo does not populate company or journal on bank statement lines
    Scheduler checks all the statements which are generated automatically using synchronization and checks whether company or journal are set or not, If not then this module sets it according to bank statement data. 
    """,
    'version': '13.0.1.0.0',
    'author': 'Bista Solutions Pvt. Ltd.',
    'website': 'https://www.bistasolutions.com',
    'company': 'Bista Solutions Inc',
    'maintainer': 'Bista Solutions Inc',
    'depends': ['account'],
    'data': [
        'data/account_bank_statement_cron.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
