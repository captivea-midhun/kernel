# -*- coding: utf-8 -*-
# Copyright (c) 2017 Emipro Technologies Pvt Ltd (www.emiprotechnologies.com). All rights reserved.
{

    # App information
    'name': 'Master Production Schedule Extended',
    'category': 'Manufacturing/Manufacturing',
    'version': '8.0',
    'summary': 'Master Production Schedule',
    'license': 'OPL-1',

    # Author
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
    # Dependencies
    'depends': ['mrp_mps','product_template_tags','purchase_rfo'],

    # Views
    'data': ['security/ir.model.access.csv',
             'data/emoji_data.xml',
             'data/ir_cron.xml',
             'data/res_config_settings.xml',
             'views/mrp_mps_views.xml',
             'views/stock_warehouse_views.xml',
             'views/stock_location_view.xml',
             'views/product.xml',
             'views/hr_department.xml',
             'views/mrp_mps_templates.xml',
             'views/emoji_logo.xml'
             ],
    'qweb': [
        "static/src/xml/setu_qweb_templates.xml",
    ],

    'demo': [],

    'installable': True,
    'application': True,
    'auto_install': False,
}
