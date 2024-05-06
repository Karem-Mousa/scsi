# -*- coding: utf-8 -*-
{
    'name': "Bamco HR contract",

    'summary': """
            Centione's customized module for Odoo's hr_contract.
        """,

    'description': """
        * Preventing multiple running contracts for the same employee.
    """,

    'author': "Centione",
    'website': "http://www.centione.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'HR',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_contract', 'hr_work_entry_contract','bamco_hr_payroll_base', 'bamco_hr_employee_custom'],
    'data': [
        'views/hr_contract.xml',
        'data/contract_end_scheduled.xml',
        'data/salary_rules.xml',
    ],
}
