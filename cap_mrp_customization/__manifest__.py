{
    'name': 'Cap MRP Customization',
    'version': '5.7',
    'category': 'mrp',
    'sequence': 10,
    'summary': 'Automation of Transfers on Manufacturing Order',
    'description': """
This module automates the Transfer quantities for 2-step Manufacturing.
==================================================
Transfer button to create manual transfer.
Automatically updates quantities of Transfers when Manufacturing Order quantities change.
       """,
    'website': 'https://www.captivea.com',
    'depends': ['stock', 'deltatech_mrp_edit_comp', 'purchase_by_line_routes'],
    'data': [
        'views/mrp_production_view.xml',
        'views/product_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
