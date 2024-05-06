# -*- coding: utf-8 -*-
{
    'name': "Bamco HR Reports",

    'summary': """
        module reports for HR modules and functions
        """,

    # 'description': """
    #     * Preventing multiple running contracts for the same employee.
    # """,

    'author': "Centione | Ahmed Abo El Fadl",
    'website': "http://www.centione.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'HR',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_holidays', 'hr_payroll','hr_contract', 'bamco_hr_employee_custom'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/hr_contract_employees.xml',
        'views/hr_leave.xml',
        'views/hr_contract.xml',
        'views/hr_employee.xml',
        'report/leave_report.xml',
        'report/bank_report.xml',

    ],
}
