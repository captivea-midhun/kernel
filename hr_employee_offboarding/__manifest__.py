# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Employees Offboarding",
    'version': "13.0.0.1.1",
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "https://www.bistasolutions.com",
    'category': "Human Resources/Employees",
    'summary': """Employees Offboarding""",
    'description': """
        Employees Offboarding Form.
    """,
    'depends': ['hr'],
    'data': [
        'security/offboarding_security.xml',
        'security/ir.model.access.csv',
        'data/hr_offboarding_data.xml',
        'views/hr_offboarding_views.xml',
    ],
    'installable': True,
    'auto_install': False
}
