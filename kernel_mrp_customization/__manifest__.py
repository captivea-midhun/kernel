# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Kernel - MRP Customization",
    'version': "13.0.0.2.0",
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "http://www.bistasolutions.com",
    'category': "Manufacturing",
    'summary': """Kernel - MRP Customization""",
    'description': """
        Kernel - MRP Related Customization,
    """,
    'depends': ['mrp_workorder', 'mrp_subcontracting', 'quality_control', 'product_extension',
                'product_qty_detail'],
    'data': [
        'report/mrp_production_order.xml',
        'views/mrp_workorder_view.xml',
        'views/mrp_production_views.xml',
        'views/quality_views.xml',
        'views/mrp_menu_navigation_view.xml',
        'views/mrp_unbuild_views.xml',
        'views/stock_picking.xml',
        'views/stock_move_lots_view.xml',
    ],
    'installable': True
}
