# -*- coding: utf-8 -*-
{
    'name': "Bamco Work Entry Hide",

    'summary': """
    cancel the work entry
    """,
    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_payroll','hr_work_entry_contract_enterprise'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/groups.xml',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
