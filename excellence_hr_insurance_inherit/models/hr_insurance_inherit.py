from odoo import fields, models, api, _

import pytz
from dateutil import relativedelta


class HrInsurance(models.Model):
    _inherit = "hr.insurance"

    x_insurance_company = fields.Many2one('excel.insurance.companies.name')
    x_class = fields.Many2one('excel.insurance.companies.class')
    x_payment_code = fields.Char()
    x_ref_order = fields.Char()
    x_paid_amount = fields.Float()

    @api.onchange('x_insurance_company')
    def _get_insurance_policy_and_class(self):
        if self.x_insurance_company:
            insurance_companies = self.env['excel.insurance.companies'].sudo().search([
                ('company_id', '=', self.x_insurance_company.id)])
            return {'domain': {
                'x_class': [('id', 'in', insurance_companies.mapped('insurance_class.id'))],
                'policy_id': [('id', 'in', insurance_companies.mapped('policy_id.id'))]},
            }

    @api.onchange('x_class', 'policy_id')
    def _get_insurance_company_data(self):
        if self.x_class and self.policy_id:
            insurance_companies = self.env['excel.insurance.companies'].sudo().search([
                ('policy_id', '=', self.policy_id.id),
                ('insurance_class', '=', self.x_class.id)], limit=1)
            self.x_payment_code = insurance_companies.payment_code
            self.date_from = insurance_companies.date_from
            self.date_to = insurance_companies.date_to

