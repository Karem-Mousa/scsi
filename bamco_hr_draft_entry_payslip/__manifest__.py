# -*- coding: utf-8 -*-
{
    'name': "Bamco Draft Entry Payslip",

    'summary': """
       """,

    'description': """
        * Payslip draft entry and journal from payslips.
    """,

    'author': "Centione",
    'website': "http://www.centione.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_payroll','account','bamco_access_groups_and_rules'],

    # always loaded
    'data': [
        'views/hr_payslip_run.xml',
        'views/hr_payslip.xml',
    ],
}