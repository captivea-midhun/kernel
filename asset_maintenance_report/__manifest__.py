# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Kernel - Asset Maintenance Report",
    'version': "13.0.0.1.1",
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "http://www.bistasolutions.com",
    'category': "Maintenance",
    'summary': """Asset Maintenance Report""",
    'description': """
        Asset Maintenance Report
    """,
    'depends': ['asset_equipment', 'account'],
    'data': [
        'wizard/wizard_asset_maintenance_report_view.xml',
        'wizard/wizard_maintenance_equipment_report_view.xml',
        'report/accounting_asset_template.xml',
        'report/maintenance_equip_template.xml',
        'report/accounting_asset_both_template.xml',
        'report/reports.xml',
    ],
    'installable': True,
    'auto_install': True,
}
