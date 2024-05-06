# -*- coding: utf-8 -*-
{
    'name': "bamco_resignation",
    'author': "Centione",
    'website': "",
    'depends': ['base', 'bamco_hr_employee_service'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_resignation.xml',
        'report/report.xml',
    ],

}