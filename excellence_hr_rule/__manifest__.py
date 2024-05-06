# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': ' excellence hr rule inherit',
    'category': 'Human Resources',
    'summary': 'excellence hr rule inherit',
    'version': '1.0',
    'depends': ['hr_payroll'],
    'data': [
        'views/hr_payslip_line_inherit.xml',
        'views/hr_salary_rule_inherit.xml',

    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
