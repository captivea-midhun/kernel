# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': 'Import Quality Control On Receipt',
    'version': '13.0.0.1.1',
    'summary': 'Import Quality Control with Product details on Receipt',
    'description': """
Import Quality Check
============================================
This module import quality control and
proceed Quality Check accordingly on receipt.
""",
    'category': 'Inventory',
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "https://www.bistasolutions.com",
    'depends': ['quality_control', 'purchase_stock',
                'qc_by_serial_number', 'product_tracking_extension'],
    'data': [
        'wizard/wizard_import_quality_check_view.xml',
        'views/quality_check_view.xml',
    ],
    'installable': True,
    'external_dependencies': {'python': ['xlrd']},
}
