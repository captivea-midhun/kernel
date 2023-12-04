# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': 'Kernal Kitting MRP',
    'category': 'mrp',
    'author': 'Bista Solutions Pvt. Ltd.',
    'summary': 'Added Slot in BOM and MO. Restrict component Qty to 1 or less \
    than 1. Added New Button in done state to unbuild current Mo and create \
    New Duplicate Darft MO.',
    'version': '13.0.1.0.0',
    'description': """
    Module to customize Manufacturing Process
    """,
    'depends': ['base', 'mrp', 'deltatech_mrp_edit_comp'],
    'data': [
        'views/bom_view.xml',
        'wizard/mrp_component_change_view.xml',
        'wizard/mrp_production_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
