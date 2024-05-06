# -*- coding: utf-8 -*-

{
    'name': 'Project by Phases',
    'version': '15',
    'category': 'Projects',
    'license': 'OPL-1',
    'summary': 'This apps helps to manage Project and Task Phases',
    'description': """
        Project Phases.
""",
    'author': 'Karim-Mousa',
    'depends': ['project'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
