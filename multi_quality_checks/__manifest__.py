# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Kernel - Multi Quality Checks",
    'version': "13.0.0.1.1",
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "https://www.bistasolutions.com",
    'category': "Manufacturing/Quality",
    'summary': """Multi Quality Checks""",
    'description': """
    """,
    'depends': ['purchase_stock', 'quality_control',
                'qc_by_serial_number', 'product_tracking_extension'],
    'data': [
        'wizard/wizard_multi_quality_checks_views.xml',
        'views/stock_picking_view.xml',
    ],
    'installable': True,
    'auto_install': False
}
