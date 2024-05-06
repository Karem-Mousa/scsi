# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'JOB Offer Applicant Employee',
    'version': '3.1.2',
    'price': 19.0,
    'category' : 'Human Resources/Recruitment',
    'license': 'Other proprietary',
    'currency': 'EUR',
    'summary': """This app allows your team to create a job offer for Application.""",
    'description': """
This app allows your team to create a job offer for Application.
Allow your team to create a job offer for new employees.
Recruitment officers create an offer letter using a job offer request.
Print Job Offer letter in PDF format.
Create a job offer directly from a job application.
For more details please check below screenshots and watch the video.
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/job_offer_applicant_employee/228',#'https://youtu.be/8TuwhaRh1uo',
    'images': [
        'static/description/img.jpg'
    ],
    'depends': [
        'hr_recruitment',
    ],
    'data':[
        'security/ir.model.access.csv',
        'data/job_offer_sequence.xml',
        'report/job_offer_custom.xml',
        'views/job_offer_custom_view.xml',
        'wizard/job_offer_request_wizard_view.xml',
        'views/hr_applicant_view.xml',
        'views/menu.xml',
    ],
    'qweb': [
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
