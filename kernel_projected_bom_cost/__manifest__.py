# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Kernel Projected BOM Cost",
    'version': "13.0.0.1.3",
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "https://www.bistasolutions.com",
    'category': "Product",
    'summary': """BOM Customization""",
    'description': """
        Kernel - BOM Related Customization.
    """,
    'depends': ['product', 'mrp', 'mrp_subcontracting'],
    'data': [
        'views/product_view.xml',
        'views/mrp_bom_view.xml',
        'views/mrp_templates.xml',
        'report/mrp_report_view_main.xml',
        'report/mrp_report_projected_bom_structure.xml',
    ],
    'installable': True,
    'auto_install': False
}
