from odoo import fields, models, api


class ExcelInsuranceCompanies(models.Model):
    _name = 'excel.insurance.companies'
    _rec_name = "company_id"
    _description = 'Description'

    name = fields.Char()
    company_id = fields.Many2one('excel.insurance.companies.name', required=True,)
    policy_id = fields.Many2one('insurance.policy', string='Policy', required=True, help="Policy")
    insurance_class = fields.Many2one('excel.insurance.companies.class')
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    payment_code = fields.Char(required=True)


class ExcelInsuranceCompaniesName(models.Model):
    _name = 'excel.insurance.companies.name'
    _description = 'Description'

    name = fields.Char(required=True)


class ExcelInsuranceCompaniesClass(models.Model):
    _name = 'excel.insurance.companies.class'
    _description = 'Description'
    _rec_name = "name"

    name = fields.Char(required=True)



