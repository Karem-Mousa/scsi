{
    'name': 'Job Offer Letter',
    'version': "1.0.0",
    "author": "Odoo Bangladesh",
    "website": "http://odoobangladesh.com",
    'category': 'Human Resources',
    'depends': ['hr_recruitment', 'excellences_project_inherit'],
    'data': [
        'data/mail_data.xml',
        'views/he_application_view.xml',
        'reports/job_offer_report.xml',
    ],
    'installable': True,
    'application': False,
}
