# -*- coding: utf-8 -*-
{
    'name': "Bamco Employee Customize",

    'author': "Centione",
    'website': "http://www.centione.com",

    'depends': ['base', 'hr','hr_contract','account'],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/hr_contract_inherit.xml',
        'views/hr_branch.xml',
        'views/hr_area.xml',
        'views/bank.xml',
    ],
}
