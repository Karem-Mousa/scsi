# -*- coding: utf-8 -*-
# from odoo import http


# class TemsahSalaryRules(http.Controller):
#     @http.route('/temsah_salary_rules/temsah_salary_rules/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/temsah_salary_rules/temsah_salary_rules/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('temsah_salary_rules.listing', {
#             'root': '/temsah_salary_rules/temsah_salary_rules',
#             'objects': http.request.env['temsah_salary_rules.temsah_salary_rules'].search([]),
#         })

#     @http.route('/temsah_salary_rules/temsah_salary_rules/objects/<model("temsah_salary_rules.temsah_salary_rules"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('temsah_salary_rules.object', {
#             'object': obj
#         })
