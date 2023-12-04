# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Kernel - Product Extension",
    'version': "13.0.0.1.1",
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "https://www.bistasolutions.com",
    'category': "Operations/Inventory",
    'summary': """Product Extension""",
    'description': """
        Kernel - Product Related Customization
    """,
    'depends': ['stock', 'account', 'stock_account'],
    'data': [
        'security/security.xml',
        'security/invoice_address_group.xml',
        'security/archive_button_group.xml',
        'security/product_template_group.xml',
        'security/ir.model.access.csv',
        'data/invoice_email_template.xml',
        'views/product_category_view.xml',
        'views/product_template_view.xml',
        'views/stock_inventory_view.xml',
        'views/supplier_view.xml',
        'views/stock_putaway_rule_view.xml',
        'views/product_product_view.xml',

        # Wizard view files
        'wizard/update_product_category_view.xml',

    ],
    'installable': True,
    'auto_install': False
}
