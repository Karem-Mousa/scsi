# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Excellence project Customization',
    'category': 'Services/Project',
    'summary': 'Excellence project Customization',
    'version': '1.0',
    'depends': ['project','hr'],
    'data': [
        'security/groups.xml',
        'views/project_project_view_inherit.xml',
        'views/project_task_inherit.xml',
        'data/mail_templates.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'excellences_project_inherit/static/src/js/kanban_button.js',
        ],
        'web.assets_qweb': [
            'excellences_project_inherit/static/src/xml/kanban_button.xml',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
