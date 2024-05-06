# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Excellence Tenders Minutes',
    'category': 'Customizations',
    'summary': 'Excellence Tenders Minutes',
    'version': '1.0',
    'depends': ['purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/tenders_minutes.xml',
        'views/purchase_order_inherit.xml',

    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
