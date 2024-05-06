# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': ' excellence hr employee inherit',
    'category': 'Human Resources',
    'summary': 'excellence hr employee inherit',
    'version': '1.0',
    'depends': ['hr','ent_hr_insurance'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/excel_insurance_companies.xml',
        'views/hr_employee_inherit.xml',
        'views/hr_insurance_inherit.xml',

    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
