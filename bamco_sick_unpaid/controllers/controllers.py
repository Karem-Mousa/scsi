# -*- coding: utf-8 -*-
from odoo import http

# class RedconSalaryRules(http.Controller):
#     @http.route('/redcon_salary_rules/redcon_salary_rules/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/redcon_salary_rules/redcon_salary_rules/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('redcon_salary_rules.listing', {
#             'root': '/redcon_salary_rules/redcon_salary_rules',
#             'objects': http.request.env['redcon_salary_rules.redcon_salary_rules'].search([]),
#         })

#     @http.route('/redcon_salary_rules/redcon_salary_rules/objects/<model("redcon_salary_rules.redcon_salary_rules"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('redcon_salary_rules.object', {
#             'object': obj
#         })