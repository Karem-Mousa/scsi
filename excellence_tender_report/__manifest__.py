# -*- coding: utf-8 -*-
{
    'name': "EX Tender Report",

    'developer': 'Omar Talaat',

    'depends': ['base', 'excellences_tenders_minutes'],

    # always loaded
    'data': [
        # -*- Security -*-
        'security/ir.model.access.csv',

        # -*- Views -*-
        'views/ex_tender_report.xml',
        'views/ex_tenders.xml',
        # 'views/res_company.xml',

        # -*- Reports -*-
        'reports/ex_report.xml',
    ],
}
