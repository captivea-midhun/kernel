# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': 'Quality Check By Serial Number',
    'version': '13.0.0.1.1',
    'summary': 'Create Quality Check By Serial Number.',
    'description': """
This module extend functionality
============================================
Create Quality Check By Number of products on Receipt.
""",
    'category': 'Quality',
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "https://www.bistasolutions.com",
    'depends': ['purchase', 'quality_control'],
    'data': [
        'views/quality_check_view.xml',
    ],
    'installable': True,
    'auto_install': True,
}
