# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Kernel - Purchase RFO",
    'version': "13.0.0.1.7",
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "https://www.bistasolutions.com",
    'category': "Operations/Purchase",
    'summary': """Purchase RFO""",
    'description': """
        This module extend the following functionality,

        1> Added Purchase RFO Approval.\n
        2> Added Project and Project Manager fields on RFO and vendor bills.\n
        3> Added analytic account field on RFO.\n
        4> Make RFO and Purchase order separate sequence.\n
        5> Predefined terms & condition for purchase orders.\n
        6> Purchase order report customization\n
        7> Added new object - purchase payments, it will be used in purchase order.\n
        8> Added new field tracking number in purchase order.\n
    """,
    'depends': ['purchase_stock', 'hr', 'product_extension', 'account'],
    'data': [
        'security/purchase_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/cron_approve_purchase_order.xml',
        'data/account_data.xml',
        'data/courier_data.xml',
        'data/purchase_order_email_template.xml',
        'reports/purchase_reports.xml',
        'reports/purchase_order_templates.xml',
        'wizard/wizard_purchase_tracking_number_view.xml',
        'wizard/purchase_custom_report_view.xml',
        'wizard/purchase_custom_report.xml',
        'wizard/mail_wizard_invite.xml',
        'views/hr_department_view.xml',
        'views/res_config_setting_view.xml',
        'views/account_move.xml',
        'views/purchase_view.xml',
        'views/res_partner_view.xml',
        'views/res_users_view.xml',
        'views/stock_move_views.xml',
        'views/purchase_delivery_courier_view.xml',
        'views/stock_quant_view.xml',
        'views/account_move_line.xml',
        'views/purpose_type_views.xml',
        'views/stock_location_view.xml',
        'views/stock_view.xml',
        'views/stock_picking_view.xml',
    ],
    'installable': True,
    'auto_install': False
}
