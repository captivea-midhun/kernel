# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

{
    'name': 'HR Employee Form',
    'version': '13.0.0.1.1',
    'summary': 'New Hr Employee Form Creation',
    'description': """
HR Employee Form
============================================
This module create and customization of new hr employee view
with tree,kanban,form view mode.
    """,
    'category': 'Human Resources/Employees',
    'author': "Bista Solutions Pvt. Ltd.",
    'website': "https://www.bistasolutions.com",
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_view.xml',
    ],
    'installable': True,
}
