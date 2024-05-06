# -*- coding: utf-8 -*-
{
    'name': "Allowances and Deductions",

    'summary': """
        Allowances And Deduction Added to the Contracts""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Centione",
    'website': "http://www.centione.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'HR',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_contract', 'hr_payroll'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        # 'data/salary_rules.xml'
    ],
}