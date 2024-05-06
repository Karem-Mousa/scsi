# -*- coding: utf-8 -*-
{
    'name': "Admin Request Report",

    'author': "Centione",
    'website': "http://www.centione.com",

    'depends': ['base', 'hr', 'bamco_hr_employee_service'],

    'data': [
        'security/ir.model.access.csv',
        'views/admin_req.xml',
        'reports/report.xml',
    ],
}
