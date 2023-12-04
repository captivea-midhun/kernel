# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Kernel - CRM Customization",
    'version': "13.0.0.1.1",
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "https://www.bistasolutions.com",
    'category': "Sale",
    'summary': """CRM Customization""",
    'description': """
        Kernel - CRM Related Customization.
    """,
    'depends': ['crm'],
    'data': [
        'security/crm_security.xml',
        'views/crm_view.xml',
    ],
    'installable': True,
    'auto_install': False
}
