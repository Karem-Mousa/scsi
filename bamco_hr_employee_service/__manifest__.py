# -*- coding: utf-8 -*-
{
    'name': "Bamco Hr Employee service",

    'summary': """
    module to access loans time off and other self service models
        """,

    'description': """
    """,

    'author': "Centione | Ahmed Abo El Fadl",
    'website': "http://www.centione.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr','base','hr_holidays','bamco_hr_self_service','bamco_hr_loan_correct'],

    # always loaded
    'data': [
        'views/hr_employee_service.xml',
        # 'security/ir.model.access.csv',
    ],
}