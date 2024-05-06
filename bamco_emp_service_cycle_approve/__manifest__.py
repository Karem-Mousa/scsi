# -*- coding: utf-8 -*-
{
    'name': "Employee Service Cycle Approve",

    'author': "Centione",
    'website': "http://www.centione.com",

    'depends': [
        'base',
        'mail',
        'bamco_admin_req_report',
        'bamco_financial_identification_request',
        'bamco_resignation',
    ],

    'data': [
        'security/groups.xml',
        'views/admin_req.xml',
        'views/fin_id_req.xml',
        'views/hr_resignation.xml',
    ],
}
