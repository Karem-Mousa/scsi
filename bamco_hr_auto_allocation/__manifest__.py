# -*- coding: utf-8 -*-
{
    'name': "Bamco HR Leave Allocation",

    'summary': """
            Centione's customized module for Odoo's leave allocation automated.
        """,

    'description': """
        
    """,

    'author': "Centione",
    'website': "http://www.centione.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'HR',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr','hr_holidays','bamco_hr_employee_custom'],
    'data': [
        'security/ir.model.access.csv',
        'data/server_action.xml',
        'views/transfer_allocation.xml',
        'views/hr_employee.xml',
        'views/hr_leave_type.xml',
        'views/hr_leave.xml',
    ],
}
