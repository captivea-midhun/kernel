# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Kernel - Asset Equipment",
    'version': "13.0.0.1.1",
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "http://www.bistasolutions.com",
    'category': "Maintenance",
    'summary': """Menage Asset Equipment""",
    'description': """
        Kernel - Asset Equipment Customization,
        Add equipment inside asset.
    """,
    'depends': ['account_asset', 'maintenance', 'hr_maintenance', 'purchase',
                'mrp_maintenance', 'stock'],
    'data': [
        'security/maintenance_equipment_security.xml',
        'security/ir.model.access.csv',
        'data/update_EEOL_field.xml',
        'data/equipment_categories_data.xml',
        'views/assets.xml',
        'wizard/wizard_reassign_equipment_view.xml',
        'views/maintenance_equipment_views.xml',
        'views/account_asset_views.xml',
        'views/maintenance_request_view.xml',
        'views/menu_access_view.xml',
    ],
    'installable': True
}
