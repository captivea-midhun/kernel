# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': 'Serial Import',
    'version': '13.0.0.1.1',
    'summary': 'Create Serial Number.',
    'description': """
This module extend functionality
============================================
Create Serial Number.
""",
    'category': 'mrp',
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "https://www.bistasolutions.com",
    'depends': ['mrp'],
    'data': [
        'wizard/serial_import_view.xml',
        'views/mrp_production_view.xml',

    ],
    'installable': True,
    'auto_install': True,
}
