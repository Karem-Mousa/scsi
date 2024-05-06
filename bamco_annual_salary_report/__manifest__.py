# -*- coding: utf-8 -*-
{
    'name': "Bamco Annual Salary Report",
    'author': "Centione | Toqa Hossam Eldien",
    'website': "http://www.centione.com/",
    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'bamco_hr_variable_allowance_deduction', 'hr_payroll', 'bamco_hr_variable_allowance_deduction'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/annual_wizard.xml',
    ],

}