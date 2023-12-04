# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Kernel - MRP Test Result",
    'version': "13.0.0.1.1",
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "http://www.bistasolutions.com",
    'category': "Manufacturing",
    'summary': """MRP Test Result""",
    'description': """
        MRP Test Result
    """,
    'depends': ['mrp'],
    'data': [
        'security/mrp_test_result_security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'data/mrp_test_result_config_data.xml',
        'views/table_header_views.xml',
        'views/mrp_test_result_error_view.xml',
        'views/mrp_test_result_config.xml',
        'views/mrp_test_result_scheduler.xml',
    ],
    'installable': True
}
