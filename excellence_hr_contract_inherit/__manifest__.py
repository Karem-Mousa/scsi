# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': ' excellence hr contract inherit',
    'category': 'Human Resources',
    'summary': 'excellence hr contract inherit',
    'version': '1.0',
    'depends': ['l10n_sa_hr_payroll','bamco_hr_contract','hr_contract','bamco_hr_reports','bamco_hr_employee_custom'],
    'data': [
        'views/hr_contract_inherit.xml',

    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
