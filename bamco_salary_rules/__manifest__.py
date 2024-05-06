# -*- coding: utf-8 -*-
{
    'name': "Bamco Salary Rules",

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'bamco_hr_payroll_base','hr_payroll'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/salary_rules.xml',
        'views/hr_salary_rule_inherit.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
