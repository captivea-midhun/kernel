{
    'name': 'Cap BOM Consumable',
    'version': '2.0',
    'category': 'mrp',
    'sequence': 10,
    'summary': 'Proper processing of Manufacturing Orders with BOM component as consumable',
    'description': """
This module add journal entries to properly handle consumable components in a BOM
==================================================
Creates a Journal Entry from the Manufacturing Clearing Account to 504000
Creates a Journal Entry for the unbuild of a Manufacturing Order
       """,
    'website': 'https://www.captivea.com',
    'depends': ['stock', 'deltatech_mrp_edit_comp'],
    'data': [
        'views/res_config_settings_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
