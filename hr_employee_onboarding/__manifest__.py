# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Employees Onboarding",
    'version': "13.0.0.1.1",
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "https://www.bistasolutions.com",
    'category': "Human Resources/Employees",
    'summary': """Employees Onboarding""",
    'description': """
        Employees Onboarding Form.
    """,
    'depends': ['hr'],
    'data': [
        'security/onboarding_security.xml',
        'security/ir.model.access.csv',
        'data/hr_onboarding_data.xml',
        'views/hr_onboarding_views.xml',
    ],
    'installable': True,
    'auto_install': False
}
