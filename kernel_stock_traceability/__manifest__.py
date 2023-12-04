# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Kernel Stock Traceability",
    'summary': """ Contain Stock Traceability Report Modification """,
    'author': "Bista Solutions Inc.",
    'website': "http://www.bistasolutions.com",
    'category': 'Stock',
    'version': '13.0.0.1',
    'depends': ['mrp', 'kernel_kitting_mrp'],
    'data': [
        'views/template_assets.xml',
        'views/stock_traceability_report.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'installable': True,
    'auto_install': False
}
