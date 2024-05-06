# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'STEM Employees Request',
    'category': 'Human Resources',
    'summary': 'Employee Request',
    'version': '1.0',
    'depends': ['base', 'contacts', 'hr'],
    'data': [
        'views/employee_request_views.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',

    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
