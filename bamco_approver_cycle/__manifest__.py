# -*- coding: utf-8 -*-
{
    'name': "Bamco Approver Cycle",

    'summary': """
    module for approver cycle on time off mission and excuse 
       """,

    'description': """
    """,

    'author': "Centione",
    'website': "http://www.centione.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_holidays', 'mail', 'bamco_hr_self_service', 'bamco_hr_loan_correct',
                'bamco_hr_reports', 'bamco_emp_service_cycle_approve', 'bamco_hr_employee_custom','bamco_admin_req_report','bamco_emp_service_cycle_approve',
                'bamco_financial_identification_request'],

    # always loaded
    'data': [
        'views/hr_loan.xml',
        'views/hr_leave.xml',
    ],
}
