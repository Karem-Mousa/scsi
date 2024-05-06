# -*- coding: utf-8 -*-
{
    'name': "Employee Appraisals",

    'summary': """
    module for appraisial and examinning employee preforamnce
 """,

    'author': "Centione",
    'website': "www.centione.com",

    # any module necessary for this one to work correctly
    'depends': ['base','hr_appraisal','hr','hr_contract'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'data/scheduale_action.xml',
        'views/kpi_appraisal.xml',
        'views/hr_appraisal.xml',
        'views/hr_employee.xml',
        'views/appraisal_data.xml',
        'views/hr_contract.xml',
        'report/monthly_evaluation.xml',
        'report/yearly_evaluation.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}